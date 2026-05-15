# core/views.py

from django.http import JsonResponse
from django.shortcuts import render

from common.tasks.test_progress import (
    test_progress
)


def start_test_task(request):

    task = test_progress.delay()

    return JsonResponse({
        "task_id": task.id
    })


def websocket_test(request):

    return render(
        request,
        "test.html"
    )