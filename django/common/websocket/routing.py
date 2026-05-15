# common/websocket/routing.py

from django.urls import re_path

from .consumers import ProgressConsumer


websocket_urlpatterns = [

    re_path(
        r"ws/task/(?P<task_id>[\w-]+)/$",
        ProgressConsumer.as_asgi(),
    ),

]