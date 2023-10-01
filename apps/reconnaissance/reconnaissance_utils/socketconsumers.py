import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from apps.reconnaissance.models import ReconnaissanceAIResults


class ReconnaissanceAIResultConsumer(AsyncWebsocketConsumer):
    room_group_name = "RECONNAISSANCEAIRESULT"

    async def connect(self):
        try:
            await self.accept()
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        except:
            await self.send(text_data={"msg": "error msg"})
            await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            await self.send(text_data=json.dumps([{"title": "UNL"}]))

    async def disconnect(self, code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )
        except:
            print("Failed to disconnect user from socket")

    async def send_notification(self, event):
        if self.scope.get("ip"):
            if self.scope.get("ip") == event.get("text").get("camera_ip"):
                print("In Live detections")
                await self.send(text_data=json.dumps(event["text"]))
        else:
            print("In Live detections")
            await self.send(text_data=json.dumps(event["text"]))


class ReconnaissanceAIProcessingConsumer(AsyncWebsocketConsumer):
    room_group_name = "RECONNAISSANCEAIPROCESS"

    async def connect(self):
        try:
            await self.accept()
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        except:
            await self.send(text_data={"msg": "error msg"})
            await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            await self.send(text_data=json.dumps([{"title": "UNL"}]))

    async def disconnect(self, code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )
        except:
            print("Failed to disconnect user from socket")

    async def send_notification(self, event):
        if self.scope.get("ip"):
            if self.scope.get("ip") == event.get("text").get("camera_ip"):
                print("In Live detections")
                await self.send(text_data=json.dumps(event["text"]))
        else:
            print("In Live detections")
            await self.send(text_data=json.dumps(event["text"]))

