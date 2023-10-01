import os
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from apps.data_source.models import DataSource
import json
import ast
from customutils.kafka_utils import Kafka


class AIXImageConsumer(AsyncWebsocketConsumer):
    room_group_name = "AIXIMAGE"

    async def connect(self):
        try:
            await self.accept()
            # self.room_group_name = os.getenv("AIX_GROUP_NAME")
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

        await self.send(text_data=json.dumps(event["text"]))


class AIXReconFixedImageConsumer(AsyncWebsocketConsumer):
    room_group_name = "AIXRFI"

    async def connect(self):
        try:
            await self.accept()
            # self.room_group_name = os.getenv("AIX_GROUP_NAME")
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
            print(
                "+++++++++++++++++++++++In fixed image consumer socket URL +++++++++++++++++++++++++++++++"
            )
            filename, file_extension = os.path.splitext(
                event.get("text").get("processed_url")
            )
            if file_extension == ".tif" or file_extension == ".tiff":
                if file_extension == ".tif":
                    processed_url = event.get("text").get("processed_url")[:-3] + "jpeg"
                    event["text"]["processed_url"] = processed_url
                elif file_extension == ".tiff":
                    processed_url = event.get("text").get("processed_url")[:-4] + "jpeg"
                    event["text"]["processed_url"] = processed_url
                print("In Send image")
                await self.send(text_data=json.dumps(event["text"]))
            else:
                await self.send(text_data=json.dumps(event["text"]))
        else:
            print("User not matched in fixed image socket")


class AIXReconDetectionsImageConsumer(AsyncWebsocketConsumer):
    room_group_name = "AIXRDI"

    async def connect(self):
        try:
            await self.accept()
            # self.room_group_name = os.getenv("AIX_GROUP_NAME")
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
        try:
            if event.get("text").get("user_id") == self.scope.get("user").id:
                print(
                    "+++++++++++++++++++++++In fixed image consumer socket URL +++++++++++++++++++++++++++++++"
                )
                filename, file_extension = os.path.splitext(
                    event.get("text").get("processed_url")
                )
                if file_extension == ".tif" or file_extension == ".tiff":
                    if file_extension == ".tif":
                        processed_url = (
                            event.get("text").get("processed_url")[:-3] + "jpeg"
                        )
                        event["text"]["processed_url"] = processed_url
                    elif file_extension == ".tiff":
                        processed_url = (
                            event.get("text").get("processed_url")[:-4] + "jpeg"
                        )
                        event["text"]["processed_url"] = processed_url
                    print("In Send image")
                    await self.send(text_data=json.dumps(event["text"]))
                else:
                    await self.send(text_data=json.dumps(event["text"]))
            else:
                print("User not matched in fixed image socket")
        except Exception as e:
            print("Exception ==========".format(str(e)))
            print(
                "Exception in socket fixed images+++++++++++++++++++++++++++++++++++++++++"
            )


class AIXVideoConsumer(AsyncWebsocketConsumer):
    room_group_name = "AIXVIDEO"

    async def connect(self):
        try:
            await self.accept()
            # self.room_group_name = os.getenv("AIX_GROUP_NAME")
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        except:
            await self.send(text_data={"msg": "error msg"})
            await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            await self.send(text_data=json.dumps([{"title": "Receive"}]))

    async def disconnect(self, code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )
        except:
            print("Failed to disconnect user from socket")

    async def send_notification(self, event):
        if event.get("text").get("user_id") == self.scope.get("user").id:
            print("In Send Video")
            await self.send(text_data=json.dumps(event["text"]))


class BDMSocketConsumer(AsyncWebsocketConsumer):
    room_group_name = "BDM"
    kaf = Kafka()



    async def connect(self):
        try:
            await self.accept()
            # self.kaf = Kafka()
            # self.room_group_name = os.getenv("AIX_GROUP_NAME")
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        except:
            await self.send(text_data={"msg": "error msg"})
            await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        try:
            if text_data:
                text_data = ast.literal_eval(text_data)
                print("In BDM Socket")
                self.kaf.kafka_producer(
                    topic=os.getenv("BDM_KAFKA_TOPIC"),
                    values=text_data,
                )
        except Exception as e:
            print("Exception in BDM socket {}".format(str(e)))


    async def disconnect(self, code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )
        except:
            print("Failed to disconnect user from socket")

    async def send_notification(self, event):
        print("In send data")