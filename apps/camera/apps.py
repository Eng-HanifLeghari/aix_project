import json
import os
import sys
from multiprocessing import Process
from django.apps import AppConfig
from customutils.channels_util import ChannelsCommonConsumer
from customutils.kafka_utils import Kafka
from datetime import datetime


class CameraConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.camera"

    def ready(self):
        # check if it has runserver
        if "runserver" in sys.argv:
            pass
        else:
            return
        con = ChannelsCommonConsumer()
        kaf = Kafka()

        def camera_detections():
            """
            Consumer for handling processed camera response
            :return: Streaming
            """
            print("In Camera/video kafka response function")
            try:
                consumer = kaf.kafka_consumer(
                    topic=os.getenv("KAFKA_CAMERA_DETECTIONS_TOPIC"), group_id=None
                )
                for msg in consumer:
                    data = msg.value.decode("UTF-8")
                    if data:
                        from apps.camera.controllers import CameraController
                        #
                        data = json.loads(data)
                        # (
                        #     camera_response_data_object,
                        #     status,
                        # ) = CameraController.save_camera_detections(data=data)
                        # if status:
                        #     data = CameraController.create_camera_detections_response_for_channels(
                        #         data=data,
                        #         camera_response_data_object=camera_response_data_object,
                        #     )
                        con.send_data(data=data, room_group_name="AIXCAMERA")
            except Exception as e:
                print("Exception in cam detections. Exception message :", str(e))

        def plotted_video_url():
            """
            Consumer for handling processed camera response
            :return: Streaming
            """
            print("In Camera kafka add response function")
            try:
                consumer = kaf.kafka_consumer(
                    topic=os.getenv("KAFKA_CAMERA_PLOTTED_VIDEO_URL"), group_id=None
                )
                for msg in consumer:
                    data = msg.value.decode("UTF-8")
                    if data:
                        from apps.camera.controllers import CameraController

                        (
                            update_status,
                            exception_message,
                            camera_object,
                        ) = CameraController.update_urls(data)
                        if update_status:
                            data = json.loads(data)
                            data["user_id"] = camera_object.user.id
                            con.send_data(data=data, room_group_name="AIXCAMSTREAMURL")
                        else:
                            print(
                                "Exception in update streamed URL controller. Exception message",
                                exception_message,
                            )
            except Exception as e:
                print("Exception in kafka streamed url. Exception message: ", str(e))

        def camera_alerts_all_ip():
            """
            Consumer for handling processed camera alerts
            :return: Streaming
            """
            print("In Camera/alerts kafka response function")
            try:
                consumer = kaf.kafka_consumer(
                    topic=os.getenv("KAFKA_STREAM_DETECTIONS_ALERTS"), group_id=None
                )
                for msg in consumer:
                    data = msg.value.decode("UTF-8")
                    if data:
                        from apps.camera.controllers import CameraController
                        data = json.loads(data)
                        data = CameraController.create_alerts_detections_response_for_channels(
                            data=data
                        )
                        con.send_data(data=data, room_group_name="AIXCAMALLALERTS")
            except Exception as e:
                print("Exception in cam detections. Exception message :", str(e))

        def camera_alerts_priority():
            """
            Consumer for handling processed camera alerts
            :return: Streaming
            """
            print("In Camera/alerts kafka response function")
            try:
                consumer = kaf.kafka_consumer(
                    topic=os.getenv("KAFKA_STREAM_DETECTIONS_ALERTS"), group_id=None
                )
                for msg in consumer:
                    data = msg.value.decode("UTF-8")
                    if data:
                        from apps.camera.controllers import CameraController
                        data = json.loads(data)
                        data["Time"] = datetime.strptime(data["Time"], "%Y-%m-%d %H:%M:%S.%f").strftime(os.getenv("CUSTOM_TIME_FORMAT"))
                        data = CameraController.create_data_for_notifications(
                            data=data
                        )
                        priority = 0
                        priority = data.get("priority")
                        if priority == 1:
                            con.send_data(data=data, room_group_name="AIXCAMHighPRIORITYALERTS")
                        elif priority == 2:
                            con.send_data(data=data, room_group_name="AIXCAMMediumPRIORITYALERTS")
                        elif priority == 3:
                            con.send_data(data=data, room_group_name="AIXCAMLowPRIORITYALERTS")
            except Exception as e:
                print("Exception in cam detections. Exception message :", str(e))

        def high_alert_image():
            """
            Consumer for handling processed camera alerts
            :return: Streaming
            """
            print("In Camera/alerts kafka response function")
            try:
                consumer = kaf.kafka_consumer(
                    topic=os.getenv("KAFKA_HIGH_ALERT_IMAGE"), group_id=None
                )
                for msg in consumer:
                    data = msg.value.decode("UTF-8")
                    if data:
                        from apps.notifications.models import Notification
                        data = json.loads(data)
                        data["Time"] = datetime.strptime(data["Time"], "%Y-%m-%d %H:%M:%S.%f").strftime(
                            os.getenv("CUSTOM_TIME_FORMAT"))
                        con.send_data(data=data, room_group_name="AixHighAlertImage")
                        alert_id = data.get("alert_id", None)
                        if alert_id:
                            Notification.objects.filter(alert_id=alert_id).update(is_view=True)
            except Exception as e:
                print("Exception in high alert image. Exception message :", str(e))

        def restart_camera_streaming():
            try:
                consumer = kaf.kafka_consumer(
                    topic=os.getenv("KAFKA_RESTART_CAMERA_STREAMING"), group_id=None
                )
                for msg in consumer:
                    data = msg.value.decode("UTF-8")
                    if data:
                        from apps.camera.models import Camera
                        from apps.camera.camera_utils.check_available_port import kill_node_ports
                        data = json.loads(data)
                        camera_obj = Camera.objects.get(ip=data.get("camera_ip"))
                        camera_obj.is_stream = False
                        camera_obj.save()
                        payload = {
                            "status": "restart_streaming",
                            "streaming_port": camera_obj.streaming_port,
                            "ai_streaming_port": camera_obj.ai_streaming_port
                        }
                        con.send_data(data=payload, room_group_name="RestartCameraStreaming")
            except Exception as e:
                print("Exception in Restart Camera Streaming. Exception message :", str(e))

        # Processes
        p1 = Process(target=camera_detections, args=())
        p1.start()
        camera_process_url = Process(target=plotted_video_url, args=())
        camera_process_url.start()
        camera_alerts_all_ip = Process(target=camera_alerts_all_ip, args=())
        camera_alerts_all_ip.start()
        camera_alerts_priority = Process(target=camera_alerts_priority, args=())
        camera_alerts_priority.start()
        high_alert_image = Process(target=high_alert_image, args=())
        high_alert_image.start()
        restart_camera_streaming = Process(target=restart_camera_streaming, args=())
        restart_camera_streaming.start()
