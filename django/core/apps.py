from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):

        from auditlog.registry import auditlog

        from .models import User

        auditlog.register(
            User,

            # 不记录这些字段
            exclude_fields=['password', 'last_login',],

            # 敏感字段脱敏
            mask_fields=[],
        )