# common/tasks/test_progress.py

import time

from celery import shared_task

from common.tasks.progress import (
    ProgressReporter
)


@shared_task(bind=True)
def test_progress(self):

    total = 100

    reporter = ProgressReporter(
        self.request.id
    )

    for i in range(total + 1):

        time.sleep(0.2)

        reporter.send(
            current=i,
            total=total,
            message=f"正在处理 {i}/{total}"
        )

    return {
        "status": "success"
    }