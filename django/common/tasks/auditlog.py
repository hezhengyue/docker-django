# common/tasks/auditlog.py
from celery import shared_task
from auditlog.models import LogEntry
from django.utils import timezone
from datetime import timedelta


@shared_task
def clean_old_audit_logs(days=180):

    expire_time = timezone.now() - timedelta(days=days)

    deleted_count, _ = LogEntry.objects.filter(
        timestamp__lt=expire_time
    ).delete()

    return deleted_count