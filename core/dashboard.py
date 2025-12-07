"""
Dashboard helper functions for CEO and other role-based summaries.
"""
from datetime import timedelta
from django.db.models import Sum, Q, Avg
from django.utils import timezone
from .models import Student, Registration, PaymentInstallment, UnitTask, SalesIncentive, OperationsIncentive, CustomUser


def get_ceo_summary():
    """
    Return a dict with high-level CEO KPIs.
    Uses your existing progress helper properties on Registration.
    """
    today = timezone.localdate()

    # Basic counts
    students_total = Student.objects.count()
    registrations_total = Registration.objects.count()
    registrations_active = Registration.objects.filter(
        deadline_date__gte=today
    ).count()

    # Completed registrations & overdue units using your progress helpers
    registrations_completed = 0
    units_overdue_total = 0
    
    for reg in Registration.objects.all():
        if reg.units_total and reg.units_done == reg.units_total:
            registrations_completed += 1
        units_overdue_total += reg.units_overdue

    # Revenue expected = sum of all total_fee from Registration
    # Use total_fee directly from Registration (more reliable than payment_plan)
    revenue_expected = Registration.objects.aggregate(
        total=Sum("total_fee")
    )["total"] or 0

    # Revenue collected = sum of all paid installments
    revenue_collected = PaymentInstallment.objects.filter(
        paid_at__isnull=False
    ).aggregate(total=Sum("amount"))["total"] or 0

    # Overdue payments count
    payments_overdue = PaymentInstallment.objects.filter(
        paid_at__isnull=True,
        due_date__lt=today
    ).count()

    # Overdue ops tasks (UnitTask)
    ops_overdue_tasks = UnitTask.objects.filter(
        status="PENDING",
        due_date__lt=today
    ).count()

    return {
        "students_total": students_total,
        "registrations_total": registrations_total,
        "registrations_active": registrations_active,
        "registrations_completed": registrations_completed,
        "revenue_expected": float(revenue_expected) if revenue_expected else 0.0,
        "revenue_collected": float(revenue_collected) if revenue_collected else 0.0,
        "payments_overdue": payments_overdue,
        "units_overdue_total": units_overdue_total,
        "ops_overdue_tasks": ops_overdue_tasks,
    }


