"""
Comprehensive email notification system for ICPS.
Handles notifications for ProQual and other course providers.
"""
import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from .models import UnitTask, PaymentInstallment, Registration, CustomUser, CourseProvider

logger = logging.getLogger(__name__)


def _get_email_from():
    """Get the from email address from settings"""
    return getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@icps.com')


def _send_email(subject, message, recipient_list, html_message=None):
    """
    Helper function to send email with error handling.
    """
    if not recipient_list:
        logger.warning(f"Attempted to send email '{subject}' with no recipients")
        return False
    
    # Filter out None and empty emails
    valid_recipients = [email for email in recipient_list if email]
    if not valid_recipients:
        logger.warning(f"Attempted to send email '{subject}' with no valid recipients")
        return False
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=_get_email_from(),
            recipient_list=valid_recipients,
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email sent successfully: '{subject}' to {valid_recipients}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email '{subject}' to {valid_recipients}: {str(e)}", exc_info=True)
        return False


# ============================================================================
# PROQUAL NOTIFICATIONS
# ============================================================================

def notify_proqual_ops_assigned(registration: Registration):
    """
    ProQual: Notify Ops team member when a student is assigned to them.
    """
    if not registration.is_proqual:
        return
    
    if not registration.assigned_to or not registration.assigned_to.email:
        logger.warning(f"Cannot notify Ops assignment for registration {registration.id}: no assigned_to or email")
        return
    
    student = registration.student
    ops_user = registration.assigned_to
    
    subject = f"[ICPS ProQual] New Student Assigned: {student.name}"
    
    message = f"""
Hello {ops_user.username},

A new ProQual student has been assigned to you:

Student Details:
- Name: {student.name}
- Registration ID: {registration.id}
- Course: {registration.provider.name} - {registration.field.name} ({registration.level})
- Qualification Type: {registration.get_qualification_type_display() or 'N/A'}

Please review the student's registration and prepare for their portal activation.

Best regards,
ICPS System
"""
    
    html_message = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50;">New ProQual Student Assigned</h2>
        <p>Hello {ops_user.username},</p>
        <p>A new ProQual student has been assigned to you:</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #2c3e50;">Student Details</h3>
            <p><strong>Name:</strong> {student.name}</p>
            <p><strong>Registration ID:</strong> {registration.id}</p>
            <p><strong>Course:</strong> {registration.provider.name} - {registration.field.name} ({registration.level})</p>
            <p><strong>Qualification Type:</strong> {registration.get_qualification_type_display() or 'N/A'}</p>
        </div>
        
        <p>Please review the student's registration and prepare for their portal activation.</p>
        
        <p style="margin-top: 30px; color: #7f8c8d;">Best regards,<br>ICPS System</p>
    </div>
</body>
</html>
"""
    
    _send_email(subject, message, [ops_user.email], html_message)


def notify_proqual_portal_allotted(registration: Registration):
    """
    ProQual: Notify when portal is allotted (to Ops team and ProQual Admin).
    """
    if not registration.is_proqual:
        return
    
    if not registration.portal_allotment_date:
        return
    
    student = registration.student
    recipients = []
    
    # Add Ops team member if assigned
    if registration.assigned_to and registration.assigned_to.email:
        recipients.append(registration.assigned_to.email)
    
    # Add all ProQual Admin users
    proqual_admins = CustomUser.objects.filter(role="ProQualAdmin", is_active=True)
    for admin in proqual_admins:
        if admin.email:
            recipients.append(admin.email)
    
    if not recipients:
        logger.warning(f"Cannot notify portal allotment for registration {registration.id}: no recipients")
        return
    
    subject = f"[ICPS ProQual] Portal Allotted: {student.name}"
    
    message = f"""
Portal Allotment Notification

The portal has been allotted for the following ProQual student:

Student: {student.name}
Registration ID: {registration.id}
Portal Allotment Date: {registration.portal_allotment_date}
Course: {registration.provider.name} - {registration.field.name} (Level {registration.level.name})

The 32-week timeline has now started from the portal allotment date.

Best regards,
ICPS System
"""
    
    html_message = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #27ae60;">Portal Allotted</h2>
        <p>The portal has been allotted for the following ProQual student:</p>
        
        <div style="background-color: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #27ae60;">
            <p><strong>Student:</strong> {student.name}</p>
            <p><strong>Registration ID:</strong> {registration.id}</p>
            <p><strong>Portal Allotment Date:</strong> {registration.portal_allotment_date}</p>
            <p><strong>Course:</strong> {registration.provider.name} - {registration.field.name} ({registration.level})</p>
        </div>
        
        <p style="color: #27ae60; font-weight: bold;">The 32-week timeline has now started from the portal allotment date.</p>
        
        <p style="margin-top: 30px; color: #7f8c8d;">Best regards,<br>ICPS System</p>
    </div>
</body>
</html>
"""
    
    _send_email(subject, message, recipients, html_message)


