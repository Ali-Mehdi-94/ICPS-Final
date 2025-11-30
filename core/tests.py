from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status

from .models import (
    CustomUser, Student, CourseProvider, Field, Level,
    Registration, PaymentPlan, PaymentInstallment
)
from .services import build_payment_schedule


class BuildPaymentScheduleIdempotentTests(TestCase):
    """Tests for idempotent payment schedule logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.provider = CourseProvider.objects.create(name="OTHM")
        self.field = Field.objects.create(name="OHS", provider=self.provider)
        self.level = Level.objects.create(number=5)
        self.student = Student.objects.create(
            name="Test Student",
            email="test@example.com",
            phone="1234567890",
            dob="1990-01-01"
        )
        self.sales_user = CustomUser.objects.create_user(
            username="salesuser",
            password="testpass123",
            role="Sales"
        )
        self.registration = Registration.objects.create(
            student=self.student,
            provider=self.provider,
            field=self.field,
            level=self.level,
            registered_by=self.sales_user,
            upfront_payment_percent=50,
            remaining_months=2,
            total_fee=Decimal("1000.00")
        )

    def test_build_payment_schedule_creates_installments(self):
        """Test that build_payment_schedule creates installments correctly."""
        build_payment_schedule(self.registration, Decimal("1000.00"))
        
        plan = PaymentPlan.objects.get(registration=self.registration)
        installments = plan.installments.all()
        
        # Should have 3 installments: upfront (seq 0) + 2 monthly
        self.assertEqual(installments.count(), 3)
        
        # Verify upfront is 50% = 500
        upfront = installments.get(sequence=0)
        self.assertEqual(upfront.amount, Decimal("500.00"))
        
        # Verify monthly payments (250 each for 2 months)
        monthly1 = installments.get(sequence=1)
        monthly2 = installments.get(sequence=2)
        self.assertEqual(monthly1.amount, Decimal("250.00"))
        self.assertEqual(monthly2.amount, Decimal("250.00"))

    def test_build_payment_schedule_preserves_paid_upfront(self):
        """Test that running build_payment_schedule again preserves paid upfront."""
        # First run
        build_payment_schedule(self.registration, Decimal("1000.00"))
        
        plan = PaymentPlan.objects.get(registration=self.registration)
        upfront = plan.installments.get(sequence=0)
        
        # Mark upfront as paid
        upfront.paid_at = timezone.localdate()
        upfront.save()
        original_paid_at = upfront.paid_at
        original_amount = upfront.amount
        
        # Second run with different total_fee
        build_payment_schedule(self.registration, Decimal("1200.00"))
        
        # Refresh from database
        upfront.refresh_from_db()
        
        # Paid upfront should NOT be modified
        self.assertEqual(upfront.paid_at, original_paid_at)
        self.assertEqual(upfront.amount, original_amount)

    def test_build_payment_schedule_preserves_paid_monthly(self):
        """Test that paid monthly installments are preserved."""
        # First run
        build_payment_schedule(self.registration, Decimal("1000.00"))
        
        plan = PaymentPlan.objects.get(registration=self.registration)
        monthly1 = plan.installments.get(sequence=1)
        
        # Mark first monthly as paid
        monthly1.paid_at = timezone.localdate()
        monthly1.save()
        original_paid_at = monthly1.paid_at
        original_amount = monthly1.amount
        
        # Second run with different total_fee
        build_payment_schedule(self.registration, Decimal("1200.00"))
        
        # Refresh from database
        monthly1.refresh_from_db()
        
        # Paid installment should NOT be modified
        self.assertEqual(monthly1.paid_at, original_paid_at)
        self.assertEqual(monthly1.amount, original_amount)

    def test_build_payment_schedule_updates_unpaid_installments(self):
        """Test that unpaid installments are updated when schedule changes."""
        # First run with 1000
        build_payment_schedule(self.registration, Decimal("1000.00"))
        
        plan = PaymentPlan.objects.get(registration=self.registration)
        upfront = plan.installments.get(sequence=0)
        monthly1 = plan.installments.get(sequence=1)
        
        # Verify initial amounts
        self.assertEqual(upfront.amount, Decimal("500.00"))
        self.assertEqual(monthly1.amount, Decimal("250.00"))
        
        # Second run with 2000 (unpaid installments should update)
        build_payment_schedule(self.registration, Decimal("2000.00"))
        
        # Refresh from database
        upfront.refresh_from_db()
        monthly1.refresh_from_db()
        
        # Unpaid installments should be updated
        self.assertEqual(upfront.amount, Decimal("1000.00"))  # 50% of 2000
        self.assertEqual(monthly1.amount, Decimal("500.00"))  # 500 per month

    def test_build_payment_schedule_removes_extra_unpaid_only(self):
        """Test that only extra unpaid installments are removed when months reduced."""
        # First run with 3 months
        self.registration.remaining_months = 3
        self.registration.save()
        build_payment_schedule(self.registration, Decimal("1000.00"))
        
        plan = PaymentPlan.objects.get(registration=self.registration)
        
        # Should have 4 installments (upfront + 3 monthly)
        self.assertEqual(plan.installments.count(), 4)
        
        # Mark the third monthly (sequence 3) as paid
        monthly3 = plan.installments.get(sequence=3)
        monthly3.paid_at = timezone.localdate()
        monthly3.save()
        
        # Reduce to 2 months and run again
        self.registration.remaining_months = 2
        self.registration.save()
        build_payment_schedule(self.registration, Decimal("1000.00"))
        
        plan.refresh_from_db()
        
        # Paid installment at sequence 3 should still exist
        self.assertTrue(plan.installments.filter(sequence=3, paid_at__isnull=False).exists())

    def test_build_payment_schedule_no_delete_all(self):
        """Test that payment history is not wiped when updating."""
        # Create initial schedule
        build_payment_schedule(self.registration, Decimal("1000.00"))
        
        plan = PaymentPlan.objects.get(registration=self.registration)
        
        # Pay all installments
        for inst in plan.installments.all():
            inst.paid_at = timezone.localdate()
            inst.save()
        
        paid_count = plan.installments.filter(paid_at__isnull=False).count()
        
        # Run again (should not delete paid history)
        build_payment_schedule(self.registration, Decimal("1000.00"))
        
        plan.refresh_from_db()
        
        # All paid installments should still exist
        self.assertEqual(plan.installments.filter(paid_at__isnull=False).count(), paid_count)


class OverduePaymentsViewTests(TestCase):
    """Tests for the OverduePaymentsView API endpoint."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        
        self.ceo_user = CustomUser.objects.create_user(
            username="ceouser",
            password="testpass123",
            role="CEO"
        )
        self.sales_user = CustomUser.objects.create_user(
            username="salesuser",
            password="testpass123",
            role="Sales"
        )
        self.ops_user = CustomUser.objects.create_user(
            username="opsuser",
            password="testpass123",
            role="Ops"
        )
        
        self.provider = CourseProvider.objects.create(name="OTHM")
        self.field = Field.objects.create(name="OHS", provider=self.provider)
        self.level = Level.objects.create(number=5)
        self.student = Student.objects.create(
            name="Test Student",
            email="test@example.com",
            phone="1234567890",
            dob="1990-01-01"
        )
        # Create registration with total_fee - this will trigger signal to create PaymentPlan
        self.registration = Registration.objects.create(
            student=self.student,
            provider=self.provider,
            field=self.field,
            level=self.level,
            registered_by=self.sales_user,
            upfront_payment_percent=50,
            remaining_months=2,
            total_fee=Decimal("1000.00")
        )
        
        # Get the payment plan created by the signal
        self.plan = self.registration.payment_plan
        
        # Update the upfront installment to be overdue (30 days ago)
        self.overdue_installment = self.plan.installments.get(sequence=0)
        self.overdue_installment.due_date = timezone.localdate() - timedelta(days=30)
        self.overdue_installment.save()
        
        # Get the first monthly installment (sequence 1) as future installment
        self.future_installment = self.plan.installments.get(sequence=1)

    def test_ceo_can_view_all_overdue_payments(self):
        """Test that CEO can view all overdue payments."""
        self.client.force_authenticate(user=self.ceo_user)
        response = self.client.get('/api/dashboard/payments/overdue/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.overdue_installment.id)
        self.assertEqual(response.data[0]['student_name'], 'Test Student')
        self.assertEqual(response.data[0]['provider'], 'OTHM')
        self.assertEqual(response.data[0]['days_overdue'], 30)

    def test_sales_can_view_own_overdue_payments(self):
        """Test that Sales can only view their own overdue payments."""
        self.client.force_authenticate(user=self.sales_user)
        response = self.client.get('/api/dashboard/payments/overdue/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_ops_cannot_view_overdue_payments(self):
        """Test that Ops cannot access overdue payments endpoint."""
        self.client.force_authenticate(user=self.ops_user)
        response = self.client.get('/api/dashboard/payments/overdue/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access(self):
        """Test that unauthenticated users cannot access endpoint."""
        response = self.client.get('/api/dashboard/payments/overdue/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_overdue_payments_returned(self):
        """Test that only overdue (not future) payments are returned."""
        self.client.force_authenticate(user=self.ceo_user)
        response = self.client.get('/api/dashboard/payments/overdue/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only the overdue installment should be returned, not the future one
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.overdue_installment.id)

    def test_paid_installments_not_returned(self):
        """Test that paid installments are not returned even if past due date."""
        # Mark the overdue installment as paid
        self.overdue_installment.paid_at = timezone.localdate()
        self.overdue_installment.save()
        
        self.client.force_authenticate(user=self.ceo_user)
        response = self.client.get('/api/dashboard/payments/overdue/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
