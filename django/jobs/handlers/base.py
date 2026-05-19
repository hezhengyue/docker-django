# jobs/handlers/base.py

from jobs.services.job_service import JobService


class BaseHandler:

    def __init__(self, job):
        self.job = job

    def log(self, message, level='info'):
        JobService.log(self.job, message, level)

    def progress(self, current, total):
        JobService.progress(
            self.job,
            current,
            total,
        )

    def handle(self):
        raise NotImplementedError