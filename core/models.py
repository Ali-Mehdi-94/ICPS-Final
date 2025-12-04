# Models for ICPS - Student Registration & Course Management System
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.conf import settings
from datetime import date
from dateutil.relativedelta import relativedelta


from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)



class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('Sales', 'Sales Team'),
        ('Ops', 'Operations Team'),
        ('CEO', 'Chief Executive Officer'),
        ('ProQualAdmin', 'ProQual Administrator'),
        ('HR', 'Human Resources'),
        ('Finance', 'Finance'),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)

    objects = CustomUserManager()  # ✅ Add this

    # Fix reverse accessor conflict:
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )



# Course Providers like OTHM, PROQUAL, etc.
class CourseProvider(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Fields like OHS, Business, IT, etc.
class Field(models.Model):
    name = models.CharField(max_length=100)
    provider = models.ForeignKey(CourseProvider, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.provider.name}"


# Levels like 3, 4, 5, 6, 7
class Level(models.Model):
    number = models.IntegerField()

    def __str__(self):
        return f"Level {self.number}"


# Main Student model
class Student(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    dob = models.DateField()

    def __str__(self):
        return self.name


# Registration connects Student to course, level, field, staff, etc.
class Registration(models.Model):
    QUALIFICATION_TYPE_CHOICES = (
        ('award', 'Award'),
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('extended', 'Extended Diploma'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    provider = models.ForeignKey(CourseProvider, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    qualification_type = models.CharField(max_length=20, choices=QUALIFICATION_TYPE_CHOICES, blank=True, null=True, help_text="Select qualification type (Award, Certificate, Diploma, Extended)")
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,related_name="registrations_made",db_constraint=True,)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_students",db_constraint=True,)
    upfront_payment_percent = models.IntegerField(default=50)
    remaining_months = models.IntegerField(default=2)
    estimated_completion_date = models.DateField(null=True, blank=True)
    program_template = models.ForeignKey('ProgramTemplate', on_delete=models.SET_NULL, null=True, blank=True)
    unit_count = models.PositiveIntegerField(null=True, blank=True, help_text="Manually set the number of units for this registration")
    deadline_date = models.DateField(null=True, blank=True)
    total_fee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Total fee - used to generate payment installments")
    
    # ProQual specific: Portal allotment date (timeline starts from this date)
    portal_allotment_date = models.DateField(null=True, blank=True, help_text="ProQual: Date when portal was allocated. 32-week timeline starts from this date.")
    
    # Incentive tracking
    sales_incentive_paid = models.BooleanField(default=False, help_text="Sales team incentive paid when full payment received")
    ops_incentive_paid = models.BooleanField(default=False, help_text="Ops team incentive paid when coursework completed on time")
    
    @property
    def is_proqual(self):
        """Check if this registration is for ProQual provider"""
        return self.provider.name.lower() == "proqual"
    
    def __str__(self):
        qual = f" - {self.get_qualification_type_display()}" if self.qualification_type else ""
        return f"{self.student.name} - {self.provider.name} ({self.level}){qual}"
    
    def apply_template_defaults(self):
        """
        Call this after program_template is set.
        Fills unit_count and deadline_date if missing.
        """
        if self.program_template:
            if not self.unit_count:
                self.unit_count = self.program_template.default_unit_count

            # Prefer the user-entered estimated_completion_date if present
            if self.estimated_completion_date and not self.deadline_date:
                self.deadline_date = self.estimated_completion_date

            # Otherwise compute now + duration_months based on provider
            if not self.deadline_date:
                base = date.today()
                months = self._calculate_duration_months()
                self.deadline_date = base + relativedelta(months=months)
        else:
            # If no template, still set deadline_date from estimated_completion_date if available
            if self.estimated_completion_date and not self.deadline_date:
                self.deadline_date = self.estimated_completion_date
            # If still no deadline_date, calculate based on provider defaults
            elif not self.deadline_date:
                base = date.today()
                months = self._calculate_duration_months()
                self.deadline_date = base + relativedelta(months=months)
    
    def _calculate_duration_months(self):
        """Calculate duration based on provider and qualification type"""
        provider_name = self.provider.name.lower() if self.provider.name else ""
        
        if "othm" in provider_name:
            # OTHM: 3-4 months (use 4 as default)
            return 4
        elif "proqual" in provider_name:
            # ProQual: 6-10 months (use 8 as default)
            return 8
        
        # Default fallback
        return 3
    
    def is_fully_paid(self):
        """Check if all payments are completed"""
        if not hasattr(self, 'payment_plan'):
            return False
        return all(inst.paid_at for inst in self.payment_plan.installments.all())
    
    def is_coursework_completed_on_time(self):
        """Check if all coursework is completed within deadline"""
        if not self.deadline_date:
            return False
        
        # Check if all assignment tasks (UnitTask with phase="Assignments") are completed
        assignment_tasks = self.tasks.filter(phase="Assignments")
        if not assignment_tasks.exists():
            return False
        
        # Check if all assignment tasks are completed
        all_completed = all(task.status == "DONE" for task in assignment_tasks)
        if not all_completed:
            return False
        
        # Check if completed before deadline
        from django.utils import timezone
        completed_tasks = assignment_tasks.filter(status="DONE", completed_at__isnull=False)
        if not completed_tasks.exists():
            return False
        
        last_completion = completed_tasks.order_by('-completed_at').first()
        if last_completion and last_completion.completed_at:
            return last_completion.completed_at.date() <= self.deadline_date
        
        return False
    
    def update_sales_incentive_status(self):
        """Update sales incentive status when payment is fully received"""
        if self.is_fully_paid() and not self.sales_incentive_paid:
            self.sales_incentive_paid = True
            self.save(update_fields=['sales_incentive_paid'])
            
            # Create or update SalesIncentive record
            from django.utils import timezone
            now = timezone.now()
            sales_incentive, created = SalesIncentive.objects.get_or_create(
                registration=self,
                defaults={
                    'sales_person': self.registered_by,
                    'amount': 0,  # Set amount as needed
                    'paid': True,
                    'paid_at': now,
                }
            )
            if not created:
                sales_incentive.paid = True
                sales_incentive.paid_at = now
                sales_incentive.save()
    
    def update_ops_incentive_status(self):
        """Update ops incentive status when coursework is completed on time"""
        if self.is_coursework_completed_on_time() and not self.ops_incentive_paid:
            self.ops_incentive_paid = True
            self.save(update_fields=['ops_incentive_paid'])
            
            # Create or update OperationsIncentive record
            from django.utils import timezone
            now = timezone.now()
            ops_incentive, created = OperationsIncentive.objects.get_or_create(
                registration=self,
                defaults={
                    'ops_person': self.assigned_to,
                    'amount': 0,  # Set amount as needed
                    'paid': True,
                    'completed_on_time': True,
                    'paid_at': now,
                }
            )
            if not created:
                ops_incentive.paid = True
                ops_incentive.completed_on_time = True
                ops_incentive.paid_at = now
                ops_incentive.save()
    
    # ---------- PROGRESS HELPERS ----------
    
    @property
    def units_total(self) -> int:
        """
        Total assignment units for this registration (not forms/buffer).
        We count UnitTasks where phase='Assignments'.
        """
        return self.tasks.filter(phase="Assignments").count()
    
    @property
    def units_done(self) -> int:
        """
        How many assignment units are marked DONE.
        """
        return self.tasks.filter(phase="Assignments", status="DONE").count()
    
    @property
    def units_overdue(self) -> int:
        """
        Assignment units whose due_date has passed and are still pending.
        """
        from django.utils import timezone
        today = timezone.localdate()
        return self.tasks.filter(
            phase="Assignments",
            status="PENDING",
            due_date__lt=today,
        ).count()
    
    @property
    def unit_progress_percent(self) -> int:
        """
        Percentage of assignment units completed.
        """
        total = self.units_total or 0
        if total == 0:
            return 0
        return int((self.units_done / total) * 100)
    
    @property
    def payments_total(self) -> int:
        """
        Total number of installments (including upfront).
        """
        plan = getattr(self, "payment_plan", None)
        if not plan:
            return 0
        return plan.installments.count()
    
    @property
    def payments_paid(self) -> int:
        """
        Number of installments that have been paid.
        """
        plan = getattr(self, "payment_plan", None)
        if not plan:
            return 0
        return plan.installments.filter(paid_at__isnull=False).count()
    
    @property
    def payments_overdue(self) -> int:
        """
        Number of installments that are overdue (due_date passed and not paid).
        """
        plan = getattr(self, "payment_plan", None)
        if not plan:
            return 0
        from django.utils import timezone
        today = timezone.localdate()
        return plan.installments.filter(
            paid_at__isnull=True,
            due_date__lt=today,
        ).count()
    
    @property
    def payment_progress_percent(self) -> int:
        """
        Percentage of installments paid.
        """
        total = self.payments_total
        if total == 0:
            return 0
        return int((self.payments_paid / total) * 100)

class UnitTask(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('DONE', 'Done'),
    )

    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='tasks')
    week_index   = models.PositiveIntegerField()  # 1..N
    phase        = models.CharField(max_length=50)  # Forms / Assignments / Assessment/Buffer
    label        = models.CharField(max_length=120) # e.g. "Unit 1" or "Forms & Documentation"
    due_date     = models.DateField()
    unit_number  = models.PositiveIntegerField(null=True, blank=True)  # only for Assignments
    assigned_to  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('registration', 'week_index')

    def __str__(self):
        return f"Reg#{self.registration_id} • W{self.week_index} • {self.label}"


# --- PROGRAM / UNIT TEMPLATES ---

class ProgramTemplate(models.Model):
    QUAL_TYPE_CHOICES = (
        ("award", "Award"),
        ("certificate", "Certificate"),
        ("diploma", "Diploma"),
        ("extended", "Extended Diploma"),
    )
    
    provider = models.ForeignKey(CourseProvider, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    qualification_type = models.CharField(max_length=20, choices=QUAL_TYPE_CHOICES, blank=True, null=True, help_text="Optional: Specific qualification type for this template")
    name = models.CharField(max_length=120, blank=True)  # e.g., "OTHM OHS L5"
    duration_weeks = models.IntegerField(default=10)      # default timeline
    default_unit_count = models.IntegerField(default=6, help_text="Default number of units (can be overridden in registration)")
    
    # ProQual specific: forms phase
    has_forms_phase = models.BooleanField(default=False, help_text="ProQual: First 8 weeks for forms")
    forms_weeks = models.PositiveIntegerField(default=0, help_text="Number of weeks allocated for forms phase")

    class Meta:
        unique_together = ('provider', 'field', 'level', 'qualification_type')

    def __str__(self):
        qual = f" - {self.get_qualification_type_display()}" if self.qualification_type else ""
        return self.name or f"{self.provider} / {self.field} / {self.level}{qual}"

class UnitTemplate(models.Model):
    program = models.ForeignKey(ProgramTemplate, on_delete=models.CASCADE, related_name='units')
    order = models.IntegerField()
    title = models.CharField(max_length=200)  # e.g., "Unit 1 - Risk Assessment"
    offset_weeks = models.IntegerField(default=1)  # due week (1..N)

    class Meta:
        unique_together = ('program', 'order')
        ordering = ('order',)

    def __str__(self):
        return f"{self.program} / {self.order}: {self.title}"

# --- PER-REGISTRATION UNITS (TASKS) ---

class AssignmentUnit(models.Model):
    registration = models.ForeignKey('Registration', on_delete=models.CASCADE, related_name='assignment_units')
    order = models.IntegerField()
    title = models.CharField(max_length=200)
    due_date = models.DateField()
    completed_at = models.DateField(null=True, blank=True)

    @property
    def status(self):
        if self.completed_at:
            return "completed"
        from django.utils import timezone
        return "overdue" if self.due_date < timezone.localdate() else "due"

    class Meta:
        ordering = ('order',)

# --- PAYMENTS ---

class PaymentPlan(models.Model):
    registration = models.OneToOneField('Registration', on_delete=models.CASCADE, related_name='payment_plan')
    total_fee = models.DecimalField(max_digits=12, decimal_places=2)
    upfront_percent = models.IntegerField(default=50)
    months = models.IntegerField(default=2)

    def __str__(self):
        return f"Plan for {self.registration_id}"

class PaymentInstallment(models.Model):
    plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, related_name='installments')
    sequence = models.IntegerField()  # 0 = upfront, 1..N = months
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    paid_at = models.DateField(null=True, blank=True)

    @property
    def status(self):
        from django.utils import timezone
        if self.paid_at:
            return "paid"
        return "overdue" if self.due_date < timezone.localdate() else "due"

    class Meta:
        unique_together = ('plan', 'sequence')
        ordering = ('sequence',)


# --- INCENTIVE TRACKING ---

class SalesIncentive(models.Model):
    """Tracks sales team incentives - paid when student fully pays"""
    registration = models.OneToOneField(Registration, on_delete=models.CASCADE, related_name='sales_incentive')
    sales_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sales_incentives')
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Incentive amount")
    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        status = "Paid" if self.paid else "Pending"
        return f"Sales Incentive - {self.registration.student.name} ({status})"


class OperationsIncentive(models.Model):
    """Tracks operations team incentives - paid when coursework completed on time"""
    registration = models.OneToOneField(Registration, on_delete=models.CASCADE, related_name='ops_incentive')
    ops_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='ops_incentives')
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Incentive amount")
    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    completed_on_time = models.BooleanField(default=False, help_text="Whether coursework was completed within deadline")
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        status = "Paid" if self.paid else "Pending"
        return f"Ops Incentive - {self.registration.student.name} ({status})"

