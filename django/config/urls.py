"""
docker-django/django/config/urls.py - Django 项目 URL 配置
"""

from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings

def health_check(request):
    """健康检查端点 - Docker/K8s/云厂商使用"""
    return JsonResponse({
        "status": "healthy",
        "service": getattr(settings, 'PROJECT_NAME', 'unknown'),
        "version": "1.0.0"
    })

def root_redirect(request):
    """根路径重定向到 admin"""
    return redirect('/admin/')

urlpatterns = [
    path('', root_redirect, name='root'),
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health'),
]