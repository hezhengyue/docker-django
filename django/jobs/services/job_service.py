# jobs/services/job_service.py

from django.utils import timezone

from jobs.models import Job
from jobs.models import JobLog


class JobService:

    @staticmethod
    def start(job: Job):

        job.status = 'running'
        job.started_at = timezone.now()

        job.save(
            update_fields=[
                'status',
                'started_at',
            ]
        )

        JobService.log(job, '任务开始执行')

    @staticmethod
    def progress(job: Job, current: int, total: int):

        job.current = current
        job.total = total

        if total > 0:
            job.progress = int(current / total * 100)

        job.save(
            update_fields=[
                'current',
                'total',
                'progress',
            ]
        )

    @staticmethod
    def success(job: Job, result=None):

        job.status = 'success'
        job.progress = 100
        job.finished_at = timezone.now()
        job.result = result or {}

        job.save(
            update_fields=[
                'status',
                'progress',
                'finished_at',
                'result',
            ]
        )

        JobService.log(job, '任务执行成功')

    @staticmethod
    def failed(job: Job, error):

        job.status = 'failed'
        job.error_message = str(error)
        job.finished_at = timezone.now()

        job.save(
            update_fields=[
                'status',
                'error_message',
                'finished_at',
            ]
        )

        JobService.log(
            job,
            f'任务执行失败: {error}',
            level='error'
        )

    @staticmethod
    def log(job: Job, message: str, level='info'):

        JobLog.objects.create(
            job=job,
            level=level,
            message=message,
        )