# jobs/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _


class Job(models.Model):

    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '运行中'),
        ('success', '成功'),
        ('failed', '失败'),
        ('cancelled', '取消'),
    ]

    job_type = models.CharField(max_length=100)

    name = models.CharField(max_length=255)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    progress = models.IntegerField(default=0)

    total = models.IntegerField(default=0)

    current = models.IntegerField(default=0)

    payload = models.JSONField(default=dict)

    result = models.JSONField(default=dict)

    error_message = models.TextField(blank=True)

    started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('任务')
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return f'{self.id} - {self.name}'


class JobLog(models.Model):

    LEVEL_CHOICES = [
        ('info', '信息'),
        ('warning', '警告'),
        ('error', '错误'),
    ]

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='logs'
    )

    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='info'
    )

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('任务日志')
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.message