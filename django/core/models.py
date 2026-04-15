"""
docker-django/django/core/models.py - Django 项目核心模型定义
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """自定义用户模型 - Django 5.2 兼容"""
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("手机号"),
        validators=[RegexValidator(r'^1[3-9]\d{9}$', _('请输入正确的手机号'))],
        db_index=True,
        help_text=_("11 位中国大陆手机号")
    )
    
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = verbose_name
        db_table = 'core_user'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return self.username or self.email or self.phone or f'User-{self.pk}'
    
    @property
    def display_name(self):
        return self.get_full_name() or self.username or self.phone