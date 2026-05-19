# common/admin/rename.py
from django.apps import apps


THIRD_PARTY_APP_NAMES = {
    'axes': '安全监控',
    'auditlog': '操作审计',
    'django_celery_beat': '定时任务',
    'django_celery_results': '任务结果',
}


THIRD_PARTY_MODEL_NAMES = {

    # axes
    'axes.AccessAttempt': '锁定记录',
    'axes.AccessLog': '登录流水',
    'axes.AccessFailureLog': '旧登录流水',

    # auditlog
    'auditlog.LogEntry': '操作日志',

    # celery beat
    'django_celery_beat.PeriodicTask': '定时任务',
    'django_celery_beat.IntervalSchedule': '间隔计划',
    'django_celery_beat.CrontabSchedule': 'Crontab计划',

    # celery result
    'django_celery_results.TaskResult': '任务结果',
}


def rename_third_party_apps():

    # =========================
    # APP 名称
    # =========================

    for app_label, verbose_name in THIRD_PARTY_APP_NAMES.items():

        try:
            app_config = apps.get_app_config(app_label)
            app_config.verbose_name = verbose_name

        except LookupError:
            pass

    # =========================
    # MODEL 名称
    # =========================

    for model_path, verbose_name in THIRD_PARTY_MODEL_NAMES.items():

        try:
            app_label, model_name = model_path.split('.')

            model = apps.get_model(app_label, model_name)

            model._meta.verbose_name = verbose_name
            model._meta.verbose_name_plural = verbose_name

        except LookupError:
            pass