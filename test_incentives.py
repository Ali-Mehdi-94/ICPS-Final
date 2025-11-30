"""
Test script for Sales and Ops Incentives
"""
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ICPS.settings')
django.setup()

from core.models import (
    CustomUser, CourseProvider, Student, Field, Level, Registration,
    PaymentPlan, PaymentInstallment, UnitTask, SalesIncentive, OperationsIncentive
)
from django.utils import timezone

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def main():
    print("\n" + "="*60)
    print("  INCENTIVE SYSTEM TEST SUITE")
    print("="*60)
    
    # Setup test data
    print_section("SETUP: Getting Test Data")
    try:
        sales_user = CustomUser.objects.filter(role="Sales").first()
        ops_user = CustomUser.objects.filter(role="Ops").first()
        student = Student.objects.first()
        provider = CourseProvider.objects.filter(name__iexact="OTHM").first()
        if not provider:
            provider = CourseProvider.objects.first()
        field = Field.objects.filter(provider=provider).first()
        if not field:
            field = Field.objects.create(name="Test Field", provider=provider)
        level = Level.objects.first()
        
        print(f"✓ Sales user: {sales_user.username if sales_user else 'None'}")
        print(f"✓ Ops user: {ops_user.username if ops_user else 'None'}")
        print(f"✓ Student: {student.name if student else 'None'}")
        print(f"✓ Provider: {provider.name if provider else 'None'}")
        
        if not sales_user or not ops_user or not student or not provider:
            print("✗ Missing required test data!")
            return
    except Exception as e:
        print(f"✗ Setup failed: {str(e)}")
        return
    
    # TEST 1: Create Registration for Sales Incentive Test
    print_section("TEST 1: Create Registration for Sales Incentive")
    try:
        reg_sales = Registration.objects.create(
            student=student,
            provider=provider,
            field=field,
            level=level,
            qualification_type="diploma",
            total_fee=5000.00,
            upfront_payment_percent=50,
            remaining_months=2,
            registered_by=sales_user,
            assigned_to=ops_user,
            deadline_date=date.today() + timedelta(days=120)
        )
        print(f"✓ Registration created: ID {reg_sales.id}")
        print(f"  Registered by: {reg_sales.registered_by.username}")
        print(f"  Total fee: {reg_sales.total_fee}")
        print(f"  Sales incentive paid: {reg_sales.sales_incentive_paid}")
        print(f"  Ops incentive paid: {reg_sales.ops_incentive_paid}")
    except Exception as e:
        print(f"✗ Registration creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # TEST 2: Check Payment Plan Creation
    print_section("TEST 2: Check Payment Plan Creation")
    try:
        # Payment plan should be created by signal
        if hasattr(reg_sales, 'payment_plan'):
            plan = reg_sales.payment_plan
            installments = plan.installments.all()
            print(f"✓ Payment plan exists")
            print(f"  Total fee: {plan.total_fee}")
            print(f"  Installments: {installments.count()}")
            for inst in installments:
                print(f"    - Seq {inst.sequence}: {inst.amount} (Due: {inst.due_date}, Paid: {inst.paid_at})")
        else:
            print("✗ Payment plan not created!")
            return
    except Exception as e:
        print(f"✗ Payment plan check failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # TEST 3: Test Sales Incentive - Mark All Payments as Paid
    print_section("TEST 3: Sales Incentive - Mark All Payments as Paid")
    try:
        plan = reg_sales.payment_plan
        installments = plan.installments.all()
        
        print(f"  Marking {installments.count()} installments as paid...")
        for inst in installments:
            if not inst.paid_at:
                inst.paid_at = date.today()
                inst.save()
                print(f"    ✓ Marked installment {inst.sequence} as paid")
        
        # Check if fully paid
        is_fully_paid = reg_sales.is_fully_paid()
        print(f"  Is fully paid: {is_fully_paid}")
        
        # Manually trigger incentive update
        reg_sales.update_sales_incentive_status()
        
        # Refresh from DB
        reg_sales.refresh_from_db()
        
        print(f"  Sales incentive paid status: {reg_sales.sales_incentive_paid}")
        
        # Check SalesIncentive record
        if hasattr(reg_sales, 'sales_incentive'):
            incentive = reg_sales.sales_incentive
            print(f"✓ Sales incentive record exists!")
            print(f"  Amount: {incentive.amount}")
            print(f"  Paid: {incentive.paid}")
            print(f"  Paid at: {incentive.paid_at}")
            print(f"  Sales person: {incentive.sales_person.username if incentive.sales_person else 'None'}")
        else:
            print("✗ Sales incentive record not found!")
    except Exception as e:
        print(f"✗ Sales incentive test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # TEST 4: Create Registration for Ops Incentive Test
    print_section("TEST 4: Create Registration for Ops Incentive")
    try:
        reg_ops = Registration.objects.create(
            student=student,
            provider=provider,
            field=field,
            level=level,
            qualification_type="diploma",
            total_fee=5000.00,
            upfront_payment_percent=50,
            remaining_months=2,
            registered_by=sales_user,
            assigned_to=ops_user,
            deadline_date=date.today() + timedelta(days=120)
        )
        print(f"✓ Registration created: ID {reg_ops.id}")
        print(f"  Assigned to: {reg_ops.assigned_to.username}")
        print(f"  Deadline: {reg_ops.deadline_date}")
        
        # Check if tasks were created
        tasks_count = reg_ops.tasks.count()
        print(f"  Tasks created: {tasks_count}")
        
        if tasks_count == 0:
            print("  ⚠ No tasks created - may need program template")
    except Exception as e:
        print(f"✗ Registration creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # TEST 5: Test Ops Incentive - Complete All Assignment Units Before Deadline
    print_section("TEST 5: Ops Incentive - Complete All Assignment Units")
    try:
        # Get assignment tasks (phase="Assignments")
        assignment_tasks = reg_ops.tasks.filter(phase="Assignments")
        print(f"  Assignment tasks found: {assignment_tasks.count()}")
        
        if assignment_tasks.count() == 0:
            print("  ⚠ No assignment tasks - creating test tasks...")
            # Create some test assignment tasks
            for i in range(1, 4):
                UnitTask.objects.create(
                    registration=reg_ops,
                    week_index=i,
                    phase="Assignments",
                    label=f"Unit {i}",
                    unit_number=i,
                    due_date=date.today() - timedelta(days=1),  # Due yesterday (before deadline)
                    assigned_to=ops_user,
                    status="PENDING"
                )
            assignment_tasks = reg_ops.tasks.filter(phase="Assignments")
            print(f"  Created {assignment_tasks.count()} test assignment tasks")
        
        # Complete all assignment tasks
        print(f"  Completing {assignment_tasks.count()} assignment tasks...")
        for task in assignment_tasks:
            task.status = "DONE"
            task.completed_at = timezone.now()
            task.save()
            print(f"    ✓ Completed task: {task.label}")
        
        # Refresh registration
        reg_ops.refresh_from_db()
        
        # Check if coursework completed on time
        is_completed_on_time = reg_ops.is_coursework_completed_on_time()
        print(f"  Is coursework completed on time: {is_completed_on_time}")
        print(f"  Units total: {reg_ops.units_total}")
        print(f"  Units done: {reg_ops.units_done}")
        print(f"  Deadline: {reg_ops.deadline_date}")
        
        # Manually trigger incentive update
        reg_ops.update_ops_incentive_status()
        
        # Refresh from DB
        reg_ops.refresh_from_db()
        
        print(f"  Ops incentive paid status: {reg_ops.ops_incentive_paid}")
        
        # Check OperationsIncentive record
        if hasattr(reg_ops, 'ops_incentive'):
            incentive = reg_ops.ops_incentive
            print(f"✓ Ops incentive record exists!")
            print(f"  Amount: {incentive.amount}")
            print(f"  Paid: {incentive.paid}")
            print(f"  Paid at: {incentive.paid_at}")
            print(f"  Completed on time: {incentive.completed_on_time}")
            print(f"  Ops person: {incentive.ops_person.username if incentive.ops_person else 'None'}")
        else:
            print("✗ Ops incentive record not found!")
    except Exception as e:
        print(f"✗ Ops incentive test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # TEST 6: Test Automatic Updates via API Actions
    print_section("TEST 6: Test Automatic Updates via API Actions")
    try:
        # Create another registration
        reg_auto = Registration.objects.create(
            student=student,
            provider=provider,
            field=field,
            level=level,
            qualification_type="diploma",
            total_fee=3000.00,
            upfront_payment_percent=50,
            remaining_months=1,
            registered_by=sales_user,
            assigned_to=ops_user,
            deadline_date=date.today() + timedelta(days=60)
        )
        
        print(f"✓ Test registration created: ID {reg_auto.id}")
        
        # Test: Mark payment via InstallmentPayView logic
        if hasattr(reg_auto, 'payment_plan'):
            plan = reg_auto.payment_plan
            installments = plan.installments.all()
            
            # Mark all as paid
            for inst in installments:
                inst.paid_at = date.today()
                inst.save()
            
            # Trigger update
            reg_auto.update_sales_incentive_status()
            reg_auto.refresh_from_db()
            
            print(f"  After marking all payments:")
            print(f"    Sales incentive paid: {reg_auto.sales_incentive_paid}")
            if hasattr(reg_auto, 'sales_incentive'):
                print(f"    Incentive record paid: {reg_auto.sales_incentive.paid}")
        
        # Test: Complete task via UnitTaskCompleteView logic
        assignment_tasks = reg_auto.tasks.filter(phase="Assignments")
        if assignment_tasks.count() == 0:
            # Create test task
            task = UnitTask.objects.create(
                registration=reg_auto,
                week_index=1,
                phase="Assignments",
                label="Unit 1",
                unit_number=1,
                due_date=date.today() - timedelta(days=1),
                assigned_to=ops_user,
                status="PENDING"
            )
            assignment_tasks = [task]
        
        # Complete task
        for task in assignment_tasks:
            task.status = "DONE"
            task.completed_at = timezone.now()
            task.save()
            # Trigger update (as done in UnitTaskCompleteView)
            reg_auto.update_ops_incentive_status()
        
        reg_auto.refresh_from_db()
        print(f"  After completing all tasks:")
        print(f"    Ops incentive paid: {reg_auto.ops_incentive_paid}")
        if hasattr(reg_auto, 'ops_incentive'):
            print(f"    Incentive record paid: {reg_auto.ops_incentive.paid}")
            print(f"    Completed on time: {reg_auto.ops_incentive.completed_on_time}")
    except Exception as e:
        print(f"✗ Automatic update test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # TEST 7: Summary of All Incentives
    print_section("TEST 7: Summary of All Incentives")
    try:
        sales_incentives = SalesIncentive.objects.all()
        ops_incentives = OperationsIncentive.objects.all()
        
        print(f"Total Sales Incentives: {sales_incentives.count()}")
        for inc in sales_incentives:
            print(f"  - Reg {inc.registration_id}: {inc.sales_person.username if inc.sales_person else 'None'} - Paid: {inc.paid} - Amount: {inc.amount}")
        
        print(f"\nTotal Ops Incentives: {ops_incentives.count()}")
        for inc in ops_incentives:
            print(f"  - Reg {inc.registration_id}: {inc.ops_person.username if inc.ops_person else 'None'} - Paid: {inc.paid} - On Time: {inc.completed_on_time} - Amount: {inc.amount}")
    except Exception as e:
        print(f"✗ Summary failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("  ALL INCENTIVE TESTS COMPLETED")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

