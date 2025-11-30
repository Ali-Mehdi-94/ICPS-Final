"""
Quick email test script to verify SMTP configuration.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ICPS.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("="*60)
print("EMAIL CONFIGURATION TEST")
print("="*60)

# Display current configuration
print("\nCurrent Email Configuration:")
print(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"  EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
print(f"  EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
print(f"  EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
print(f"  EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
print(f"  DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")
print(f"  DEBUG: {settings.DEBUG}")

# Test email
print("\n" + "="*60)
print("Sending test email...")
print("="*60)

# Replace with your test email address
TEST_EMAIL = input("\nEnter your test email address: ").strip()

if not TEST_EMAIL:
    print("✗ No email address provided. Exiting.")
    exit(1)

try:
    send_mail(
        subject='[ICPS] Test Email - Email Configuration Working!',
        message='''
This is a test email from your ICPS system.

If you receive this email, your SMTP configuration is working correctly!

Your email settings:
- Backend: {backend}
- Host: {host}
- Port: {port}
- TLS: {tls}

You can now receive notifications from the ICPS system.

Best regards,
ICPS System
        '''.format(
            backend=settings.EMAIL_BACKEND,
            host=getattr(settings, 'EMAIL_HOST', 'N/A'),
            port=getattr(settings, 'EMAIL_PORT', 'N/A'),
            tls=getattr(settings, 'EMAIL_USE_TLS', 'N/A'),
        ),
        from_email=None,  # Uses DEFAULT_FROM_EMAIL
        recipient_list=[TEST_EMAIL],
        fail_silently=False,
    )
    print(f"\n✓ Email sent successfully to {TEST_EMAIL}!")
    print("\nPlease check your inbox (and spam folder) for the test email.")
except Exception as e:
    print(f"\n✗ Error sending email: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Check your EMAIL_HOST_USER and EMAIL_HOST_PASSWORD environment variables")
    print("2. For Gmail, make sure you're using an App Password (not your regular password)")
    print("3. Verify EMAIL_HOST and EMAIL_PORT are correct")
    print("4. Check your firewall/network settings")
    print("\nSee EMAIL_SETUP_GUIDE.md for detailed setup instructions.")

print("\n" + "="*60)