def notify_proqual_unit_due(task: UnitTask):
    """
    ProQual: Notify Ops team and ProQual Admin when a unit is due.
    """
    registration = task.registration
    if not registration.is_proqual:
        return
    
    if task.status == "DONE":
        return  # Don't notify for completed tasks
    
    student = registration.student
    recipients = []
    
    # Add Ops team member if assigned
    if registration.assigned_to and registration.assigned_to.email:
        recipients.append(registration.assigned_to.email)
    
    # Add all ProQual Admin users
    proqual_admins = CustomUser.objects.filter(role="ProQualAdmin", is_active=True)
    for admin in proqual_admins:
        if admin.email:
            recipients.append(admin.email)
    
    if not recipients:
        return
    
    days_until_due = (task.due_date - timezone.localdate()).days
    status_text = "OVERDUE" if days_until_due < 0 else f"Due in {days_until_due} day(s)"
    
    # Calculate colors for HTML
    color_primary = '#e74c3c' if days_until_due < 0 else '#f39c12'
    color_bg = '#ffebee' if days_until_due < 0 else '#fff3e0'
    
    subject = f"[ICPS ProQual] Unit Due: {task.label} - {student.name}"
    
    message = f"""
Unit Due Notification

A ProQual unit is due for the following student:

Student: {student.name}
Registration ID: {registration.id}
Unit: {task.label}
Phase: {task.phase}
Due Date: {task.due_date}
Status: {status_text}

Please ensure the unit is completed on time.

Best regards,
ICPS System
"""
    
    html_message = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: {color_primary};">Unit Due: {task.label}</h2>
        <p>A ProQual unit is due for the following student:</p>
        
        <div style="background-color: {color_bg}; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid {color_primary};">
            <p><strong>Student:</strong> {student.name}</p>
            <p><strong>Registration ID:</strong> {registration.id}</p>
            <p><strong>Unit:</strong> {task.label}</p>
            <p><strong>Phase:</strong> {task.phase}</p>
            <p><strong>Due Date:</strong> {task.due_date}</p>
            <p><strong style="color: {color_primary};">{status_text}</strong></p>
        </div>
        
        <p>Please ensure the unit is completed on time.</p>
        
        <p style="margin-top: 30px; color: #7f8c8d;">Best regards,<br>ICPS System</p>
    </div>
</body>
</html>
"""
    
    _send_email(subject, message, recipients, html_message)


def notify_proqual_unit_completed(task: UnitTask):
    """
    ProQual: Notify ProQual Admin when a unit is completed.
    """
    registration = task.registration
    if not registration.is_proqual:
        return
    
    if task.status != "DONE":
        return
    
    student = registration.student
    
    # Get all ProQual Admin users
    proqual_admins = CustomUser.objects.filter(role="ProQualAdmin", is_active=True)
    recipients = [admin.email for admin in proqual_admins if admin.email]
    
    if not recipients:
        return
    
    subject = f"[ICPS ProQual] Unit Completed: {task.label} - {student.name}"
    
    message = f"""
Unit Completion Notification

A ProQual unit has been completed:

Student: {student.name}
Registration ID: {registration.id}
Unit: {task.label}
Phase: {task.phase}
Completed At: {task.completed_at.strftime('%Y-%m-%d %H:%M:%S') if task.completed_at else 'N/A'}
Completed By: {task.assigned_to.username if task.assigned_to else 'N/A'}

Best regards,
ICPS System
"""
    
    html_message = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #27ae60;">Unit Completed</h2>
        <p>A ProQual unit has been completed:</p>
        
        <div style="background-color: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #27ae60;">
            <p><strong>Student:</strong> {student.name}</p>
            <p><strong>Registration ID:</strong> {registration.id}</p>
            <p><strong>Unit:</strong> {task.label}</p>
            <p><strong>Phase:</strong> {task.phase}</p>
            <p><strong>Completed At:</strong> {task.completed_at.strftime('%Y-%m-%d %H:%M:%S') if task.completed_at else 'N/A'}</p>
            <p><strong>Completed By:</strong> {task.assigned_to.username if task.assigned_to else 'N/A'}</p>
        </div>
        
        <p style="margin-top: 30px; color: #7f8c8d;">Best regards,<br>ICPS System</p>
    </div>
</body>
</html>
"""
    
    _send_email(subject, message, recipients, html_message)


# ============================================================================
# OTHER PROVIDERS NOTIFICATIONS
# ============================================================================