def get_sales_summary(sales_user):
    """
    Return a dict with sales-specific KPIs for the logged-in sales person.
    Filters all data by registrations where registered_by = sales_user.
    """
    today = timezone.localdate()
    
    # Get all registrations by this sales person
    my_registrations = Registration.objects.filter(registered_by=sales_user)
    
    # Basic counts
    students_total = Student.objects.filter(
        registration__registered_by=sales_user
    ).distinct().count()
    
    registrations_total = my_registrations.count()
    
    registrations_active = my_registrations.filter(
        deadline_date__gte=today
    ).count()
    
    # Completed registrations & progress metrics
    registrations_completed = 0
    units_overdue_total = 0
    total_progress_percent = 0
    
    for reg in my_registrations:
        if reg.units_total and reg.units_done == reg.units_total:
            registrations_completed += 1
        units_overdue_total += reg.units_overdue
        total_progress_percent += reg.unit_progress_percent
    
    # Average progress percentage
    avg_progress_percent = (
        int(total_progress_percent / registrations_total) 
        if registrations_total > 0 else 0
    )
    
    # Revenue expected = sum of total_fee from my registrations
    revenue_expected = my_registrations.aggregate(
        total=Sum("total_fee")
    )["total"] or 0
    
    # Revenue collected = sum of paid installments from my registrations' payment plans
    revenue_collected = PaymentInstallment.objects.filter(
        plan__registration__registered_by=sales_user,
        paid_at__isnull=False
    ).aggregate(total=Sum("amount"))["total"] or 0
    
    # Payment status breakdown
    payments_total = PaymentInstallment.objects.filter(
        plan__registration__registered_by=sales_user
    ).count()
    
    payments_paid = PaymentInstallment.objects.filter(
        plan__registration__registered_by=sales_user,
        paid_at__isnull=False
    ).count()
    
    payments_overdue = PaymentInstallment.objects.filter(
        plan__registration__registered_by=sales_user,
        paid_at__isnull=True,
        due_date__lt=today
    ).count()
    
    payments_pending = payments_total - payments_paid - payments_overdue
    
    # Incentive tracking
    incentives_earned = SalesIncentive.objects.filter(
        sales_person=sales_user,
        paid=True
    ).count()
    
    incentives_pending = SalesIncentive.objects.filter(
        sales_person=sales_user,
        paid=False
    ).count()
    
    # Calculate incentive amounts
    incentives_amount_earned = SalesIncentive.objects.filter(
        sales_person=sales_user,
        paid=True
    ).aggregate(total=Sum("amount"))["total"] or 0
    
    incentives_amount_pending = SalesIncentive.objects.filter(
        sales_person=sales_user,
        paid=False
    ).aggregate(total=Sum("amount"))["total"] or 0
    
    return {
        "students_total": students_total,
        "registrations_total": registrations_total,
        "registrations_active": registrations_active,
        "registrations_completed": registrations_completed,
        "avg_progress_percent": avg_progress_percent,
        "revenue_expected": float(revenue_expected) if revenue_expected else 0.0,
        "revenue_collected": float(revenue_collected) if revenue_collected else 0.0,
        "revenue_pending": float(revenue_expected - revenue_collected) if revenue_expected else 0.0,
        "payments_total": payments_total,
        "payments_paid": payments_paid,
        "payments_pending": payments_pending,
        "payments_overdue": payments_overdue,
        "units_overdue_total": units_overdue_total,
        "incentives_earned": incentives_earned,
        "incentives_pending": incentives_pending,
        "incentives_amount_earned": float(incentives_amount_earned) if incentives_amount_earned else 0.0,
        "incentives_amount_pending": float(incentives_amount_pending) if incentives_amount_pending else 0.0,
    }


def get_ops_summary(user):
    """
    Returns a summary of everything related to ONE Ops member:
    - how many students/registrations they handle
    - how many tasks are done / pending / overdue
    - how many units are completed
    - incentives earned / pending
    """
    today = timezone.localdate()
    in_7_days = today + timedelta(days=7)

    # All registrations assigned to this Ops user
    regs = Registration.objects.filter(assigned_to=user)

    registrations_total = regs.count()
    registrations_active = regs.filter(deadline_date__gte=today).count()
    
    # Completed registrations - check if all units are done
    registrations_completed = 0
    for reg in regs:
        if reg.units_total and reg.units_done == reg.units_total:
            registrations_completed += 1

    # All tasks for these registrations
    tasks = UnitTask.objects.filter(registration__in=regs)

    tasks_total = tasks.count()
    tasks_done = tasks.filter(status="DONE").count()
    tasks_pending = tasks.filter(status="PENDING").count()
    tasks_due_7 = tasks.filter(
        status="PENDING",
        due_date__gte=today,
        due_date__lte=in_7_days
    ).count()
    tasks_overdue = tasks.filter(
        status="PENDING",
        due_date__lt=today
    ).count()

    # Only assignment units (ignore forms/buffer)
    unit_tasks = tasks.filter(unit_number__isnull=False)
    units_total = unit_tasks.count()
    units_done = unit_tasks.filter(status="DONE").count()
    units_overdue = unit_tasks.filter(
        status="PENDING",
        due_date__lt=today
    ).count()

    # Average unit progress across this Ops user's registrations
    progress_values = [r.unit_progress_percent for r in regs]
    avg_progress = int(sum(progress_values) / len(progress_values)) if progress_values else 0

    # Incentives (per OperationsIncentive model)
    # Note: using ops_person field (not user) and paid field (not is_paid)
    ops_incentives = OperationsIncentive.objects.filter(ops_person=user)
    incentives_earned_qs = ops_incentives.filter(paid=True)
    incentives_pending_qs = ops_incentives.filter(paid=False)

    incentives_earned_count = incentives_earned_qs.count()
    incentives_pending_count = incentives_pending_qs.count()

    incentives_amount_earned = (
        incentives_earned_qs.aggregate(total=Sum("amount"))["total"] or 0
    )
    incentives_amount_pending = (
        incentives_pending_qs.aggregate(total=Sum("amount"))["total"] or 0
    )

    # Upcoming registration deadlines (within 7 days)
    upcoming_deadlines = regs.filter(
        deadline_date__gte=today,
        deadline_date__lte=in_7_days,
    ).count()

    return {
        "registrations_total": registrations_total,
        "registrations_active": registrations_active,
        "registrations_completed": registrations_completed,

        "tasks_total": tasks_total,
        "tasks_done": tasks_done,
        "tasks_pending": tasks_pending,
        "tasks_due_7_days": tasks_due_7,
        "tasks_overdue": tasks_overdue,

        "units_total": units_total,
        "units_done": units_done,
        "units_overdue": units_overdue,
        "avg_unit_progress_percent": avg_progress,

        "upcoming_deadlines": upcoming_deadlines,

        "incentives_earned_count": incentives_earned_count,
        "incentives_pending_count": incentives_pending_count,
        "incentives_amount_earned": float(incentives_amount_earned) if incentives_amount_earned else 0.0,
        "incentives_amount_pending": float(incentives_amount_pending) if incentives_amount_pending else 0.0,
    }


