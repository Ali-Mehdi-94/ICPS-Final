"""
Test script for the notification system.
This script tests all notification functions to ensure they work correctly.
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ICPS.settings')
django.setup()

from core.models import Registration, UnitTask, PaymentInstallment, CustomUser, CourseProvider, Student
from core.notifications import (
    notify_proqual_ops_assigned,
    notify_proqual_portal_allotted,
    notify_proqual_unit_due,
    notify_proqual_unit_completed,
    notify_ceo_unit_completed,
    notify_ops_unit_due,
    notify_payment_due,
)
from django.utils import timezone
from datetime import timedelta

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_proqual_notifications():
    """Test ProQual-specific notifications"""
    print_section("TEST: ProQual Notifications")
    
    # Get ProQual provider
    try:
        proqual_provider = CourseProvider.objects.get(name__iexact="ProQual")
    except CourseProvider.DoesNotExist:
        print("⚠ ProQual provider not found. Skipping ProQual tests.")
        return
    
    # Get a ProQual registration
    proqual_reg = Registration.objects.filter(provider=proqual_provider).first()
    if not proqual_reg:
        print("⚠ No ProQual registrations found. Skipping ProQual tests.")
        return
    
    print(f"✓ Testing with ProQual registration ID: {proqual_reg.id}")
    
    # Test 1: Ops assignment notification
    if proqual_reg.assigned_to:
        print("\n1. Testing notify_proqual_ops_assigned...")
        try:
            notify_proqual_ops_assigned(proqual_reg)
            print("   ✓ Notification sent successfully")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
    else:
        print("\n1. Skipping ops_assigned (no assigned_to)")
    
    # Test 2: Portal allotment notification
    if proqual_reg.portal_allotment_date:
        print("\n2. Testing notify_proqual_portal_allotted...")
        try:
            notify_proqual_portal_allotted(proqual_reg)
            print("   ✓ Notification sent successfully")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
    else:
        print("\n2. Skipping portal_allotted (no portal_allotment_date)")
    
    # Test 3: Unit due notification
    proqual_task = UnitTask.objects.filter(registration=proqual_reg, status="PENDING").first()
    if proqual_task:
        print("\n3. Testing notify_proqual_unit_due...")
        try:
            notify_proqual_unit_due(proqual_task)
            print("   ✓ Notification sent successfully")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
    else:
        print("\n3. Skipping unit_due (no pending tasks)")
    
    # Test 4: Unit completed notification
    proqual_completed_task = UnitTask.objects.filter(registration=proqual_reg, status="DONE").first()
    if proqual_completed_task:
        print("\n4. Testing notify_proqual_unit_completed...")
        try:
            notify_proqual_unit_completed(proqual_completed_task)
            print("   ✓ Notification sent successfully")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
    else:
        print("\n4. Skipping unit_completed (no completed tasks)")

def test_other_provider_notifications():
    """Test notifications for other providers"""
    print_section("TEST: Other Provider Notifications")
    
    # Get a non-ProQual registration
    try:
        proqual_provider = CourseProvider.objects.get(name__iexact="ProQual")
        other_reg = Registration.objects.exclude(provider=proqual_provider).first()
    except CourseProvider.DoesNotExist:
        other_reg = Registration.objects.first()
    
    if not other_reg:
        print("⚠ No non-ProQual registrations found. Skipping tests.")
        return
    
    print(f"✓ Testing with registration ID: {other_reg.id} (Provider: {other_reg.provider.name})")
    
    # Test 1: CEO unit completed notification
    completed_task = UnitTask.objects.filter(registration=other_reg, status="DONE").first()
    if completed_task:
        print("\n1. Testing notify_ceo_unit_completed...")
        try:
            notify_ceo_unit_completed(completed_task)
            print("   ✓ Notification sent successfully")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
    else:
        print("\n1. Skipping ceo_unit_completed (no completed tasks)")
    
    # Test 2: Ops unit due notification
    pending_task = UnitTask.objects.filter(registration=other_reg, status="PENDING").first()
    if pending_task:
        print("\n2. Testing notify_ops_unit_due...")
        try:
            notify_ops_unit_due(pending_task)
            print("   ✓ Notification sent successfully")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
    else:
        print("\n2. Skipping ops_unit_due (no pending tasks)")

def test_payment_notifications():
    """Test payment notifications"""
    print_section("TEST: Payment Notifications")
    
    # Get an unpaid installment
    unpaid_installment = PaymentInstallment.objects.filter(paid_at__isnull=True).first()
    if not unpaid_installment:
        print("⚠ No unpaid installments found. Skipping payment tests.")
        return
    
    print(f"✓ Testing with installment ID: {unpaid_installment.id}")
    print(f"  Amount: £{unpaid_installment.amount}")
    print(f"  Due Date: {unpaid_installment.due_date}")
    
    print("\n1. Testing notify_payment_due...")
    try:
        notify_payment_due(unpaid_installment)
        print("   ✓ Notification sent successfully")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")

def test_notification_recipients():
    """Test that notifications have valid recipients"""
    print_section("TEST: Notification Recipients")
    
    # Check ProQual Admin users
    proqual_admins = CustomUser.objects.filter(role="ProQualAdmin", is_active=True)
    print(f"\nProQual Admin users: {proqual_admins.count()}")
    for admin in proqual_admins:
        print(f"  - {admin.username} ({admin.email or 'No email'})")
    
    # Check CEO users
    ceo_users = CustomUser.objects.filter(role="CEO", is_active=True)
    print(f"\nCEO users: {ceo_users.count()}")
    for ceo in ceo_users:
        print(f"  - {ceo.username} ({ceo.email or 'No email'})")
    
    # Check Ops users
    ops_users = CustomUser.objects.filter(role="Ops", is_active=True)
    print(f"\nOps users: {ops_users.count()}")
    for ops in ops_users[:5]:  # Show first 5
        print(f"  - {ops.username} ({ops.email or 'No email'})")
    if ops_users.count() > 5:
        print(f"  ... and {ops_users.count() - 5} more")
    
    # Check Sales users
    sales_users = CustomUser.objects.filter(role="Sales", is_active=True)
    print(f"\nSales users: {sales_users.count()}")
    for sales in sales_users[:5]:  # Show first 5
        print(f"  - {sales.username} ({sales.email or 'No email'})")
    if sales_users.count() > 5:
        print(f"  ... and {sales_users.count() - 5} more")

def main():
    print("\n" + "="*60)
    print("  NOTIFICATION SYSTEM TEST")
    print("="*60)
    
    # Test recipient availability
    test_notification_recipients()
    
    # Test ProQual notifications
    test_proqual_notifications()
    
    # Test other provider notifications
    test_other_provider_notifications()
    
    # Test payment notifications
    test_payment_notifications()
    
    print_section("SUMMARY")
    print("✓ All notification tests completed!")
    print("\nNote: In development mode, emails are sent to console.")
    print("      Check the console output above for email content.")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()

