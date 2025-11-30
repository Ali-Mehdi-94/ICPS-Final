"""
Django signals for automatic registration processing and notifications.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Registration, UnitTask, PaymentInstallment
from .services import apply_template_defaults, create_units_for_registration, build_payment_schedule

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Registration)
def registration_post_save(sender, instance: Registration, created, **kwargs):
    """
    When a Registration is created or edited:
    - ensure defaults from template,
    - (re)build unit tasks (for ProQual, only if portal_allotment_date is set),
    - (re)build payment schedule (if total fee known).
    This is idempotent: safe on repeated saves.
    """
    # Prevent infinite recursion by checking if this is from apply_template_defaults
    if kwargs.get('update_fields') == ['unit_count', 'deadline_date']:
        # This save was triggered by apply_template_defaults, skip to avoid recursion
        return
    
    # 1) template defaults (unit_count/deadline)
    apply_template_defaults(instance)

    # 2) units timeline
    # For ProQual: only create tasks if portal_allotment_date is set
    # For others: create tasks immediately
    if instance.is_proqual:
        if instance.portal_allotment_date:
            create_units_for_registration(instance)
    else:
        create_units_for_registration(instance)

    # 3) payments: read total_fee from registration
    total_fee = getattr(instance, "total_fee", None)
    if total_fee:
        build_payment_schedule(instance, float(total_fee))


@receiver(post_save, sender=UnitTask)
def unit_task_post_save(sender, instance: UnitTask, created, **kwargs):
    """
    When a UnitTask is created or updated:
    - Send notifications if the task is due or due soon.
    """
    # Only send notifications for new tasks or when due date changes
    update_fields = kwargs.get('update_fields') or []
    if not created and 'due_date' not in update_fields:
        return
    
    # Skip if task is already completed
    if instance.status == "DONE":
        return
    
    registration = instance.registration
    today = timezone.localdate()
    days_until_due = (instance.due_date - today).days
    
    # Send notification if due within 7 days, due today, or overdue
    if days_until_due <= 7:
        try:
            if registration.is_proqual:
                from .notifications import notify_proqual_unit_due
                notify_proqual_unit_due(instance)
            else:
                from .notifications import notify_ops_unit_due
                notify_ops_unit_due(instance)
        except Exception as e:
            logger.error(f"Failed to send unit due notification for task {instance.id}: {str(e)}", exc_info=True)


@receiver(post_save, sender=PaymentInstallment)
def payment_installment_post_save(sender, instance: PaymentInstallment, created, **kwargs):
    """
    When a PaymentInstallment is created or updated:
    - Send notifications if the payment is due or due soon.
    """
    # Skip if already paid
    if instance.paid_at:
        return
    
    # Only send notifications for new installments or when due date changes
    update_fields = kwargs.get('update_fields') or []
    if not created and 'due_date' not in update_fields:
        return
    
    today = timezone.localdate()
    days_until_due = (instance.due_date - today).days
    
    # Send notification if due within 7 days, due today, or overdue
    if days_until_due <= 7:
        try:
            from .notifications import notify_payment_due
            notify_payment_due(instance)
        except Exception as e:
            logger.error(f"Failed to send payment due notification for installment {instance.id}: {str(e)}", exc_info=True)

