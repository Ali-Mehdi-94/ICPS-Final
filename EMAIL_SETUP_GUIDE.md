# Email Setup Guide - Sending Real Emails

## Quick Overview

Currently, your system is set to **print emails to the console** (development mode). To send emails to actual email addresses, you need to:

1. **Configure SMTP settings** (Gmail, Outlook, or other email provider)
2. **Set environment variables** with your email credentials
3. **Optionally disable DEBUG mode** or override the email backend

---

## Option 1: Using Gmail (Recommended for Testing)

### Step 1: Create a Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification** (enable it if not already enabled)
3. Scroll down to **App passwords**
4. Select **Mail** and **Other (Custom name)**
5. Enter "ICPS Django" as the name
6. Click **Generate**
7. **Copy the 16-character password** (you'll need this)

### Step 2: Set Environment Variables

Create a `.env` file in your project root (or set system environment variables):

**Windows (PowerShell):**
```powershell
$env:EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
$env:EMAIL_HOST="smtp.gmail.com"
$env:EMAIL_PORT="587"
$env:EMAIL_USE_TLS="True"
$env:EMAIL_HOST_USER="your-email@gmail.com"
$env:EMAIL_HOST_PASSWORD="your-16-char-app-password"
$env:DEFAULT_FROM_EMAIL="your-email@gmail.com"
```

**Windows (Command Prompt):**
```cmd
set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
set EMAIL_HOST=smtp.gmail.com
set EMAIL_PORT=587
set EMAIL_USE_TLS=True
set EMAIL_HOST_USER=your-email@gmail.com
set EMAIL_HOST_PASSWORD=your-16-char-app-password
set DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Linux/Mac:**
```bash
export EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
export EMAIL_HOST="smtp.gmail.com"
export EMAIL_PORT="587"
export EMAIL_USE_TLS="True"
export EMAIL_HOST_USER="your-email@gmail.com"
export EMAIL_HOST_PASSWORD="your-16-char-app-password"
export DEFAULT_FROM_EMAIL="your-email@gmail.com"
```

### Step 3: Override DEBUG Mode (Optional)

If you want to test emails while still in DEBUG mode, you can temporarily override the email backend in `settings.py`:

```python
# Force SMTP even in DEBUG mode (for testing)
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.smtp.EmailBackend'  # Changed from console
)
```

Or set it directly:
```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
```

---

## Option 2: Using Outlook/Office 365

### Environment Variables:

```bash
EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST="smtp.office365.com"
EMAIL_PORT="587"
EMAIL_USE_TLS="True"
EMAIL_HOST_USER="your-email@outlook.com"
EMAIL_HOST_PASSWORD="your-password"
DEFAULT_FROM_EMAIL="your-email@outlook.com"
```

---

## Option 3: Using Other SMTP Providers

### Generic SMTP Configuration:

```bash
EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST="smtp.your-provider.com"  # e.g., smtp.mail.yahoo.com
EMAIL_PORT="587"  # or 465 for SSL
EMAIL_USE_TLS="True"  # or False if using SSL on port 465
EMAIL_HOST_USER="your-email@provider.com"
EMAIL_HOST_PASSWORD="your-password"
DEFAULT_FROM_EMAIL="your-email@provider.com"
```

### Common SMTP Settings:

| Provider | Host | Port | TLS |
|----------|------|------|-----|
| Gmail | smtp.gmail.com | 587 | Yes |
| Outlook | smtp.office365.com | 587 | Yes |
| Yahoo | smtp.mail.yahoo.com | 587 | Yes |
| SendGrid | smtp.sendgrid.net | 587 | Yes |
| Mailgun | smtp.mailgun.org | 587 | Yes |

---

## Option 4: Using .env File (Recommended)

### Step 1: Install python-decouple (if not already installed)

```bash
pip install python-decouple
```

### Step 2: Create `.env` file in project root

```env
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Other settings
DEBUG=True
SECRET_KEY=your-secret-key
```

### Step 3: Update settings.py to use decouple

Add at the top:
```python
from decouple import config
```

Then update email settings:
```python
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='no-reply@icps.local')
```

**Note**: Make sure `.env` is in your `.gitignore` file!

---

## Testing Email Configuration

### Test 1: Quick Test Script

Create `test_email.py`:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ICPS.settings')
django.setup()

from django.core.mail import send_mail

try:
    send_mail(
        subject='Test Email from ICPS',
        message='This is a test email. If you receive this, your email configuration is working!',
        from_email=None,  # Uses DEFAULT_FROM_EMAIL
        recipient_list=['your-test-email@gmail.com'],
        fail_silently=False,
    )
    print("✓ Email sent successfully!")
except Exception as e:
    print(f"✗ Error sending email: {str(e)}")
```

Run it:
```bash
python test_email.py
```

### Test 2: Test via Django Shell

```bash
python manage.py shell
```

Then:
```python
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test.',
    None,
    ['your-email@gmail.com'],
    fail_silently=False,
)
```

### Test 3: Test Notification System

```bash
python test_notifications.py
```

---

## Troubleshooting

### Issue: "Authentication failed"

**Solutions:**
- For Gmail: Make sure you're using an **App Password**, not your regular password
- Check that 2-Step Verification is enabled
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are correct

### Issue: "Connection refused" or "Timeout"

**Solutions:**
- Check your firewall settings
- Verify EMAIL_HOST and EMAIL_PORT are correct
- Try using port 465 with SSL instead of 587 with TLS

### Issue: Emails going to spam

**Solutions:**
- Use a professional email address (not a personal Gmail)
- Set up SPF, DKIM, and DMARC records (for production)
- Use a service like SendGrid or Mailgun for better deliverability

### Issue: "SMTPAuthenticationError"

**Solutions:**
- Double-check your credentials
- For Gmail: Ensure "Less secure app access" is enabled (if not using App Password)
- Try generating a new App Password

---

## Production Recommendations

### For Production, consider:

1. **Email Service Providers:**
   - **SendGrid** (free tier: 100 emails/day)
   - **Mailgun** (free tier: 5,000 emails/month)
   - **Amazon SES** (very cheap, pay per email)
   - **Postmark** (great deliverability)

2. **Security:**
   - Never commit `.env` file to git
   - Use environment variables or secret management
   - Rotate passwords regularly

3. **Monitoring:**
   - Set up email delivery monitoring
   - Log email failures
   - Set up alerts for email service issues

---

## Quick Start (Gmail)

1. **Get Gmail App Password:**
   - Google Account → Security → App passwords → Generate

2. **Set environment variables:**
   ```powershell
   $env:EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
   $env:EMAIL_HOST_USER="your-email@gmail.com"
   $env:EMAIL_HOST_PASSWORD="your-app-password"
   $env:DEFAULT_FROM_EMAIL="your-email@gmail.com"
   ```

3. **Test:**
   ```bash
   python test_email.py
   ```

4. **Done!** Your emails should now send to real addresses.

---

## Current Configuration Check

Your current setup in `settings.py`:
- ✅ Uses console backend when `DEBUG=True`
- ✅ Uses SMTP backend when `DEBUG=False`
- ✅ Reads from environment variables
- ✅ Has sensible defaults

**To enable real emails:**
1. Set environment variables (see above)
2. Either set `DEBUG=False` OR override `EMAIL_BACKEND` to use SMTP

That's it! 🎉

