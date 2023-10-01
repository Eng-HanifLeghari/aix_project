import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from apps.camera.models import Camera

from apps.camera.models import Camera


class CameraConsumer(AsyncWebsocketConsumer):
    room_group_name = "AIXCAMERA"

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


class CameraConsumerGetStreamUrl(AsyncWebsocketConsumer):
    room_group_name = "AIXCAMSTREAMURL"

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
        if event.get("text").get("user_id") == self.scope.get("user").id:
            print("In streamed URL")
            await self.send(text_data=json.dumps(event["text"]))


class CameraAlertsAll(AsyncWebsocketConsumer):
    room_group_name = "AIXCAMALLALERTS"

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

    @sync_to_async
    def is_cam_exists(self , event):
        camera_exists = False
        cam_obj_exists = Camera.objects.filter(ip=event.get("text").get("camera_ip"))
        if cam_obj_exists:
            camera_exists = True
        return camera_exists



    async def send_notification(self, event):
        priority = event.get("text").get("priority", None)
        if priority:
            event.get("text").pop("priority")
        # if event.get("text").get("user_id") == self.scope.get("user").id:
        if self.scope.get("ip"):

            if self.scope.get("ip") == event.get("text").get("camera_ip"):
                # todo Changes for camera exists
                cam_exists = False
                cam_exists = await self.is_cam_exists(event)
                if cam_exists:
                    print("In alerts")
                    await self.send(text_data=json.dumps(event["text"]))
        else:
            # todo Changes for camera exists
            cam_exists = False
            cam_exists = await self.is_cam_exists(event)
            if cam_exists:
                await self.send(text_data=json.dumps(event["text"]))


class AIXCAMHighPRIORITYALERTS(AsyncWebsocketConsumer):
    room_group_name = "AIXCAMHighPRIORITYALERTS"

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
        # if event.get("text").get("user_id") == self.scope.get("user").id:
        if event.get("text").get("priority") is not None:
            await self.send(text_data=json.dumps(event["text"]))


class AIXCAMMediumPRIORITYALERTS(AsyncWebsocketConsumer):
    room_group_name = "AIXCAMMediumPRIORITYALERTS"

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
        if event.get("text").get("priority") is not None:
            await self.send(text_data=json.dumps(event["text"]))


class AIXCAMLowPRIORITYALERTS(AsyncWebsocketConsumer):
    room_group_name = "AIXCAMLowPRIORITYALERTS"

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
        if event.get("text").get("priority") is not None:
            await self.send(text_data=json.dumps(event["text"]))




class HighAlertImage(AsyncWebsocketConsumer):
    room_group_name = "AixHighAlertImage"

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
            # if event.get("text").get("user_id") == self.scope.get("user").id:
            if self.scope.get("ip") == event.get("text").get("camera_ip"):
                await self.send(text_data=json.dumps(event["text"]))
        else:
            await self.send(text_data=json.dumps(event["text"]))


class RestartCameraStreaming(AsyncWebsocketConsumer):
    room_group_name = "RestartCameraStreaming"

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
            # if event.get("text").get("user_id") == self.scope.get("user").id:
            if self.scope.get("ip") == event.get("text").get("camera_ip"):
                await self.send(text_data=json.dumps(event["text"]))
        else:
            await self.send(text_data=json.dumps(event["text"]))




