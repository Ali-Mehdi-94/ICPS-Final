"""
Test script for ProQual features using Django test client
"""
import os
import django
import sys
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ICPS.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.models import CustomUser, CourseProvider, Student, Field, Level, Registration
from rest_framework_simplejwt.tokens import RefreshToken
import json

User = get_user_model()

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def get_auth_token(username, password):
    """Get JWT token for a user"""
    try:
        user = CustomUser.objects.get(username=username)
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    except CustomUser.DoesNotExist:
        return None

def test_authentication():
    """Test 1: Get JWT token for ProQualAdmin"""
    print_section("TEST 1: Authentication - Get JWT Token")
    
    token = get_auth_token("proqual_admin", "testpass123")
    
    if token:
        print(f"✓ Authentication successful!")
        print(f"  Access token: {token[:50]}...")
        return token
    else:
        print(f"✗ Authentication failed: Could not get token")
        return None

def test_dashboard_summary(client, token):
    """Test 2: Get ProQual Admin Dashboard Summary"""
    print_section("TEST 2: ProQual Admin Dashboard Summary")
    
    response = client.get(
        "/api/dashboard/proqual/summary/",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Dashboard summary retrieved successfully!")
        print(f"  Total registrations: {data.get('registrations_total', 0)}")
        print(f"  Pending portal: {data.get('registrations_pending_portal', 0)}")
        print(f"  Pending assignment: {data.get('registrations_pending_assignment', 0)}")
        print(f"  Active registrations: {data.get('registrations_active', 0)}")
        print(f"  Completed: {data.get('registrations_completed', 0)}")
        print(f"  Average progress: {data.get('avg_progress_percent', 0)}%")
        return True
    else:
        print(f"✗ Dashboard summary failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False

def test_ops_list(client, token):
    """Test 3: Get Ops Team List"""
    print_section("TEST 3: Get Ops Team List")
    
    response = client.get(
        "/api/proqual/ops-list/",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )
    
    if response.status_code == 200:
        data = response.json()
        ops_users = data.get("ops_users", [])
        print(f"✓ Ops list retrieved successfully!")
        print(f"  Found {len(ops_users)} Ops team members:")
        for ops in ops_users:
            print(f"    - {ops['username']} (ID: {ops['id']})")
        return ops_users[0]["id"] if ops_users else None
    else:
        print(f"✗ Ops list failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None

def test_create_proqual_registration(client, token):
    """Test 4: Create ProQual Registration"""
    print_section("TEST 4: Create ProQual Registration")
    
    # Get or create test data
    try:
        student = Student.objects.first()
        proqual_provider = CourseProvider.objects.get(name__iexact="ProQual")
        field = Field.objects.filter(provider=proqual_provider).first()
        level = Level.objects.first()
        
        if not field:
            print("  Creating test field...")
            field = Field.objects.create(name="Test Field", provider=proqual_provider)
        
        registration_data = {
            "student": student.id,
            "provider": proqual_provider.id,
            "field": field.id,
            "level": level.id,
            "qualification_type": "diploma",
            "total_fee": "5000.00",
            "upfront_payment_percent": 50,
            "remaining_months": 2
        }
        
        response = client.post(
            "/api/proqual/registrations/",
            data=json.dumps(registration_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            reg_id = data.get("id")
            print(f"✓ ProQual registration created successfully!")
            print(f"  Registration ID: {reg_id}")
            print(f"  Student: {data.get('student_name')}")
            print(f"  Assigned to: {data.get('assigned_to')} (should be None)")
            print(f"  Portal date: {data.get('portal_allotment_date')} (should be None)")
            return reg_id
        else:
            print(f"✗ Registration creation failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None

def test_set_portal_date(client, token, reg_id):
    """Test 5: Set Portal Allotment Date"""
    print_section("TEST 5: Set Portal Allotment Date")
    
    # Set portal date to today
    portal_date = date.today().isoformat()
    
    response = client.post(
        f"/api/proqual/registrations/{reg_id}/set-portal-date/",
        data=json.dumps({"portal_allotment_date": portal_date}),
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Portal date set successfully!")
        print(f"  Portal date: {data.get('portal_allotment_date')}")
        print(f"  Tasks created: {data.get('tasks_created', 0)}")
        return True
    else:
        print(f"✗ Portal date setting failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False

def test_assign_ops(client, token, reg_id, ops_user_id):
    """Test 6: Assign Ops Team Member"""
    print_section("TEST 6: Assign Ops Team Member")
    
    response = client.post(
        f"/api/proqual/registrations/{reg_id}/assign-ops/",
        data=json.dumps({"ops_user_id": ops_user_id}),
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Ops team member assigned successfully!")
        print(f"  Assigned to: {data.get('assigned_to_username')} (ID: {data.get('assigned_to')})")
        return True
    else:
        print(f"✗ Ops assignment failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False

def test_get_registration(client, token, reg_id):
    """Test 7: Get Registration Details"""
    print_section("TEST 7: Get Registration Details")
    
    response = client.get(
        f"/api/proqual/registrations/{reg_id}/",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Registration details retrieved!")
        print(f"  Student: {data.get('student_name')}")
        print(f"  Provider: {data.get('provider_name')}")
        print(f"  Portal date: {data.get('portal_allotment_date')}")
        print(f"  Assigned to: {data.get('assigned_to')}")
        print(f"  Units total: {data.get('units_total', 0)}")
        print(f"  Units done: {data.get('units_done', 0)}")
        print(f"  Progress: {data.get('unit_progress_percent', 0)}%")
        print(f"  Tasks count: {len(data.get('tasks', []))}")
        if data.get('tasks'):
            print(f"  First few tasks:")
            for task in data.get('tasks', [])[:5]:
                print(f"    - Week {task.get('week_index')}: {task.get('label')} ({task.get('phase')}) - Due: {task.get('due_date')}")
        return True
    else:
        print(f"✗ Get registration failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False

def main():
    print("\n" + "="*60)
    print("  PROQUAL FEATURES TEST SUITE")
    print("="*60)
    
    client = Client()
    
    # Test 1: Authentication
    token = test_authentication()
    if not token:
        print("\n✗ Cannot proceed without authentication token!")
        return
    
    # Test 2: Dashboard Summary
    test_dashboard_summary(client, token)
    
    # Test 3: Get Ops List
    ops_user_id = test_ops_list(client, token)
    if not ops_user_id:
        print("\n✗ Cannot proceed without Ops team members!")
        return
    
    # Test 4: Create ProQual Registration
    reg_id = test_create_proqual_registration(client, token)
    if not reg_id:
        print("\n✗ Cannot proceed without registration!")
        return
    
    # Test 5: Set Portal Date
    test_set_portal_date(client, token, reg_id)
    
    # Test 6: Assign Ops
    test_assign_ops(client, token, reg_id, ops_user_id)
    
    # Test 7: Get Registration Details
    test_get_registration(client, token, reg_id)
    
    # Final Dashboard Check
    print_section("FINAL: Dashboard Summary After Changes")
    test_dashboard_summary(client, token)
    
    print("\n" + "="*60)
    print("  ALL TESTS COMPLETED")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
