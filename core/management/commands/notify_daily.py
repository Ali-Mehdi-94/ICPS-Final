"""
Management command to send daily reminders to ops/sales (dev mode).
"""
from django.core.management.base import BaseCommand
from core.notifications import notify_ops_pending_and_overdue, notify_sales_payment_reminders


class Command(BaseCommand):
    help = "Send daily reminders to ops/sales (dev mode)."

    def handle(self, *args, **opts):
        notify_ops_pending_and_overdue()
        notify_sales_payment_reminders()
        self.stdout.write(self.style.SUCCESS("Daily notifications sent."))

