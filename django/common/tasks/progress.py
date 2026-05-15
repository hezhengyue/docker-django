# common/tasks/progress.py

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class ProgressReporter:

    def __init__(self, task_id):

        self.task_id = task_id

        self.group_name = (
            f"task_{task_id}"
        )

        self.channel_layer = (
            get_channel_layer()
        )

    def send(
        self,
        current,
        total,
        message=""
    ):

        percent = int(
            current / total * 100
        )

        async_to_sync(
            self.channel_layer.group_send
        )(
            self.group_name,

            {
                "type": "progress_update",

                "data": {
                    "current": current,
                    "total": total,
                    "percent": percent,
                    "message": message,
                }
            }
        )