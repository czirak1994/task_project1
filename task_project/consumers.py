import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            await self.channel_layer.group_add("tasks", self.channel_name)
            await self.accept()
        except Exception as e:
            print(f"Error during connect: {e}")    

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("tasks", self.channel_name)

    async def receive(self, text_data):
        # WebSocket üzenetek fogadása, ha szükséges
        pass

    async def task_created(self, event):
        task = event['task']
        await self.send(text_data=json.dumps({
            'type': 'task_created',
            'task': task
        }))

    async def task_selected(self, event):
            await self.send(text_data=json.dumps({
                'type': 'task_selected',
                'task_id': event['task_id'],
                'username': event['username']
            }))
    async def task_completed(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task_completed',
            'task_id': event['task_id'],
            'completed_by': event['completed_by']
        }))
    async def task_deselected(self, event):
        await self.send(text_data=json.dumps({
                'type': 'task_deselected',
                'task_id': event['task_id'],
            }))  