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


class OpsCannotCreateRegistrationTests(TestCase):
    """Tests for restricting Ops users from creating registrations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        
        self.ops_user = CustomUser.objects.create_user(
            username="opsuser",
            password="testpass123",
            role="Ops"
        )
        self.sales_user = CustomUser.objects.create_user(
            username="salesuser",
            password="testpass123",
            role="Sales"
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
    
    def test_ops_cannot_create_registration(self):
        """Test that Ops users cannot create registrations."""
        self.client.force_authenticate(user=self.ops_user)
        
        response = self.client.post('/api/registrations/', {
            'student': self.student.id,
            'provider': self.provider.id,
            'field': self.field.id,
            'level': self.level.id,
        })
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('not allowed', response.data['detail'].lower())
    
    def test_sales_can_create_registration(self):
        """Test that Sales users can still create registrations."""
        self.client.force_authenticate(user=self.sales_user)
        
        response = self.client.post('/api/registrations/', {
            'student': self.student.id,
            'provider': self.provider.id,
            'field': self.field.id,
            'level': self.level.id,
        })
        
        # Should succeed (201 Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class IsAdminOrSalesPermissionTests(TestCase):
    """Tests for the IsAdminOrSales permission class."""
    
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
        self.proqual_user = CustomUser.objects.create_user(
            username="proqualadmin",
            password="testpass123",
            role="ProQualAdmin"
        )
        
        self.provider = CourseProvider.objects.create(name="OTHM")
    
    def test_ops_can_read_providers(self):
        """Test that Ops can read (GET) providers."""
        self.client.force_authenticate(user=self.ops_user)
        
        response = self.client.get('/api/providers/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_ops_cannot_create_provider(self):
        """Test that Ops cannot create providers."""
        self.client.force_authenticate(user=self.ops_user)
        
        response = self.client.post('/api/providers/', {'name': 'NewProvider'})
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_ops_cannot_update_provider(self):
        """Test that Ops cannot update providers."""
        self.client.force_authenticate(user=self.ops_user)
        
        response = self.client.put(f'/api/providers/{self.provider.id}/', {'name': 'UpdatedProvider'})
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_ops_cannot_delete_provider(self):
        """Test that Ops cannot delete providers."""
        self.client.force_authenticate(user=self.ops_user)
        
        response = self.client.delete(f'/api/providers/{self.provider.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_ceo_can_create_provider(self):
        """Test that CEO can create providers."""
        self.client.force_authenticate(user=self.ceo_user)
        
        response = self.client.post('/api/providers/', {'name': 'NewProvider'})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_sales_can_create_provider(self):
        """Test that Sales can create providers."""
        self.client.force_authenticate(user=self.sales_user)
        
        response = self.client.post('/api/providers/', {'name': 'SalesProvider'})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_proqual_can_create_provider(self):
        """Test that ProQualAdmin can create providers."""
        self.client.force_authenticate(user=self.proqual_user)
        
        response = self.client.post('/api/providers/', {'name': 'ProQualProvider'})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class HRAndFinanceRoleTests(TestCase):
    """Tests for HR and Finance role functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        
        # Create users with different roles
        self.hr_user = CustomUser.objects.create_user(
            username="hruser",
            password="testpass123",
            role="HR"
        )
        self.finance_user = CustomUser.objects.create_user(
            username="financeuser",
            password="testpass123",
            role="Finance"
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
        self.ceo_user = CustomUser.objects.create_user(
            username="ceouser",
            password="testpass123",
            role="CEO"
        )
        
        # Create test data for finance calculations
        self.provider = CourseProvider.objects.create(name="OTHM")
        self.field = Field.objects.create(name="OHS", provider=self.provider)
        self.level = Level.objects.create(number=5)
        self.student = Student.objects.create(
            name="Test Student",
            email="test@example.com",
            phone="1234567890",
            dob="1990-01-01"
        )
        self.registration = Registration.objects.create(
            student=self.student,
            provider=self.provider,
            field=self.field,
            level=self.level,
            registered_by=self.sales_user,
            total_fee=Decimal("1000.00")
        )
    
    def test_hr_user_can_access_hr_dashboard(self):
        """Test that HR user can access HR dashboard."""
        self.client.force_authenticate(user=self.hr_user)
        
        response = self.client.get('/api/dashboard/hr/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_users', response.data)
        self.assertIn('active_users', response.data)
        self.assertIn('inactive_users', response.data)
        self.assertIn('role_breakdown', response.data)
    
    def test_non_hr_user_cannot_access_hr_dashboard(self):
        """Test that non-HR users cannot access HR dashboard."""
        self.client.force_authenticate(user=self.sales_user)
        
        response = self.client.get('/api/dashboard/hr/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_finance_user_can_access_finance_dashboard(self):
        """Test that Finance user can access Finance dashboard."""
        self.client.force_authenticate(user=self.finance_user)
        
        response = self.client.get('/api/dashboard/finance/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('revenue_expected', response.data)
        self.assertIn('revenue_collected', response.data)
        self.assertIn('revenue_pending', response.data)
        self.assertIn('overdue_payments_count', response.data)
        self.assertIn('total_incentive_liabilities', response.data)
    
    def test_non_finance_user_cannot_access_finance_dashboard(self):
        """Test that non-Finance users cannot access Finance dashboard."""
        self.client.force_authenticate(user=self.sales_user)
        
        response = self.client.get('/api/dashboard/finance/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_hr_summary_returns_correct_user_stats(self):
        """Test that HR summary returns correct user statistics."""
        from .dashboard import get_hr_summary
        
        data = get_hr_summary()
        
        # Should have 5 users (hr, finance, sales, ops, ceo)
        self.assertEqual(data['total_users'], 5)
        self.assertEqual(data['active_users'], 5)
        self.assertEqual(data['inactive_users'], 0)
        
        # Check role breakdown
        self.assertIn('HR', data['role_breakdown'])
        self.assertIn('Finance', data['role_breakdown'])
        self.assertEqual(data['role_breakdown']['HR']['count'], 1)
        self.assertEqual(data['role_breakdown']['Finance']['count'], 1)
    
    def test_finance_summary_returns_correct_revenue_stats(self):
        """Test that Finance summary returns correct financial statistics."""
        from .dashboard import get_finance_summary
        
        data = get_finance_summary()
        
        # Should have revenue expected from the registration
        self.assertGreaterEqual(data['revenue_expected'], 1000.0)
        self.assertEqual(data['revenue_collected'], 0.0)  # No payments made yet
        self.assertGreaterEqual(data['revenue_pending'], 1000.0)
    
    def test_finance_user_can_create_provider(self):
        """Test that Finance user can create providers (write operations)."""
        self.client.force_authenticate(user=self.finance_user)
        
        response = self.client.post('/api/providers/', {'name': 'FinanceProvider'})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_finance_user_can_update_provider(self):
        """Test that Finance user can update providers."""
        self.client.force_authenticate(user=self.finance_user)
        
        response = self.client.put(f'/api/providers/{self.provider.id}/', {'name': 'UpdatedProvider'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProQualRegistrationLogicTests(TestCase):
    """Tests for ProQual registration logic updates."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        
        # Create users
        self.sales_user = CustomUser.objects.create_user(
            username="salesuser",
            password="testpass123",
            role="Sales"
        )
        self.ops_user = CustomUser.objects.create_user(
            username="opsuser",
            password="testpass123",
            role="Ops",
            is_active=True
        )
        
        # Create ProQual provider
        self.proqual_provider = CourseProvider.objects.create(name="ProQual")
        self.othm_provider = CourseProvider.objects.create(name="OTHM")
        self.field = Field.objects.create(name="Business", provider=self.proqual_provider)
        self.othm_field = Field.objects.create(name="OHS", provider=self.othm_provider)
        self.level = Level.objects.create(number=5)
        
        self.student = Student.objects.create(
            name="ProQual Student",
            email="proqual@example.com",
            phone="1234567890",
            dob="1995-01-01"
        )
    
    def test_proqual_registration_not_auto_assigned(self):
        """Test that ProQual registrations are not auto-assigned via round-robin."""
        self.client.force_authenticate(user=self.sales_user)
        
        registration_data = {
            'student': self.student.id,
            'provider': self.proqual_provider.id,
            'field': self.field.id,
            'level': self.level.id,
            'total_fee': '1000.00',
            'upfront_payment_percent': 50,
            'remaining_months': 2,
        }
        
        response = self.client.post('/api/registrations/', registration_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify that assigned_to is None
        registration = Registration.objects.get(id=response.data['id'])
        self.assertIsNone(registration.assigned_to)
    
    def test_non_proqual_registration_is_auto_assigned(self):
        """Test that non-ProQual registrations are auto-assigned via round-robin."""
        self.client.force_authenticate(user=self.sales_user)
        
        registration_data = {
            'student': self.student.id,
            'provider': self.othm_provider.id,
            'field': self.othm_field.id,
            'level': self.level.id,
            'total_fee': '1000.00',
            'upfront_payment_percent': 50,
            'remaining_months': 2,
        }
        
        response = self.client.post('/api/registrations/', registration_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify that assigned_to is set (should be ops_user via round-robin)
        registration = Registration.objects.get(id=response.data['id'])
        self.assertIsNotNone(registration.assigned_to)
        self.assertEqual(registration.assigned_to.role, 'Ops')
    
    def test_proqual_registration_explicit_assignment_is_ignored(self):
        """Test that explicit assignment in ProQual registration is ignored."""
        self.client.force_authenticate(user=self.sales_user)
        
        registration_data = {
            'student': self.student.id,
            'provider': self.proqual_provider.id,
            'field': self.field.id,
            'level': self.level.id,
            'total_fee': '1000.00',
            'upfront_payment_percent': 50,
            'remaining_months': 2,
            'assigned_to': self.ops_user.id,  # Explicitly try to assign
        }
        
        response = self.client.post('/api/registrations/', registration_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify that assigned_to is still None (explicit assignment ignored for ProQual)
        registration = Registration.objects.get(id=response.data['id'])
        self.assertIsNone(registration.assigned_to)
