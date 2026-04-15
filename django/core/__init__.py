"""
docker-django/django/core/__init__.py - Django 项目核心模块
"""
from .celery import app as celery_app
__all__ = ('celery_app',)