def notify_ceo_unit_completed(task: UnitTask):
    """
    Other Providers: Notify CEO when a unit is completed.
    """
    registration = task.registration
    if registration.is_proqual:
        return  # ProQual has its own notification system
    
    if task.status != "DONE":
        return
    
    # Get all CEO users
    ceo_users = CustomUser.objects.filter(role="CEO", is_active=True)
    recipients = [ceo.email for ceo in ceo_users if ceo.email]
    
    if not recipients:
        return
    
    student = registration.student
    
    subject = f"[ICPS] Unit Completed: {task.label} - {student.name}"
    
    message = f"""
Unit Completion Notification

A unit has been completed:

Student: {student.name}
Registration ID: {registration.id}
Provider: {registration.provider.name}
Course: {registration.field.name} (Level {registration.level.name})
Unit: {task.label}
Phase: {task.phase}
Completed At: {task.completed_at.strftime('%Y-%m-%d %H:%M:%S') if task.completed_at else 'N/A'}
Completed By: {task.assigned_to.username if task.assigned_to else 'N/A'}

Best regards,
ICPS System
"""
    
    html_message = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #3498db;">Unit Completed</h2>
        <p>A unit has been completed:</p>
        
        <div style="background-color: #ebf5fb; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #3498db;">
            <p><strong>Student:</strong> {student.name}</p>
            <p><strong>Registration ID:</strong> {registration.id}</p>
            <p><strong>Provider:</strong> {registration.provider.name}</p>
            <p><strong>Course:</strong> {registration.field.name} ({registration.level})</p>
            <p><strong>Unit:</strong> {task.label}</p>
            <p><strong>Phase:</strong> {task.phase}</p>
            <p><strong>Completed At:</strong> {task.completed_at.strftime('%Y-%m-%d %H:%M:%S') if task.completed_at else 'N/A'}</p>
            <p><strong>Completed By:</strong> {task.assigned_to.username if task.assigned_to else 'N/A'}</p>
        </div>
        
        <p style="margin-top: 30px; color: #7f8c8d;">Best regards,<br>ICPS System</p>
    </div>
</body>
</html>
"""
    
    _send_email(subject, message, recipients, html_message)


def notify_ops_unit_due(task: UnitTask):
    """
    Other Providers: Notify Ops team when a unit is due.
    """
    registration = task.registration
    if registration.is_proqual:
        return  # ProQual has its own notification system
    
    if task.status == "DONE":
        return  # Don't notify for completed tasks
    
    if not task.assigned_to or not task.assigned_to.email:
        return
    
    student = registration.student
    days_until_due = (task.due_date - timezone.localdate()).days
    status_text = "OVERDUE" if days_until_due < 0 else f"Due in {days_until_due} day(s)"
    
    # Calculate colors for HTML
    color_primary = '#e74c3c' if days_until_due < 0 else '#f39c12'
    color_bg = '#ffebee' if days_until_due < 0 else '#fff3e0'
    
    subject = f"[ICPS] Unit Due: {task.label} - {student.name}"
    
    message = f"""
Unit Due Notification

A unit is due for the following student:

Student: {student.name}
Registration ID: {registration.id}
Provider: {registration.provider.name}
Unit: {task.label}
Phase: {task.phase}
Due Date: {task.due_date}
Status: {status_text}

Please ensure the unit is completed on time.

Best regards,
ICPS System
"""
    
    html_message = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: {color_primary};">Unit Due: {task.label}</h2>
        <p>A unit is due for the following student:</p>
        
        <div style="background-color: {color_bg}; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid {color_primary};">
            <p><strong>Student:</strong> {student.name}</p>
            <p><strong>Registration ID:</strong> {registration.id}</p>
            <p><strong>Provider:</strong> {registration.provider.name}</p>
            <p><strong>Unit:</strong> {task.label}</p>
            <p><strong>Phase:</strong> {task.phase}</p>
            <p><strong>Due Date:</strong> {task.due_date}</p>
            <p><strong style="color: {color_primary};">{status_text}</strong></p>
        </div>
        
        <p>Please ensure the unit is completed on time.</p>
        
        <p style="margin-top: 30px; color: #7f8c8d;">Best regards,<br>ICPS System</p>
    </div>
</body>
</html>
"""
    
    _send_email(subject, message, [task.assigned_to.email], html_message)


# ============================================================================
# PAYMENT NOTIFICATIONS (ALL PROVIDERS)
# ============================================================================

