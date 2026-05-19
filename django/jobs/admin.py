# jobs/admin.py

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from jobs.models import Job
from jobs.models import JobLog


# =========================
# JobLog Admin
# =========================
@admin.register(JobLog)
class JobLogAdmin(admin.ModelAdmin):

    list_display = [
        'job_name',
        'level',
        'short_message',
        'created_at',
    ]

    list_filter = [
        'level',
        'job',
    ]

    search_fields = [
        'message',
        'job__name',
    ]

    ordering = [
        '-id'
    ]

    list_per_page = 100

    readonly_fields = [
        'job',
        'level',
        'message',
        'created_at',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def job_name(self, obj):

        url = reverse(
            'admin:jobs_job_change',
            args=[obj.job.id]
        )

        return format_html(
            '<a href="{}">#{} - {}</a>',
            url,
            obj.job.id,
            obj.job.name
        )

    job_name.short_description = '任务'

    def short_message(self, obj):

        if len(obj.message) > 100:
            return obj.message[:100] + '...'

        return obj.message

    short_message.short_description = '日志'


# =========================
# Job Admin
# =========================

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):

    change_form_template = 'admin/jobs/job/change_form.html'

    list_display = [
        'id',
        'name',
        'job_type',
        'status',
        'progress_text',
        'created_at',
    ]

    list_filter = [
        'status',
        'job_type',
    ]

    search_fields = [
        'name',
    ]

    ordering = [
        '-id'
    ]

    list_per_page = 50

    readonly_fields = [
        'name',
        'job_type',

        'status',

        'live_progress',

        'payload',
        'result',

        'error_message',

        'started_at',
        'finished_at',

        'created_at',
        'updated_at',

        'log_link',
    ]

    fields = [
        'name',
        'job_type',

        'status',

        'live_progress',

        'payload',
        'result',

        'error_message',

        'started_at',
        'finished_at',

        'created_at',
        'updated_at',

        'log_link',
    ]

    # =========================
    # 禁止新增
    # =========================

    def has_add_permission(self, request):
        return False

    # =========================
    # 禁止删除
    # =========================

    def has_delete_permission(self, request, obj=None):
        return True

    # =========================
    # 禁止编辑
    # =========================

    def has_change_permission(self, request, obj=None):
        return True

    # =========================
    # 禁止保存按钮
    # =========================

    def render_change_form(
        self,
        request,
        context,
        *args,
        **kwargs
    ):

        context.update({
            'show_save': False,
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
            'show_delete': True,
        })

        return super().render_change_form(
            request,
            context,
            *args,
            **kwargs
        )

    # =========================
    # 列表进度
    # =========================

    def progress_text(self, obj):

        return f'{obj.progress}% ({obj.current}/{obj.total})'

    progress_text.short_description = '进度'

    # =========================
    # 实时进度
    # =========================

    def live_progress(self, obj):

        return format_html(
            '''
            <span id="job-progress-text">
                {}% ({}/{})
            </span>
            ''',
            obj.progress,
            obj.current,
            obj.total,
        )

    live_progress.short_description = '实时进度'

    # =========================
    # 日志链接
    # =========================

    def log_link(self, obj):

        url = reverse(
            'admin:jobs_joblog_changelist'
        )

        return format_html(
            '<a href="{}?job__id__exact={}">查看全部日志</a>',
            url,
            obj.id
        )

    log_link.short_description = '日志'