import json
import os
import requests
from rest_framework import status
from django.db import models as django_models
from django.db.models import Q
from datetime import datetime
import time
from apps.camera.camera_utils.camera_enums import Threats, Priorities
from apps.camera.camera_utils.check_available_port import open_port, kill_node_ports
from apps.camera.models import Camera
from apps.camera.serializers import (
    CameraAddSerializer,
    CameraDetectionsResponseSerializer, CamDetailSerialzier, CameraSearchSerializer,
)
from apps.notifications.models import Notification
from customutils.data_handler import get_value_from_data
from customutils.kafka_utils import Kafka
from customutils.request_handlers import RequestHandler


class CameraSerializer:
    pass


class CameraController:
    @classmethod
    def save_camera(cls, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        kafka_con = Kafka()
        try:
            request.data["out_port"], request.data["streaming_port"], request.data["ai_streaming_port"], request.data[
                "docker_port_ml"] = open_port()
            request.data["password"] = get_value_from_data(data=request.data, key="password")
            request.data["username"] = get_value_from_data(data=request.data, key="username")

            validated_data = CameraAddSerializer(data=request.data)
            if validated_data.is_valid():
                data = validated_data.data
                data["user"] = RequestHandler.get_user(request=request)
                data["user_role"] = RequestHandler.get_user_role(request=request)
                data["service_type"] = RequestHandler.get_service_type(request=request)
                camera_added, camera_object = CameraAddSerializer.create(
                    validated_data=data
                )
                if camera_added:
                    if camera_object.active_status is True:
                        kafka_data_for_camera = {
                            "ip": camera_object.ip,
                            "is_drone_camera": camera_object.is_drone_camera,
                            "port": camera_object.port,
                            "name": camera_object.camera_name,
                            "username": camera_object.username,
                            "password": camera_object.password,
                            "threats": camera_object.threats,
                            "out_port": camera_object.out_port,
                            "lat": str(camera_object.lat),
                            "lng": str(camera_object.lng),
                            "protocol": camera_object.protocol,
                            "container_id": camera_object.container_id,
                            "docker_port_ml": camera_object.docker_port_ml,
                            "ai_service": camera_object.service_type.service_key,
                            "kafka_ip": os.getenv("KAFKA_IP") + ":" + os.getenv("KAFKA_PORT"),
                        }
                        kafka_con.kafka_producer(
                            topic=os.getenv("KAFKA_CAMERA_PRODUCER_TOPIC"),
                            values=kafka_data_for_camera,
                        )
                        # kill_node_ports(streaming_port=camera_object.streaming_port , ai_streaming_port=camera_object.ai_streaming_port)
                    aix_response = {
                            "statusMessage": "Camera added Successfully",
                            "errorStatus": False,
                            "data": [],
                            "statusCode": status.HTTP_201_CREATED,
                        }
                else:
                    aix_response = {
                            "statusMessage": "Unable to add camera",
                            "data": [],
                            "statusCode": status.HTTP_206_PARTIAL_CONTENT,
                            "errorStatus": True,
                        }
            else:
                aix_response = {
                        "statusMessage": "Invalid data",
                        "data": validated_data.errors,
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "errorStatus": True,
                    }
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return aix_response

    @classmethod
    def update_urls(cls, data):
        """
        This method is for updating stream url in camera object received by ML&DE team.
        :param data:
        :return:
        """
        update_status = False
        exception_message = ""
        camera_object = None
        try:
            data = json.loads(data)
            ip = get_value_from_data(data=data, key="ip")
            container_id = get_value_from_data(data=data, key="container_id")
            stream_url = get_value_from_data(data=data, key="stream_url")
            camera_feed_url = get_value_from_data(data=data, key="camera_feed_url")
            update_status, exception_message, camera_object = Camera.update_cam_urls(
                ip=ip, stream_url=stream_url, container_id=container_id, camera_feed_url=camera_feed_url
            )
        except Exception as e:
            exception_message = str(e)
        finally:
            return update_status, exception_message, camera_object

    @classmethod
    def update_camera_satus(cls, ip, cam_status):
        """
        This method is for updating camera status
        :param data:
        :return:
        """
        update_status = False
        exception_message = ""
        camera_object = None
        kafka_topic = None
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            active_camera_count = Camera.objects.filter(active_status=True).count()
            if cam_status:
                if active_camera_count <= 4:
                    update_status, exception_message, camera_object = Camera.update_cam_status(
                        ip=ip, cam_status=cam_status
                    )
                    if update_status:
                        kafka_con = Kafka()
                        kafka_data_for_camera = {
                            "ip": camera_object.ip,
                            "port": camera_object.port,
                            "is_drone_camera": camera_object.is_drone_camera,
                            "name": camera_object.camera_name,
                            "username": camera_object.username,
                            "password": camera_object.password,
                            "threats": camera_object.threats,
                            "out_port": camera_object.out_port,
                            "lat": str(camera_object.lat),
                            "lng": str(camera_object.lng),
                            "protocol": camera_object.protocol,
                            "container_id": camera_object.container_id,
                            "ai_service": camera_object.service_type.service_key,
                            "docker_port_ml": camera_object.docker_port_ml,
                            "kafka_ip": os.getenv("KAFKA_IP") + ":" + os.getenv("KAFKA_PORT"),
                        }
                        if cam_status == 1:
                            kafka_topic = os.getenv("KAFKA_CAMERA_PRODUCER_TOPIC")
                        elif cam_status == 0:
                            kill_node_ports(streaming_port=camera_object.streaming_port,
                                            ai_streaming_port=camera_object.ai_streaming_port)
                            kafka_topic = os.getenv("KAFKA_DELETE_CAMERA_TOPIC")
                        kafka_con.kafka_producer(
                            topic=kafka_topic,
                            values=kafka_data_for_camera,
                        )
                        time.sleep(12)
                        aix_response = {
                                "statusMessage": "Camera Enabled",
                                "data": [],
                                "statusCode": status.HTTP_200_OK,
                                "errorStatus": False,
                            }
                else:
                    aix_response = {
                            "statusMessage": "Admin restricts activating more than 4 cameras",
                            "data": [],
                            "statusCode": status.HTTP_200_OK,
                            "errorStatus": False,
                        }
            else:
                update_status, exception_message, camera_object = Camera.update_cam_status(
                    ip=ip, cam_status=cam_status
                )
                if update_status:
                    kafka_con = Kafka()
                    kafka_data_for_camera = {
                        "ip": camera_object.ip,
                        "port": camera_object.port,
                        "name": camera_object.camera_name,
                        "username": camera_object.username,
                        "password": camera_object.password,
                        "threats": camera_object.threats,
                        "out_port": camera_object.out_port,
                        "lat": str(camera_object.lat),
                        "lng": str(camera_object.lng),
                        "protocol": camera_object.protocol,
                        "container_id": camera_object.container_id,
                        "ai_service": camera_object.service_type.service_key,
                        "kafka_ip": os.getenv("KAFKA_IP") + ":" + os.getenv("KAFKA_PORT"),
                        "docker_port_ml": camera_object.docker_port_ml,
                    }
                    if cam_status == 1:
                        kafka_topic = os.getenv("KAFKA_CAMERA_PRODUCER_TOPIC")
                    elif cam_status == 0:
                        kafka_topic = os.getenv("KAFKA_DELETE_CAMERA_TOPIC")
                    kafka_con.kafka_producer(
                        topic=kafka_topic,
                        values=kafka_data_for_camera,
                    )
                    time.sleep(12)
                    aix_response = {
                            "statusMessage": "Camera Disabled",
                            "data": [],
                            "statusCode": status.HTTP_200_OK,
                            "errorStatus": False,
                        }
        except Exception as e:
            aix_response = {
                "statusMessage": str(e),
                "data": [],
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "errorStatus": True,
            }
        finally:
            return update_status, exception_message, camera_object, aix_response

    @classmethod
    def update_camera(cls, ip, data):
        """
        This method is for updating camera status
        :param data:
        :return:
        """
        update_status = False
        exception_message = ""
        camera_object = None
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            update_status, exception_message, camera_object = Camera.update_cam_detail(
                ip=ip, data=data
            )
            aix_response = {
                    "statusMessage": "Camera updated successfully",
                    "data": [],
                    "statusCode": status.HTTP_200_OK,
                    "errorStatus": False,
                }
        except Exception as e:
            aix_response = {
                "statusMessage": str(e),
                "data": [],
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "errorStatus": False,
            }
        finally:
            return update_status, exception_message, camera_object, aix_response

    @classmethod
    def save_camera_detections(cls, data):
        """
        Save response of cam detections for maintain logging
        :param data:
        :return: Boolean and data object in case of success
        """
        camera_response = None
        save_status = False
        try:
            print("Data received in save_camera_response controller")
            validated_data = CameraDetectionsResponseSerializer(data=data)
            print(validated_data)
            if validated_data.is_valid():
                print("In Validated Data")
                validated_data.data.update({"ip": data.get("camera_ip")})
                print("After getting IP")
                (
                    camera_response,
                    save_status,
                ) = CameraDetectionsResponseSerializer.create(
                    validated_data=validated_data
                )
            else:
                print("Data not valid{}".format(validated_data.errors))
        except Exception as e:
            print(str(e))
            camera_response = {}
        finally:
            return camera_response, save_status

    @classmethod
    def create_camera_detections_response_for_channels(
            cls, data, camera_response_data_object
    ):
        """
        For creating response for sockets
        :param data:
        :param camera_response_data_object:
        :return:
        """
        try:
            data["user_id"] = camera_response_data_object.camera.user.id
        except Exception as e:
            print(str(e))
        finally:
            return data

    @classmethod
    def create_alerts_detections_response_for_channels(
            cls, data
    ):
        """
        For creating response for sockets
        :param data:
        :param camera_response_data_object:
        :return:
        """
        try:
            print(data)
            event_no = Threats(data.get("event_no")).name
            data["priority"] = int(data.get("threat_value"))
            priority = Priorities(int(data.get("threat_value"))).name
            data["event_no"] = event_no
            data["threat_value"] = priority
            datetime_str = data.get("Time")
            data['alert_id'] = data.get('alert_id')
            time = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f').time()
            data["Time"] = time.strftime("%H:%M:%S")

            # data["user_id"] = camera_response_data_object.camera.user.id
        except Exception as e:
            print(str(e))
        finally:
            return data

    @classmethod
    def create_data_for_notifications(
            cls, data
    ):
        """
        For creating response for sockets
        :param data:
        :param camera_response_data_object:
        :return:
        """
        event_text = ""
        try:
            event_no = Threats(data.get("event_no")).name
            data["priority"] = int(get_value_from_data(data=data, key="threat_value"))
            priority = Priorities(int(get_value_from_data(data=data, key="threat_value"))).name

            data["event_no"] = event_no
            data["threat_value"] = priority
            # todo

            datetime_str = get_value_from_data(data=data, key="Time")
            time = datetime.strptime(datetime_str, '%d-%m-%Y %H:%M:%S').time()
            data["Time"] = time.strftime("%H:%M:%S")
            camera_ip = get_value_from_data(data=data, key="camera_ip")
            alert_id = get_value_from_data(data=data, key="alert_id")
            camera_name = get_value_from_data(data=data, key="name")
            lat = get_value_from_data(data=data, key="lat")
            lng = get_value_from_data(data=data, key="lng")
            object_id = get_value_from_data(data=data, key="object_id")

            event_text = event_no + " detected on " + \
                         get_value_from_data(data=data, key="name") + " at " + datetime.strptime(datetime_str, "%d-%m-%Y %H:%M:%S").strftime(os.getenv("CUSTOM_TIME_FORMAT"))
            data["event_text"] = event_text
            notification_data = {"text": event_text, "camera_ip": camera_ip, "camera_name": camera_name, "lat": lat,
                                 "lng": lng, "priority": priority, "threat": event_no, "alert_id": alert_id,
                                 "object_id": object_id}
            if priority == 2 or priority == 3:
                notification_data["is_view"] = True
            else:
                notification_data["is_view"] = False
            Notification.create(notification_data)
        except Exception as e:
            print(str(e))
        finally:
            return data

    @classmethod
    def delete_camera(cls, request):
        """
        For deleting cam

        :param request:
        :return: delete_status if deleted successfully
        """
        delete_status = False
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            kafka_con = Kafka()
            camera_ip = request.data.get("camera_ip", "")
            delete_status, exception_message, camera_object = Camera.delete_cam(
                ip=camera_ip
            )
            if delete_status:
                kafka_data_for_camera = {
                    "ip": camera_object.ip,
                    "port": camera_object.port,
                    "name": camera_object.camera_name,
                    "username": camera_object.username,
                    "password": camera_object.password,
                    "threats": camera_object.threats,
                    "out_port": camera_object.out_port,
                    "lat": str(camera_object.lat),
                    "lng": str(camera_object.lng),
                    "protocol": camera_object.protocol,
                    "container_id": camera_object.container_id,
                    "ai_service": camera_object.service_type.service_key,
                    "kafka_ip": os.getenv("KAFKA_IP") + ":" + os.getenv("KAFKA_PORT"),
                    "docker_port_ml": camera_object.docker_port_ml,

                }
                kafka_con.kafka_producer(
                    topic=os.getenv("KAFKA_DELETE_CAMERA_TOPIC"),
                    values=kafka_data_for_camera,
                )
                if delete_status:
                    kill_node_ports(streaming_port=camera_object.streaming_port,
                                    ai_streaming_port=camera_object.ai_streaming_port)
                    aix_response = {
                            "statusMessage": "Camera deleted successfully",
                            "errorStatus": False,
                            "data": [],
                            "statusCode": status.HTTP_200_OK,
                        }
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "errorStatus": True,
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
        finally:
            return delete_status, aix_response

    @classmethod
    def delete_camera_multiple(cls, camera_ip):
        """
        For deleting cam

        :param request:
        :return: delete_status if deleted successfully
        """
        delete_status = False
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            kafka_con = Kafka()
            delete_status, exception_message, camera_object = Camera.delete_cam(
                ip=camera_ip
            )
            if delete_status:
                kafka_data_for_camera = {
                    "ip": camera_object.ip,
                    "port": camera_object.port,
                    "name": camera_object.camera_name,
                    "username": camera_object.username,
                    "password": camera_object.password,
                    "threats": camera_object.threats,
                    "out_port": camera_object.out_port,
                    "lat": str(camera_object.lat),
                    "lng": str(camera_object.lng),
                    "protocol": camera_object.protocol,
                    "container_id": camera_object.container_id,
                    "ai_service": camera_object.service_type.service_key,
                    "kafka_ip": os.getenv("KAFKA_IP") + ":" + os.getenv("KAFKA_PORT"),
                    "docker_port_ml": camera_object.docker_port_ml,

                }
                kafka_con.kafka_producer(
                    topic=os.getenv("KAFKA_DELETE_CAMERA_TOPIC"),
                    values=kafka_data_for_camera,
                )
                pass
            if delete_status:
                aix_response = {
                        "statusMessage": "Camera deleted successfully",
                        "errorStatus": False,
                        "data": [],
                        "statusCode": status.HTTP_200_OK,
                    }
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "errorStatus": True,
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
        finally:
            return delete_status, aix_response

    @classmethod
    def get_cam_uri(cls, request):
        """

        :param request:
        :return: camera URI if found
        """
        fetch_status = False
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            kafka_con = Kafka()
            feed_type = request.data.get("feed_type", "")
            camera_ip = request.data.get("camera_ip", "")

            fetch_status, exception_message, stream_uri = Camera.get_camera_uri(
                ip=camera_ip, feed_type=feed_type
            )
            if fetch_status:
                aix_response = {
                        "statusMessage": "Stream URI fetched successfully",
                        "errorStatus": False,
                        "data": stream_uri,
                        "statusCode": status.HTTP_200_OK,
                    }
        except Exception as e:
            aix_response = {
                "statusMessage": str(e),
                "errorStatus": True,
                "data": [],
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
        finally:
            return fetch_status, aix_response

    @classmethod
    def get_camera_stream(cls, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            ip = get_value_from_data(data=request.data, key="camera_ip")
            if ip:
                camera_obj = Camera.objects.get(ip=ip)
                payload = {
                    "camera_url": "rtsp://"
                                  + camera_obj.username
                                  + ":"
                                  + camera_obj.password
                                  + "@"
                                  + camera_obj.ip
                                  + ":"
                                  + str(camera_obj.port)
                                  + "/cam/realmonitor?channel=1&subtype=0",
                    "camera_ip": camera_obj.ip,
                    "kafka_ip": os.getenv("KAFKA_IP") + ":" + os.getenv("KAFKA_PORT"),
                }
                stream_response = requests.request(
                    "POST", os.getenv("STREAM_IP_ML"), data=payload
                )
                stream_url = stream_response.text
                if stream_url:
                    stream_url = json.loads(stream_url).get("stream_url")
                    aix_response = {
                            "statusMessage": "Stream Url fetched successfully",
                            "data": {"stream_url": stream_url},
                            "statusCode": status.HTTP_200_OK,
                            "errorStatus": False,
                        }
                else:
                    aix_response = {
                            "statusMessage": "Stream URL fetching error",
                            "data": [],
                            "statusCode": status.HTTP_417_EXPECTATION_FAILED,
                            "errorStatus": True,
                        }
            else:
                aix_response = {
                        "statusMessage": "Please provide camera IP",
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "errorStatus": True,
                    }
        except Exception as e:
            aix_response = {
                    "statusMessage": "Exception in getting stream.  Exception: {}".format(
                        str(e)
                    ),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return aix_response

    @classmethod
    def get_cam_detail(cls, id):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            # todo If user specific camera required
            data_obj = Camera.objects.filter(id=id)
            if data_obj:
                data = data_obj.values(
                    "location",
                    "username",
                    "password",
                    "id",
                    "ip",
                    "port",
                    "camera_name",
                    "lat",
                    "lng",
                    "threats",
                    "protocol",
                    "active_status",
                    "streaming_port",
                    "ai_streaming_port",
                    "service_type__service_key",
                    role_key=django_models.F("user_role__role_key"),
                ).first()
                data["service_type"] = get_value_from_data(data=data, key="service_type__service_key")
                data.pop("service_type__service_key")
                aix_response = {
                        "statusMessage": "Data Fetched Successfully",
                        "errorStatus": False,
                        "data": data,
                        "statusCode": status.HTTP_200_OK,
                    }
            else:
                aix_response = {
                        "statusMessage": "No record found",
                        "errorStatus": False,
                        "data": [],
                        "statusCode": status.HTTP_200_OK,
                    }
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return aix_response

    @classmethod
    def test_connection_adding_camera(cls, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            url = os.getenv("TEST_CONNECTION_CAMERA_URL")
            ip = RequestHandler.get_request_data(request, "ip")
            port = RequestHandler.get_request_data(request, "port")
            protocol = RequestHandler.get_request_data(request, "protocol")
            payload = {
                "ip": f"{ip}:{port}",
                "protocol": protocol,
                "uname": RequestHandler.get_request_data(request, "username"),
                "password": RequestHandler.get_request_data(request, "password"),
                "additional_params": RequestHandler.get_request_data(request, "additional_params")
            }
            files = []
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            if response.json().get("StatusCode") == 200:
                aix_response = {
                        "statusMessage": response.json().get("Status"),
                        "errorStatus": False,
                        "data": [],
                        "statusCode": status.HTTP_200_OK,
                    }
            else:
                aix_response = {
                        "statusMessage": response.json().get("Status"),
                        "errorStatus": True,
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                    }
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return aix_response

    @classmethod
    def search_camera(cls, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            search_query = RequestHandler.get_request_data(request, "search_query")
            instances = Camera.objects.filter(Q(ip__icontains=search_query) |
                                              Q(user_role__role_name__icontains=search_query) |
                                              Q(username__icontains=search_query) |
                                              Q(service_type__service_name__icontains=search_query) |
                                              Q(location__icontains=search_query))
            serializer_data = CameraSearchSerializer(instances, many=True)
            if serializer_data.data:
                aix_response = {
                        "statusMessage": "Data fetched successfully",
                        "errorStatus": False,
                        "data": serializer_data.data,
                        "statusCode": status.HTTP_200_OK,
                    }
            else:
                aix_response = {
                        "statusMessage": "NO Data",
                        "errorStatus": False,
                        "data": [],
                        "statusCode": status.HTTP_200_OK,
                    }
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return aix_response
