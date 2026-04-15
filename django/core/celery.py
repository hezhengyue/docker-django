"""
docker-django/django/core/celery.py - Celery 配置文件
"""
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('ops_platform')
app.config_from_object('django.conf:settings', namespace='CELERY')

# 🔑 动态发现已安装的 app，避免导入不存在的包报错
app.autodiscover_tasks(settings.INSTALLED_APPS)

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """调试用：查看 Worker 是否正常"""
    print(f'Request: {self.request!r}')
    return 'OK'