def get_proqual_admin_summary():
    """
    Return a dict with ProQual admin dashboard data:
    - All ProQual registrations
    - Registrations pending portal allocation
    - Registrations pending ops assignment
    - Progress tracking for all ProQual students
    """
    from .models import CourseProvider
    
    today = timezone.localdate()
    
    # Get ProQual provider
    try:
        proqual_provider = CourseProvider.objects.get(name__iexact="ProQual")
    except CourseProvider.DoesNotExist:
        return {
            "error": "ProQual provider not found in database",
            "registrations_total": 0,
            "registrations_pending_portal": 0,
            "registrations_pending_assignment": 0,
            "registrations_active": 0,
            "registrations_completed": 0,
        }
    
    # All ProQual registrations
    proqual_regs = Registration.objects.filter(provider=proqual_provider)
    
    registrations_total = proqual_regs.count()
    
    # Pending portal allocation (no portal_allotment_date)
    registrations_pending_portal = proqual_regs.filter(
        portal_allotment_date__isnull=True
    ).count()
    
    # Pending ops assignment (no assigned_to)
    registrations_pending_assignment = proqual_regs.filter(
        assigned_to__isnull=True
    ).count()
    
    # Active registrations (have portal date and deadline hasn't passed)
    registrations_active = proqual_regs.filter(
        portal_allotment_date__isnull=False,
        deadline_date__gte=today
    ).count()
    
    # Completed registrations
    registrations_completed = 0
    units_overdue_total = 0
    total_progress_percent = 0
    
    for reg in proqual_regs:
        if reg.units_total and reg.units_done == reg.units_total:
            registrations_completed += 1
        units_overdue_total += reg.units_overdue
        total_progress_percent += reg.unit_progress_percent
    
    avg_progress_percent = (
        int(total_progress_percent / registrations_total)
        if registrations_total > 0 else 0
    )
    
    # Ops team performance (for assigned registrations)
    ops_performance = {}
    assigned_regs = proqual_regs.filter(assigned_to__isnull=False)
    for reg in assigned_regs:
        ops_id = reg.assigned_to_id
        if ops_id not in ops_performance:
            ops_performance[ops_id] = {
                "ops_name": reg.assigned_to.username,
                "total_registrations": 0,
                "completed_registrations": 0,
                "avg_progress": 0,
                "overdue_units": 0,
            }
        ops_perf = ops_performance[ops_id]
        ops_perf["total_registrations"] += 1
        if reg.units_total and reg.units_done == reg.units_total:
            ops_perf["completed_registrations"] += 1
        ops_perf["overdue_units"] += reg.units_overdue
    
    # Calculate average progress for each ops
    for ops_id, perf in ops_performance.items():
        ops_regs = assigned_regs.filter(assigned_to_id=ops_id)
        if ops_regs.exists():
            progress_values = [r.unit_progress_percent for r in ops_regs]
            perf["avg_progress"] = int(sum(progress_values) / len(progress_values)) if progress_values else 0
    
    return {
        "registrations_total": registrations_total,
        "registrations_pending_portal": registrations_pending_portal,
        "registrations_pending_assignment": registrations_pending_assignment,
        "registrations_active": registrations_active,
        "registrations_completed": registrations_completed,
        "avg_progress_percent": avg_progress_percent,
        "units_overdue_total": units_overdue_total,
        "ops_performance": list(ops_performance.values()),
    }


