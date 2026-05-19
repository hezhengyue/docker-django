# jobs/urls.py
from django.urls import path
from jobs.views import job_detail

urlpatterns = [
    path('<int:job_id>/', job_detail, name='job_detail'),
]