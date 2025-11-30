# ProQual Separation & Changes Implementation

## Summary of Changes

This document outlines all the changes made to separate ProQual from other course providers and implement the new ProQual admin dashboard.

## 1. Model Changes

### CustomUser Model
- **Added new role**: `ProQualAdmin` role choice
- **Updated max_length**: Changed from 10 to 15 to accommodate "ProQualAdmin"

### Registration Model
- **Added field**: `portal_allotment_date` (DateField, nullable)
  - Purpose: For ProQual registrations, this date marks when the portal was allocated
  - Timeline starts from this date (not registration date)
- **Added property**: `is_proqual` - Helper property to check if registration is for ProQual

## 2. Permissions

### New Permission Class
- **IsProQualAdmin**: Permission class for ProQual admin role
- Location: `core/permissions.py`

## 3. Business Logic Changes

### Round-Robin Assignment
- **Modified**: `RegistrationViewSet.perform_create()`
- **Change**: ProQual registrations are **NOT** auto-assigned via round-robin
- **Behavior**: ProQual registrations are created with `assigned_to=None` and require manual assignment

### Task Creation Logic
- **Modified**: `create_units_for_registration()` in `core/services.py`
- **ProQual Forms Timeline**:
  - **Before**: 8 weeks of forms
  - **After**: 1 week forms + 7 weeks buffer period
- **Timeline Start**:
  - **ProQual**: Uses `portal_allotment_date` if set, otherwise tasks are not created
  - **Other Providers**: Uses current date
- **Behavior**: ProQual tasks are only created after `portal_allotment_date` is set

### Signal Handler
- **Modified**: `registration_post_save` signal in `core/signals.py`
- **Change**: For ProQual, tasks are only created if `portal_allotment_date` is set

## 4. ProQual Admin Dashboard

### Dashboard Summary Function
- **New Function**: `get_proqual_admin_summary()` in `core/dashboard.py`
- **Returns**:
  - Total ProQual registrations
  - Registrations pending portal allocation
  - Registrations pending ops assignment
  - Active registrations
  - Completed registrations
  - Average progress percentage
  - Total overdue units
  - Ops team performance metrics

### API Endpoints

#### Dashboard
- **GET** `/api/dashboard/proqual/summary/`
  - Returns ProQual admin dashboard summary
  - Requires: ProQualAdmin role

#### Registrations Management
- **GET** `/api/proqual/registrations/` - List all ProQual registrations
- **POST** `/api/proqual/registrations/` - Create new ProQual registration
- **GET** `/api/proqual/registrations/{id}/` - Get ProQual registration details
- **PUT/PATCH** `/api/proqual/registrations/{id}/` - Update ProQual registration
- **DELETE** `/api/proqual/registrations/{id}/` - Delete ProQual registration
  - All require: ProQualAdmin role

#### Ops Assignment
- **POST** `/api/proqual/registrations/{id}/assign-ops/`
  - Manually assign Ops team member to ProQual registration
  - Request body: `{"ops_user_id": <user_id>}`
  - Requires: ProQualAdmin role
  - If portal date is set, regenerates tasks with new assignment

#### Portal Date Setting
- **POST** `/api/proqual/registrations/{id}/set-portal-date/`
  - Set portal allotment date and start 32-week timeline
  - Request body: `{"portal_allotment_date": "YYYY-MM-DD"}`
  - Requires: ProQualAdmin role
  - Automatically creates task timeline starting from portal date

#### Ops List
- **GET** `/api/proqual/ops-list/`
  - Get list of all active Ops team members
  - Returns: List of Ops users with id, username, email
  - Requires: ProQualAdmin role

## 5. Serializer Updates

### RegistrationSerializer
- **Added field**: `portal_allotment_date` to serializer fields
- Location: `core/serializers.py`

## 6. Workflow Changes

### ProQual Registration Workflow

1. **Create Registration** (ProQual Admin)
   - ProQual admin creates registration via `/api/proqual/registrations/`
   - Registration is created with `assigned_to=None`
   - No tasks are created yet

2. **Set Portal Date** (ProQual Admin)
   - 2-3 days later, ProQual admin sets portal date via `/api/proqual/registrations/{id}/set-portal-date/`
   - This triggers task creation with timeline starting from portal date
   - Timeline: 1 week forms + 7 weeks buffer + units + assessment/buffer

3. **Assign Ops Team** (ProQual Admin)
   - ProQual admin assigns Ops team member via `/api/proqual/registrations/{id}/assign-ops/`
   - Can be done before or after portal date is set
   - If portal date is already set, tasks are regenerated with new assignment

4. **Review Progress** (ProQual Admin)
   - ProQual admin can view dashboard at `/api/dashboard/proqual/summary/`
   - Can review individual registrations and Ops team performance

## 7. Timeline Structure

### ProQual Timeline (32 weeks total)
- **Week 1**: Forms & Documentation
- **Weeks 2-8**: Buffer Period (7 weeks)
- **Weeks 9+**: Assignment Units (based on unit_count)
- **Final 2 weeks**: Assessment & Resubmissions

### Other Providers (OTHM, etc.)
- No changes to timeline structure
- Still use round-robin assignment
- Timeline starts from registration date

## 8. Database Migration Required

After these changes, you need to run:

```bash
python manage.py makemigrations
python manage.py migrate
```

This will:
- Add `portal_allotment_date` field to Registration model
- Update CustomUser role field max_length

## 9. Testing Checklist

- [ ] Create ProQual admin user with role="ProQualAdmin"
- [ ] Create ProQual registration (should not auto-assign)
- [ ] Set portal_allotment_date (should create tasks)
- [ ] Assign Ops team member (should update tasks)
- [ ] Verify timeline starts from portal date
- [ ] Verify forms are 1 week, buffer is 7 weeks
- [ ] Test ProQual admin dashboard
- [ ] Verify other providers still use round-robin
- [ ] Test all ProQual admin endpoints

## 10. API Usage Examples

### Create ProQual Registration
```http
POST /api/proqual/registrations/
Authorization: Bearer <token>
Content-Type: application/json

{
  "student": 1,
  "provider": 2,  # ProQual
  "field": 1,
  "level": 1,
  "qualification_type": "diploma",
  "total_fee": 5000.00,
  "upfront_payment_percent": 50,
  "remaining_months": 2
}
```

### Set Portal Date
```http
POST /api/proqual/registrations/1/set-portal-date/
Authorization: Bearer <token>
Content-Type: application/json

{
  "portal_allotment_date": "2024-01-15"
}
```

### Assign Ops Team
```http
POST /api/proqual/registrations/1/assign-ops/
Authorization: Bearer <token>
Content-Type: application/json

{
  "ops_user_id": 5
}
```

### Get Dashboard Summary
```http
GET /api/dashboard/proqual/summary/
Authorization: Bearer <token>
```

## Notes

- ProQual registrations require manual Ops assignment (no round-robin)
- Timeline only starts after portal_allotment_date is set
- Forms phase is now 1 week (was 8 weeks)
- Buffer period is 7 weeks (was 0, now separate from forms)
- All ProQual operations require ProQualAdmin role

