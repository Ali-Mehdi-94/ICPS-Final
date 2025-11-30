"""
Simple test script for ProQual features
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ICPS.settings')
django.setup()

from core.models import CustomUser, CourseProvider, Student, Field, Level, Registration
from core.dashboard import get_proqual_admin_summary
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def main():
    print("\n" + "="*60)
    print("  PROQUAL FEATURES TEST SUITE")
    print("="*60)
    
    # Test 1: Check ProQualAdmin user exists
    print_section("TEST 1: Check ProQualAdmin User")
    try:
        proqual_admin = CustomUser.objects.get(username="proqual_admin")
        print(f"✓ ProQualAdmin user exists: {proqual_admin.username} (ID: {proqual_admin.id}, Role: {proqual_admin.role})")
        
        # Generate token
        refresh = RefreshToken.for_user(proqual_admin)
        token = str(refresh.access_token)
        print(f"✓ JWT token generated: {token[:50]}...")
    except CustomUser.DoesNotExist:
        print("✗ ProQualAdmin user not found!")
        return
    
    # Test 2: Check ProQual provider
    print_section("TEST 2: Check ProQual Provider")
    try:
        proqual_provider = CourseProvider.objects.get(name__iexact="ProQual")
        print(f"✓ ProQual provider exists: {proqual_provider.name} (ID: {proqual_provider.id})")
    except CourseProvider.DoesNotExist:
        print("✗ ProQual provider not found!")
        return
    
    # Test 3: Check Ops users
    print_section("TEST 3: Check Ops Team Members")
    ops_users = CustomUser.objects.filter(role="Ops", is_active=True)
    print(f"✓ Found {ops_users.count()} Ops team members:")
    for ops in ops_users:
        print(f"    - {ops.username} (ID: {ops.id})")
    
    if ops_users.count() == 0:
        print("✗ No Ops team members found!")
        return
    
    # Test 4: Test Dashboard Summary Function
    print_section("TEST 4: Test Dashboard Summary Function")
    try:
        summary = get_proqual_admin_summary()
        print("✓ Dashboard summary function works!")
        print(f"  Total registrations: {summary.get('registrations_total', 0)}")
        print(f"  Pending portal: {summary.get('registrations_pending_portal', 0)}")
        print(f"  Pending assignment: {summary.get('registrations_pending_assignment', 0)}")
        print(f"  Active: {summary.get('registrations_active', 0)}")
        print(f"  Completed: {summary.get('registrations_completed', 0)}")
    except Exception as e:
        print(f"✗ Dashboard summary failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 5: Create ProQual Registration
    print_section("TEST 5: Create ProQual Registration")
    try:
        student = Student.objects.first()
        field = Field.objects.filter(provider=proqual_provider).first()
        if not field:
            field = Field.objects.create(name="Test Field", provider=proqual_provider)
        level = Level.objects.first()
        
        registration = Registration.objects.create(
            student=student,
            provider=proqual_provider,
            field=field,
            level=level,
            qualification_type="diploma",
            total_fee=5000.00,
            upfront_payment_percent=50,
            remaining_months=2,
            registered_by=proqual_admin,
            assigned_to=None  # ProQual should not auto-assign
        )
        print(f"✓ ProQual registration created!")
        print(f"  Registration ID: {registration.id}")
        print(f"  Student: {registration.student.name}")
        print(f"  Assigned to: {registration.assigned_to} (should be None)")
        print(f"  Portal date: {registration.portal_allotment_date} (should be None)")
        print(f"  Tasks count: {registration.tasks.count()} (should be 0 - no portal date yet)")
    except Exception as e:
        print(f"✗ Registration creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 6: Set Portal Date
    print_section("TEST 6: Set Portal Allotment Date")
    try:
        registration.portal_allotment_date = date.today()
        registration.save()
        
        # Tasks should be created by signal
        from core.services import create_units_for_registration
        create_units_for_registration(registration)
        
        tasks_count = registration.tasks.count()
        print(f"✓ Portal date set successfully!")
        print(f"  Portal date: {registration.portal_allotment_date}")
        print(f"  Tasks created: {tasks_count}")
        
        if tasks_count > 0:
            print(f"  First few tasks:")
            for task in registration.tasks.all()[:5]:
                print(f"    - Week {task.week_index}: {task.label} ({task.phase}) - Due: {task.due_date}")
    except Exception as e:
        print(f"✗ Portal date setting failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 7: Assign Ops Team
    print_section("TEST 7: Assign Ops Team Member")
    try:
        ops_user = ops_users.first()
        registration.assigned_to = ops_user
        registration.save()
        print(f"✓ Ops team member assigned!")
        print(f"  Assigned to: {ops_user.username} (ID: {ops_user.id})")
    except Exception as e:
        print(f"✗ Ops assignment failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 8: Final Dashboard Check
    print_section("TEST 8: Final Dashboard Summary")
    try:
        summary = get_proqual_admin_summary()
        print("✓ Dashboard summary after changes:")
        print(f"  Total registrations: {summary.get('registrations_total', 0)}")
        print(f"  Pending portal: {summary.get('registrations_pending_portal', 0)}")
        print(f"  Pending assignment: {summary.get('registrations_pending_assignment', 0)}")
        print(f"  Active: {summary.get('registrations_active', 0)}")
        print(f"  Completed: {summary.get('registrations_completed', 0)}")
        print(f"  Average progress: {summary.get('avg_progress_percent', 0)}%")
    except Exception as e:
        print(f"✗ Dashboard summary failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("  ALL TESTS COMPLETED")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

