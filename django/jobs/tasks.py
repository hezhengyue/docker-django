# jobs/tasks.py

from celery import shared_task

from jobs.models import Job

from jobs.handlers.registry import JOB_HANDLERS

from jobs.services.job_service import JobService


@shared_task(bind=True)
def run_job(self, job_id):

    job = Job.objects.get(id=job_id)

    try:

        JobService.start(job)

        handler_class = JOB_HANDLERS[job.job_type]

        handler = handler_class(job)

        result = handler.handle()

        JobService.success(job, result)

    except Exception as e:

        JobService.failed(job, e)

        raise