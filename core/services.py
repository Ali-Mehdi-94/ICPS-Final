"""
Service functions for registration management.
All functions are idempotent - safe to re-run without creating duplicates.
"""
from datetime import date, timedelta
from django.db import transaction
from django.utils import timezone
from .models import (
    UnitTask, PaymentPlan, PaymentInstallment, ProgramTemplate, Registration
)


def apply_template_defaults(reg: Registration):
    """Fill unit_count/deadline based on selected template/provider if blank."""
    reg.apply_template_defaults()  # you already added this method
    # Use update() to avoid triggering signals
    Registration.objects.filter(pk=reg.pk).update(
        unit_count=reg.unit_count,
        deadline_date=reg.deadline_date
    )


def build_payment_schedule(reg: Registration, total_fee):
    """
    Create/refresh a payment plan + installments.
    PRESERVES existing paid installments.
    Only updates unpaid installments or creates new ones if needed.
    """
    if not total_fee:
        return

    plan, _ = PaymentPlan.objects.update_or_create(
        registration=reg,
        defaults={
            "total_fee": total_fee,
            "upfront_percent": reg.upfront_payment_percent,
            "months": reg.remaining_months,
        },
    )

    upfront_amount = round((total_fee * reg.upfront_payment_percent) / 100, 2)
    months = reg.remaining_months or 0
    today = timezone.localdate()
    
    # 1. Handle Upfront (Seq 0)
    try:
        inst_0 = plan.installments.get(sequence=0)
        if not inst_0.paid_at:
            inst_0.amount = upfront_amount
            inst_0.save()
    except PaymentInstallment.DoesNotExist:
        PaymentInstallment.objects.create(
            plan=plan, sequence=0, amount=upfront_amount, due_date=today
        )

    # 2. Handle Monthly Installments
    remaining_after_upfront = total_fee - upfront_amount
    per_month = round(remaining_after_upfront / months, 2) if months else 0
    
    existing_installments = {i.sequence: i for i in plan.installments.filter(sequence__gt=0)}
    
    for i in range(1, months + 1):
        due_date = today + timedelta(days=30 * i)
        if i in existing_installments:
            inst = existing_installments[i]
            if not inst.paid_at:
                inst.amount = per_month
                inst.due_date = due_date
                inst.save()
        else:
            PaymentInstallment.objects.create(
                plan=plan, sequence=i, amount=per_month, due_date=due_date
            )
            
    # 3. Cleanup: Remove any extra unpaid installments
    plan.installments.filter(sequence__gt=months, paid_at__isnull=True).delete()


def create_units_for_registration(reg: Registration):
    """
    Generate UnitTask timeline from ProgramTemplate.
    ProQual: Week 1 forms; weeks 2-8 buffer; then units; finally buffer/assessment weeks.
    Timeline starts from portal_allotment_date if set, otherwise from today.
    OTHM: straight units across duration_weeks.
    """
    # clear old tasks to keep this idempotent
    reg.tasks.all().delete()

    tmpl: ProgramTemplate | None = reg.program_template
    if not tmpl:
        return

    is_proqual = reg.provider.name.lower() == "proqual"
    
    # For ProQual, use portal_allotment_date if set, otherwise don't create tasks yet
    if is_proqual:
        if not reg.portal_allotment_date:
            # ProQual timeline hasn't started yet - don't create tasks
            return
        start = reg.portal_allotment_date
    else:
        start = timezone.localdate()
    
    week = 1

    if is_proqual:
        # Forms & documentation for week 1 only
        due = start + timedelta(days=7 * (week - 1))
        UnitTask.objects.create(
            registration=reg,
            week_index=week,
            phase="Forms",
            label="Forms & Documentation",
            due_date=due,
            assigned_to=reg.assigned_to,
        )
        week += 1
        
        # Buffer period: weeks 2-8 (7 weeks)
        for i in range(7):
            due = start + timedelta(days=7 * (week - 1))
            UnitTask.objects.create(
                registration=reg,
                week_index=week,
                phase="Buffer",
                label="Buffer Period",
                due_date=due,
                assigned_to=reg.assigned_to,
            )
            week += 1

    # Units
    unit_total = reg.unit_count or tmpl.default_unit_count
    for idx in range(1, unit_total + 1):
        due = start + timedelta(days=7 * (week - 1))
        UnitTask.objects.create(
            registration=reg,
            week_index=week,
            phase="Assignments",
            label=f"Unit {idx}",
            unit_number=idx,
            due_date=due,
            assigned_to=reg.assigned_to,  # keep visibility for ops
        )
        week += 1

    # Optional buffer for ProQual (assessment/resubmissions)
    if is_proqual:
        for _ in range(2):  # 2 extra weeks buffer by default
            due = start + timedelta(days=7 * (week - 1))
            UnitTask.objects.create(
                registration=reg,
                week_index=week,
                phase="Assessment/Buffer",
                label="Assessment & Resubmissions",
                due_date=due,
                assigned_to=reg.assigned_to,
            )
            week += 1
