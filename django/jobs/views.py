# jobs/views.py

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from jobs.models import Job



def job_detail(request, job_id):

    job = get_object_or_404(Job, id=job_id)

    return JsonResponse({
        'id': job.id,
        'status': job.status,
        'progress': job.progress,
        'current': job.current,
        'total': job.total,
        'result': job.result,
        'error_message': job.error_message,
    })