def notify_payment_due(installment: PaymentInstallment):
    """
    Notify student and sales team member for every due payment.
    Includes payment details: amount due, remaining balance, etc.
    """
    registration = installment.plan.registration
    student = registration.student
    sales_person = registration.registered_by
    
    recipients = []
    
    # Add student email if available
    if student.email:
        recipients.append(student.email)
    
    # Add sales person email if available
    if sales_person and sales_person.email:
        recipients.append(sales_person.email)
    
    if not recipients:
        logger.warning(f"Cannot notify payment due for installment {installment.id}: no recipients")
        return
    
    today = timezone.localdate()
    days_until_due = (installment.due_date - today).days
    status_text = "OVERDUE" if days_until_due < 0 else f"Due in {days_until_due} day(s)"
    
    # Calculate colors for HTML
    color_primary = '#e74c3c' if days_until_due < 0 else '#f39c12'
    color_bg = '#ffebee' if days_until_due < 0 else '#fff3e0'
    
    # Calculate remaining balance
    remaining_installments = installment.plan.installments.filter(paid_at__isnull=True).exclude(id=installment.id)
    remaining_balance = sum(inst.amount for inst in remaining_installments)
    total_remaining = remaining_balance + installment.amount
    
    subject = f"[ICPS] Payment Due: {installment.amount} - {student.name}"
    
    message = f"""
Payment Due Notification

Dear {student.name},

This is a reminder about your upcoming payment:

Payment Details:
- Amount Due: £{installment.amount}
- Due Date: {installment.due_date}
- Status: {status_text}
- Sequence: {installment.sequence} {'(Upfront Payment)' if installment.sequence == 0 else f'(Installment {installment.sequence})'}

Payment Summary:
- This Payment: £{installment.amount}
- Remaining Balance: £{remaining_balance}
- Total Remaining: £{total_remaining}

Course Details:
- Provider: {registration.provider.name}
- Course: {registration.field.name} ({registration.level})
- Registration ID: {registration.id}

Please ensure payment is made by the due date to avoid any delays in your course progress.

If you have any questions, please contact your sales representative: {sales_person.username if sales_person else 'N/A'}

Best regards,
ICPS System
"""
    
    html_message = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: {color_primary};">Payment Due Notification</h2>
        <p>Dear {student.name},</p>
        <p>This is a reminder about your upcoming payment:</p>
        
        <div style="background-color: {color_bg}; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid {color_primary};">
            <h3 style="margin-top: 0; color: #2c3e50;">Payment Details</h3>
            <p><strong>Amount Due:</strong> £{installment.amount}</p>
            <p><strong>Due Date:</strong> {installment.due_date}</p>
            <p><strong style="color: {color_primary};">Status:</strong> {status_text}</p>
            <p><strong>Sequence:</strong> {installment.sequence} {'(Upfront Payment)' if installment.sequence == 0 else f'(Installment {installment.sequence})'}</p>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #2c3e50;">Payment Summary</h3>
            <p><strong>This Payment:</strong> £{installment.amount}</p>
            <p><strong>Remaining Balance:</strong> £{remaining_balance}</p>
            <p><strong>Total Remaining:</strong> £{total_remaining}</p>
        </div>
        
        <div style="background-color: #ebf5fb; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #2c3e50;">Course Details</h3>
            <p><strong>Provider:</strong> {registration.provider.name}</p>
            <p><strong>Course:</strong> {registration.field.name} ({registration.level})</p>
            <p><strong>Registration ID:</strong> {registration.id}</p>
        </div>
        
        <p>Please ensure payment is made by the due date to avoid any delays in your course progress.</p>
        
        <p>If you have any questions, please contact your sales representative: <strong>{sales_person.username if sales_person else 'N/A'}</strong></p>
        
        <p style="margin-top: 30px; color: #7f8c8d;">Best regards,<br>ICPS System</p>
    </div>
</body>
</html>
"""
    
    _send_email(subject, message, recipients, html_message)


# ============================================================================
# LEGACY FUNCTIONS (for backward compatibility)
# ============================================================================

def notify_ops_pending_and_overdue():
    """
    Legacy function: Send email reminders to ops team for pending and overdue tasks.
    Now uses the new notification system.
    """
    today = timezone.localdate()
    qs = UnitTask.objects.select_related("assigned_to", "registration", "registration__student") \
                         .filter(status="PENDING", due_date__lte=today)
    
    for task in qs:
        registration = task.registration
        if registration.is_proqual:
            notify_proqual_unit_due(task)
        else:
            notify_ops_unit_due(task)


def notify_sales_payment_reminders():
    """
    Legacy function: Send email reminders to sales team for upcoming/overdue payments.
    Now uses the new notification system.
    """
    today = timezone.localdate()
    # Notify for payments due in 7 days, 1 day, or overdue
    qs = PaymentInstallment.objects.select_related(
        "plan", "plan__registration", "plan__registration__registered_by", "plan__registration__student"
    ).filter(paid_at__isnull=True)
    
    for inst in qs:
        days_left = (inst.due_date - today).days
        if days_left == 7 or days_left == 1 or days_left < 0:
            notify_payment_due(inst)
