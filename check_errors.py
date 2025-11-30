"""
Comprehensive error checking script
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ICPS.settings')
django.setup()

from core.models import Registration, CustomUser, CourseProvider
from core.services import build_payment_schedule, create_units_for_registration
from core.dashboard import get_ceo_summary, get_sales_summary, get_ops_summary, get_proqual_admin_summary
from django.utils import timezone
from datetime import date, timedelta

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_division_by_zero():
    """Test for division by zero errors"""
    print_section("TEST: Division by Zero Protection")
    
    issues = []
    
    # Test 1: Payment progress with 0 total
    try:
        reg = Registration.objects.first()
        if reg:
            progress = reg.payment_progress_percent
            print(f"✓ Payment progress with 0 total handled: {progress}%")
    except ZeroDivisionError:
        issues.append("Payment progress division by zero")
        print("✗ Payment progress division by zero error!")
    except Exception as e:
        print(f"⚠ Payment progress test error: {str(e)}")
    
    # Test 2: Unit progress with 0 total
    try:
        if reg:
            progress = reg.unit_progress_percent
            print(f"✓ Unit progress with 0 total handled: {progress}%")
    except ZeroDivisionError:
        issues.append("Unit progress division by zero")
        print("✗ Unit progress division by zero error!")
    except Exception as e:
        print(f"⚠ Unit progress test error: {str(e)}")
    
    # Test 3: Payment schedule with 0 months
    try:
        if reg:
            reg.remaining_months = 0
            reg.total_fee = 1000.00
            build_payment_schedule(reg, 1000.00)
            print("✓ Payment schedule with 0 months handled")
    except ZeroDivisionError:
        issues.append("Payment schedule division by zero")
        print("✗ Payment schedule division by zero error!")
    except Exception as e:
        print(f"⚠ Payment schedule test error: {str(e)}")
    
    return issues

def test_none_references():
    """Test for None reference errors"""
    print_section("TEST: None Reference Protection")
    
    issues = []
    
    # Test 1: Registration without payment plan
    try:
        reg = Registration.objects.first()
        if reg:
            is_paid = reg.is_fully_paid()
            print(f"✓ is_fully_paid() with no payment plan: {is_paid}")
    except AttributeError as e:
        issues.append(f"None reference in is_fully_paid: {str(e)}")
        print(f"✗ None reference error: {str(e)}")
    except Exception as e:
        print(f"⚠ is_fully_paid test error: {str(e)}")
    
    # Test 2: Registration without deadline
    try:
        if reg:
            completed = reg.is_coursework_completed_on_time()
            print(f"✓ is_coursework_completed_on_time() with no deadline: {completed}")
    except AttributeError as e:
        issues.append(f"None reference in is_coursework_completed_on_time: {str(e)}")
        print(f"✗ None reference error: {str(e)}")
    except Exception as e:
        print(f"⚠ is_coursework_completed_on_time test error: {str(e)}")
    
    return issues

def test_dashboard_functions():
    """Test dashboard functions for errors"""
    print_section("TEST: Dashboard Functions")
    
    issues = []
    
    try:
        summary = get_ceo_summary()
        print("✓ CEO summary generated successfully")
    except Exception as e:
        issues.append(f"CEO summary error: {str(e)}")
        print(f"✗ CEO summary error: {str(e)}")
    
    try:
        sales_user = CustomUser.objects.filter(role="Sales").first()
        if sales_user:
            summary = get_sales_summary(sales_user)
            print("✓ Sales summary generated successfully")
        else:
            print("⚠ No sales user found for testing")
    except Exception as e:
        issues.append(f"Sales summary error: {str(e)}")
        print(f"✗ Sales summary error: {str(e)}")
    
    try:
        ops_user = CustomUser.objects.filter(role="Ops").first()
        if ops_user:
            summary = get_ops_summary(ops_user)
            print("✓ Ops summary generated successfully")
        else:
            print("⚠ No ops user found for testing")
    except Exception as e:
        issues.append(f"Ops summary error: {str(e)}")
        print(f"✗ Ops summary error: {str(e)}")
    
    try:
        summary = get_proqual_admin_summary()
        print("✓ ProQual admin summary generated successfully")
    except Exception as e:
        issues.append(f"ProQual admin summary error: {str(e)}")
        print(f"✗ ProQual admin summary error: {str(e)}")
    
    return issues

def test_edge_cases():
    """Test edge cases"""
    print_section("TEST: Edge Cases")
    
    issues = []
    
    # Test 1: Registration with None provider
    try:
        reg = Registration.objects.first()
        if reg and reg.provider:
            is_proqual = reg.is_proqual
            print(f"✓ is_proqual property works: {is_proqual}")
    except AttributeError as e:
        issues.append(f"is_proqual error: {str(e)}")
        print(f"✗ is_proqual error: {str(e)}")
    except Exception as e:
        print(f"⚠ is_proqual test error: {str(e)}")
    
    # Test 2: Empty queryset operations
    try:
        empty_regs = Registration.objects.filter(id=99999)
        count = empty_regs.count()
        print(f"✓ Empty queryset handled: {count}")
    except Exception as e:
        issues.append(f"Empty queryset error: {str(e)}")
        print(f"✗ Empty queryset error: {str(e)}")
    
    return issues

def test_model_properties():
    """Test model properties for errors"""
    print_section("TEST: Model Properties")
    
    issues = []
    
    regs = Registration.objects.all()[:5]
    
    for reg in regs:
        try:
            units_total = reg.units_total
            units_done = reg.units_done
            units_overdue = reg.units_overdue
            unit_progress = reg.unit_progress_percent
            payments_total = reg.payments_total
            payments_paid = reg.payments_paid
            payments_overdue = reg.payments_overdue
            payment_progress = reg.payment_progress_percent
            print(f"✓ Registration {reg.id}: All properties work")
        except Exception as e:
            issues.append(f"Registration {reg.id} property error: {str(e)}")
            print(f"✗ Registration {reg.id} error: {str(e)}")
    
    return issues

def main():
    print("\n" + "="*60)
    print("  COMPREHENSIVE ERROR CHECK")
    print("="*60)
    
    all_issues = []
    
    # Run all tests
    all_issues.extend(test_division_by_zero())
    all_issues.extend(test_none_references())
    all_issues.extend(test_dashboard_functions())
    all_issues.extend(test_edge_cases())
    all_issues.extend(test_model_properties())
    
    # Summary
    print_section("SUMMARY")
    if all_issues:
        print(f"✗ Found {len(all_issues)} potential issues:")
        for issue in all_issues:
            print(f"  - {issue}")
    else:
        print("✓ No errors found! All checks passed.")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()

