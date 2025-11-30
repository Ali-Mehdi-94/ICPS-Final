from rest_framework import serializers
from .models import CustomUser, Student, Registration, CourseProvider, Field, Level, UnitTask, PaymentInstallment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']

class CourseProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseProvider
        fields = '__all__'

class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = '__all__'

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class UnitTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitTask
        fields = ['id', 'week_index', 'phase', 'label', 'due_date', 'unit_number', 'assigned_to', 'status', 'completed_at']

class PaymentInstallmentSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField()
    
    class Meta:
        model = PaymentInstallment
        fields = ['id', 'sequence', 'amount', 'due_date', 'paid_at', 'status']

class RegistrationSerializer(serializers.ModelSerializer):
    registered_by = serializers.PrimaryKeyRelatedField(read_only=True)
    qualification_type_display = serializers.CharField(source='get_qualification_type_display', read_only=True)
    
    # Nested serializers for detail view
    tasks = UnitTaskSerializer(many=True, read_only=True, source='tasks.all')
    installments = serializers.SerializerMethodField()
    
    # Display names for foreign keys
    student_name = serializers.CharField(source='student.name', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    field_name = serializers.CharField(source='field.name', read_only=True)
    level_name = serializers.CharField(source='level.number', read_only=True)
    
    # Progress tracking fields
    unit_progress_percent = serializers.ReadOnlyField()
    payment_progress_percent = serializers.ReadOnlyField()
    units_total = serializers.ReadOnlyField()
    units_done = serializers.ReadOnlyField()
    units_overdue = serializers.ReadOnlyField()
    payments_total = serializers.ReadOnlyField()
    payments_paid = serializers.ReadOnlyField()
    payments_overdue = serializers.ReadOnlyField()

    def get_installments(self, obj):
        """Get payment installments if payment plan exists"""
        if hasattr(obj, 'payment_plan'):
            installments = obj.payment_plan.installments.all()
            return PaymentInstallmentSerializer(installments, many=True).data
        return []

    class Meta:
        model = Registration
        fields = [
            "id",
            "student",
            "student_name",
            "provider",
            "provider_name",
            "field",
            "field_name",
            "level",
            "level_name",
            "qualification_type",
            "qualification_type_display",
            "registered_by",
            "assigned_to",
            "total_fee",
            "upfront_payment_percent",
            "remaining_months",
            "estimated_completion_date",
            "deadline_date",
            "portal_allotment_date",
            "unit_count",
            "program_template",
            # Progress + payments
            "unit_progress_percent",
            "payment_progress_percent",
            "units_total",
            "units_done",
            "units_overdue",
            "payments_total",
            "payments_paid",
            "payments_overdue",
            # Incentive tracking
            "sales_incentive_paid",
            "ops_incentive_paid",
            # Nested data
            "tasks",
            "installments",
        ]
        read_only_fields = ("registered_by", "sales_incentive_paid", "ops_incentive_paid", "tasks", "installments")

    def create(self, validated_data):
        validated_data["registered_by"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # prevent tampering on update as well
        validated_data.pop("registered_by", None)
        return super().update(instance, validated_data)
