# Email Notification System Documentation

## Overview

The ICPS system now includes a comprehensive email notification system that handles different notification flows for ProQual and other course providers.

## Notification Flows

### ProQual System

1. **Ops Assignment Notification**
   - **Trigger**: When a ProQual student is assigned to an Ops team member
   - **Recipients**: Assigned Ops team member
   - **Function**: `notify_proqual_ops_assigned()`
   - **Location**: Triggered in `ProQualAssignOpsView` (views.py)

2. **Portal Allotment Notification**
   - **Trigger**: When portal allotment date is set for a ProQual registration
   - **Recipients**: Assigned Ops team member + All ProQual Admin users
   - **Function**: `notify_proqual_portal_allotted()`
   - **Location**: Triggered in `ProQualSetPortalDateView` (views.py)

3. **Unit Due Notification**
   - **Trigger**: When a unit is due (within 7 days, due today, or overdue)
   - **Recipients**: Assigned Ops team member + All ProQual Admin users
   - **Function**: `notify_proqual_unit_due()`
   - **Location**: 
     - Signal: `unit_task_post_save` (signals.py) - for immediate notifications
     - Daily command: `notify_ops_pending_and_overdue()` - for scheduled checks

4. **Unit Completed Notification**
   - **Trigger**: When a ProQual unit is marked as completed
   - **Recipients**: All ProQual Admin users
   - **Function**: `notify_proqual_unit_completed()`
   - **Location**: Triggered in `UnitTaskCompleteView` (views.py)

### Other Course Providers

1. **CEO Unit Completed Notification**
   - **Trigger**: When a unit is marked as completed (non-ProQual)
   - **Recipients**: All CEO users
   - **Function**: `notify_ceo_unit_completed()`
   - **Location**: Triggered in `UnitTaskCompleteView` (views.py)

2. **Ops Unit Due Notification**
   - **Trigger**: When a unit is due (within 7 days, due today, or overdue)
   - **Recipients**: Assigned Ops team member
   - **Function**: `notify_ops_unit_due()`
   - **Location**: 
     - Signal: `unit_task_post_save` (signals.py) - for immediate notifications
     - Daily command: `notify_ops_pending_and_overdue()` - for scheduled checks

### Payment Notifications (All Providers)

1. **Payment Due Notification**
   - **Trigger**: When a payment is due (within 7 days, due today, or overdue)
   - **Recipients**: Student + Sales team member who registered the student
   - **Function**: `notify_payment_due()`
   - **Content**: Includes payment amount, due date, remaining balance, total remaining, and course details
   - **Location**: 
     - Signal: `payment_installment_post_save` (signals.py) - for immediate notifications
     - Daily command: `notify_sales_payment_reminders()` - for scheduled checks

## Email Features

### HTML Email Templates
All notifications include:
- **HTML formatted emails** with professional styling
- **Plain text fallback** for email clients that don't support HTML
- **Color-coded status indicators**:
  - Red (#e74c3c) for overdue items
  - Orange (#f39c12) for items due soon
  - Green (#27ae60) for completed items
  - Blue (#3498db) for informational items

### Email Content
- **Subject lines** with clear prefixes: `[ICPS]` or `[ICPS ProQual]`
- **Detailed information** including student name, registration ID, course details
- **Action items** clearly stated
- **Contact information** for sales representatives

## Implementation Details

### Files Modified

1. **`core/notifications.py`**
   - Complete rewrite with all notification functions
   - HTML email templates
   - Error handling and logging

2. **`core/views.py`**
   - Added notification calls in:
     - `ProQualAssignOpsView.post()` - Ops assignment
     - `ProQualSetPortalDateView.post()` - Portal allotment
     - `UnitTaskCompleteView.post()` - Unit completion

3. **`core/signals.py`**
   - Added `unit_task_post_save` signal for unit due notifications
   - Added `payment_installment_post_save` signal for payment due notifications

4. **`core/management/commands/notify_daily.py`**
   - Updated to use new notification system
   - Runs daily to check for due items

### Signal Handlers

#### `unit_task_post_save`
- Triggers when a UnitTask is created or updated
- Sends notification if task is due within 7 days
- Differentiates between ProQual and other providers

#### `payment_installment_post_save`
- Triggers when a PaymentInstallment is created or updated
- Sends notification if payment is due within 7 days
- Sends to both student and sales person

## Configuration

### Email Settings
Email configuration is in `ICPS/settings.py`:
- **Development**: Uses console backend (emails printed to console)
- **Production**: Uses SMTP backend (configure via environment variables)

### Environment Variables
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=no-reply@icps.com
```

## Daily Notification Command

Run the daily notification command to check for due items:
```bash
python manage.py notify_daily
```

This command:
- Checks for units due within 7 days or overdue
- Checks for payments due within 7 days or overdue
- Sends notifications to appropriate recipients

**Recommended**: Set up a cron job or scheduled task to run this daily.

## Testing

A test script is available: `test_notifications.py`

Run it to verify all notification functions:
```bash
python test_notifications.py
```

## Error Handling

All notification functions include:
- **Logging**: Errors are logged with full stack traces
- **Graceful failures**: Notification failures don't break the main application flow
- **Email validation**: Checks for valid email addresses before sending
- **Recipient validation**: Ensures at least one valid recipient exists

## Future Enhancements

Potential improvements:
1. Email templates in separate HTML files
2. Email queue system (Celery) for better performance
3. Email preferences per user
4. Notification history/logging
5. SMS notifications (optional)
6. Push notifications (for mobile apps)

## Notes

- In development mode, emails are sent to the console (check Django console output)
- In production, ensure SMTP settings are properly configured
- All notifications are logged for debugging purposes
- The system automatically differentiates between ProQual and other providers

