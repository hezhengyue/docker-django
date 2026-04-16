"""
docker-django/django/config/urls.py - Django 项目 URL 配置
"""

from django.contrib import admin
from django.urls import path,include
from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

def health_check(request):
    """健康检查端点 - Docker/K8s/云厂商使用"""
    return JsonResponse({
        "status": "healthy",
        "service": getattr(settings, 'PROJECT_NAME', 'unknown'),
    })

def root_redirect(request):
    """根路径重定向到 admin"""
    return redirect('/admin/')

urlpatterns = [
    path('', root_redirect, name='root'),
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