def get_hr_summary():
    """
    Return a dict with HR dashboard data:
    - Total users
    - Active/inactive users
    - Role breakdown
    """
    # Total users
    total_users = CustomUser.objects.count()
    
    # Active/inactive users
    active_users = CustomUser.objects.filter(is_active=True).count()
    inactive_users = CustomUser.objects.filter(is_active=False).count()
    
    # Role breakdown
    role_breakdown = {}
    for role_code, role_name in CustomUser.ROLE_CHOICES:
        count = CustomUser.objects.filter(role=role_code).count()
        role_breakdown[role_code] = {
            "name": role_name,
            "count": count,
        }
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "role_breakdown": role_breakdown,
    }


def get_finance_summary():
    """
    Return a dict with Finance dashboard data:
    - Revenue expected vs collected
    - Overdue payments
    - Incentive liabilities (sales + ops)
    """
    today = timezone.localdate()
    
    # Revenue expected = sum of all total_fee from Registration
    revenue_expected = Registration.objects.aggregate(
        total=Sum("total_fee")
    )["total"] or 0
    
    # Revenue collected = sum of all paid installments
    revenue_collected = PaymentInstallment.objects.filter(
        paid_at__isnull=False
    ).aggregate(total=Sum("amount"))["total"] or 0
    
    # Revenue pending
    revenue_pending = revenue_expected - revenue_collected
    
    # Overdue payments count and amount
    overdue_installments = PaymentInstallment.objects.filter(
        paid_at__isnull=True,
        due_date__lt=today
    )
    overdue_payments_count = overdue_installments.count()
    overdue_payments_amount = overdue_installments.aggregate(
        total=Sum("amount")
    )["total"] or 0
    
    # Incentive liabilities
    # Sales incentives pending
    sales_incentives_pending = SalesIncentive.objects.filter(paid=False)
    sales_incentives_pending_count = sales_incentives_pending.count()
    sales_incentives_pending_amount = sales_incentives_pending.aggregate(
        total=Sum("amount")
    )["total"] or 0
    
    # Ops incentives pending
    ops_incentives_pending = OperationsIncentive.objects.filter(paid=False)
    ops_incentives_pending_count = ops_incentives_pending.count()
    ops_incentives_pending_amount = ops_incentives_pending.aggregate(
        total=Sum("amount")
    )["total"] or 0
    
    # Total incentive liabilities
    total_incentive_liabilities = sales_incentives_pending_amount + ops_incentives_pending_amount
    
    return {
        "revenue_expected": float(revenue_expected) if revenue_expected else 0.0,
        "revenue_collected": float(revenue_collected) if revenue_collected else 0.0,
        "revenue_pending": float(revenue_pending) if revenue_pending else 0.0,
        "overdue_payments_count": overdue_payments_count,
        "overdue_payments_amount": float(overdue_payments_amount) if overdue_payments_amount else 0.0,
        "sales_incentives_pending_count": sales_incentives_pending_count,
        "sales_incentives_pending_amount": float(sales_incentives_pending_amount) if sales_incentives_pending_amount else 0.0,
        "ops_incentives_pending_count": ops_incentives_pending_count,
        "ops_incentives_pending_amount": float(ops_incentives_pending_amount) if ops_incentives_pending_amount else 0.0,
        "total_incentive_liabilities": float(total_incentive_liabilities) if total_incentive_liabilities else 0.0,
    }
