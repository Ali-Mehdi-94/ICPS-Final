from django.contrib import admin
from django.db import transaction
from django.utils import timezone

from .models import (
    CourseProvider, Field, Level, Student, Registration, CustomUser,
    ProgramTemplate, UnitTemplate, AssignmentUnit, PaymentPlan, PaymentInstallment,
    SalesIncentive, OperationsIncentive, UnitTask
)

@admin.register(CourseProvider)
class CourseProviderAdmin(admin.ModelAdmin):
    search_fields = ("name",)

@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ("name", "provider")
    list_filter = ("provider",)
    search_fields = ("name",)

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ("number",)
    search_fields = ("number",)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")
    search_fields = ("name", "email", "phone")

@admin.register(ProgramTemplate)
class ProgramTemplateAdmin(admin.ModelAdmin):
    list_display = ("provider", "field", "level", "qualification_type", "default_unit_count", "duration_weeks", "has_forms_phase", "forms_weeks")
    list_filter = ("provider", "field", "level", "qualification_type", "has_forms_phase")
    search_fields = ("name",)
    fieldsets = (
        ("Basic Information", {
            "fields": ("provider", "field", "level", "qualification_type", "name")
        }),
        ("Duration & Units", {
            "fields": ("duration_weeks", "default_unit_count")
        }),
        ("ProQual Settings", {
            "fields": ("has_forms_phase", "forms_weeks"),
            "description": "For ProQual providers: Enable forms phase and set weeks"
        }),
    )

@admin.register(UnitTemplate)
class UnitTemplateAdmin(admin.ModelAdmin):
    list_display = ("program", "order", "title", "offset_weeks")
    list_filter = ("program",)
    ordering = ("program", "order")

class UnitTaskInline(admin.TabularInline):
    model = UnitTask
    extra = 0
    readonly_fields = ("week_index", "phase", "label", "due_date", "unit_number", "status")
    can_delete = False

class InstallmentInline(admin.TabularInline):
    model = PaymentInstallment
    extra = 0
    readonly_fields = ("sequence", "amount", "due_date", "paid_at")
    can_delete = False
    fields = ("sequence", "amount", "due_date", "paid_at")
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('plan', 'plan__registration')

@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ("registration", "total_fee", "upfront_percent", "months")
    inlines = [InstallmentInline]
    readonly_fields = ("registration",)

@admin.register(AssignmentUnit)
class AssignmentUnitAdmin(admin.ModelAdmin):
    list_display = ("registration", "order", "title", "due_date", "completed_at")
    list_filter = ("registration__assigned_to",)
    search_fields = ("title",)

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "provider", "field", "level", "qualification_type", "unit_count", "assigned_to", "deadline_date")
    list_filter = ("provider", "field", "level", "qualification_type", "assigned_to")
    search_fields = ("student__name", "student__email")
    
    fields = (
        "student", "provider", "field", "level",
        "qualification_type", "program_template",
        "unit_count", "upfront_payment_percent", "remaining_months",
        "estimated_completion_date", "deadline_date", "total_fee",
    )
    
    inlines = [UnitTaskInline]
    
    def get_inline_instances(self, request, obj=None):
        """Show PaymentPlan inline only if registration has a payment plan"""
        inlines = super().get_inline_instances(request, obj)
        if obj and hasattr(obj, 'payment_plan'):
            # Add installments inline through payment plan
            pass  # Installments are shown in PaymentPlan admin
        return inlines
    
    def _ops_queryset(self):
        return CustomUser.objects.filter(role="Ops", is_active=True).order_by("id")

    def _pick_next_ops_user(self):
        ops = list(self._ops_queryset())
        if not ops:
            return None
        # find last assigned_to among recent registrations
        last = Registration.objects.filter(assigned_to__isnull=False).order_by("-id").values_list("assigned_to_id", flat=True).first()
        if not last:
            return ops[0]
        ids = [u.id for u in ops]
        if last not in ids:
            return ops[0]
        idx = ids.index(last)
        # pick next (wrap around) — avoids repeating the same person
        next_idx = (idx + 1) % len(ops)
        return ops[next_idx]

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None

        # set who registered (the logged-in staff)
        if is_new and not obj.registered_by_id:
            obj.registered_by = request.user

        # set assigned_to via round-robin (avoid repeating)
        if is_new and not obj.assigned_to_id:
            obj.assigned_to = self._pick_next_ops_user()

        super().save_model(request, obj, form, change)
        # Signals will handle unit tasks and payment schedule creation

@admin.register(UnitTask)
class UnitTaskAdmin(admin.ModelAdmin):
    list_display = ("registration", "week_index", "phase", "label", "due_date", "assigned_to", "status", "completed_at")
    list_filter = ("phase", "status", "assigned_to")
    search_fields = ("label", "registration__student__name")
    readonly_fields = ("completed_at",)

@admin.register(SalesIncentive)
class SalesIncentiveAdmin(admin.ModelAdmin):
    list_display = ("registration", "sales_person", "amount", "paid", "paid_at")
    list_filter = ("paid", "sales_person")
    search_fields = ("registration__student__name",)
    readonly_fields = ("created_at", "updated_at")

@admin.register(OperationsIncentive)
class OperationsIncentiveAdmin(admin.ModelAdmin):
    list_display = ("registration", "ops_person", "amount", "paid", "completed_on_time", "paid_at")
    list_filter = ("paid", "completed_on_time", "ops_person")
    search_fields = ("registration__student__name",)
    readonly_fields = ("created_at", "updated_at")
