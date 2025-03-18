import json
from channels.generic.websocket import AsyncWebsocketConsumer
from celery.result import AsyncResult

class AIProcessingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.task_id = self.scope["url_route"]["kwargs"]["task_id"]
        self.room_group_name = f"task_{self.task_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Check initial task status
        await self.send_task_status()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def send_task_status(self):
        task = AsyncResult(self.task_id)

        if task.state == "SUCCESS":
            response = {"status": "completed", "result": task.result}
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "task_update", "message": json.dumps(response)},
            )
        elif task.state == "FAILURE":
            response = {"status": "failed", "error": str(task.result)}
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "task_update", "message": json.dumps(response)},
            )

    async def task_update(self, event):
        message = event["message"]
        await self.send(text_data=message)
