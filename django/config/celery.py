# config/celery.py
import os
from pathlib import Path
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

PROJECT_NAME = Path(__file__).resolve().parent.parent.name

app = Celery(PROJECT_NAME)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    return {'app': app.main, 'project': PROJECT_NAME}