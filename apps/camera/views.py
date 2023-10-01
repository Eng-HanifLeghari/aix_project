import ast
import os
import time
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.camera.controllers import CameraController
from apps.camera.models import Camera
from apps.camera.serializers import CameraListSerializer, CamDetailSerialzier, CameraAddSerializer, \
    CameraUpdateSerialzier
from apps.camera.elasticsearch import ElasticSearchHandler
from django.db.models import Q
from apps.camera.camera_utils.check_available_port import kill_node_ports
from customutils.kafka_utils import Kafka
from customutils.request_handlers import RequestHandler


# Create your views here.
class CameraOperationsView(APIView):
    """
    File uploading view.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # parser_classes = (FileUploadParser,)

    def post(self, request):
        """
        For storing files
        :param request:
        :return:
        """
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            aix_response = CameraController.save_camera(request=request)
        except Exception as e:
            aix_response = {
                    "statusMessage": "Camera adding failed with exception {}".format(
                        str(e)
                    ),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class DeleteCamera(APIView):
    """
    Delete individual record of target
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    data_context = {}

    def delete(self, request):
        """
        For calling delete controller
        :param request:
        :return:
        """
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            delete_status, aix_response = CameraController.delete_camera(request=request)
        except Exception as e:
            aix_response = {
                    "statusMessage": "Camera deletion failed with exception {}".format(
                        str(e)
                    ),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            time.sleep(10)
            return Response(aix_response)


class DeleteCameraMultiple(APIView):
    """
    Delete multiple record of camera
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    data_context = {}

    def delete(self, request):
        """
        For calling delete controller
        :param request:
        :return:
        """
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            ip_list = RequestHandler.get_request_data(request=request, key="camera_ip_list")
            if type(ip_list) is str:
                ip_list = ast.literal_eval(ip_list)
            for camera_ip in ip_list:
                delete_status, aix_response = CameraController.delete_camera_multiple(camera_ip=camera_ip)
        except Exception as e:
            aix_response = {
                    "statusMessage": "Camera deletion failed with exception {}".format(
                        str(e)
                    ),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class CameraUri(APIView):
    """
    API for getting cam URI(Live or processed) based on feed_type param
    """

    data_context = {}

    def get(self, request):
        """
        For  controller
        :param request:
        :return:
        """
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            fetch_status, aix_response = CameraController.get_cam_uri(request=request)
        except Exception as e:
            aix_response = {
                    "statusMessage": "Fetching cam URI failed with exception {}".format(
                        str(e)
                    ),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class CameraList(generics.ListAPIView):
    """

    API for getting list of required data
    @param : No params
    @returns: returns list
    @raises Exception: Not found exception

    """

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    serializer_class = CameraListSerializer
    pagination_class = None
    model = serializer_class.Meta.model

    def get_queryset(self):
        """
        Built-in method of ListApi View
        :return:
        """
        queryset = (
            self.model.objects.all(
            )
        ).order_by("-created_at")
        return queryset

    def list(self, request, *args, **kwargs):
        """
        For getting list of cameras
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            res = super(CameraList, self).list(request, *args, **kwargs)
            if res.data:
                aix_response = {
                        "statusMessage": "Data fetched successfully",
                        "errorStatus": False,
                        "data": res.data,
                        "statusCode": status.HTTP_200_OK,
                    }
            else:
                aix_response = {
                        "statusMessage": "No Data",
                        "errorStatus": False,
                        "data": res.data,
                        "statusCode": status.HTTP_200_OK,
                    }
        except Exception as err:
            aix_response = {
                    "statusMessage": str(err),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class CameraListWithLimit(generics.ListAPIView):
    """

    API for getting list of required data
    @param : No params
    @returns: returns list
    @raises Exception: Not found exception

    """

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    serializer_class = CameraListSerializer
    pagination_class = None
    model = serializer_class.Meta.model

    def get_queryset(self):
        """
        Built-in method of ListApi View
        :return:
        """
        queryset = (
                       self.model.objects.filter(Q(container_id__isnull=False) & Q(stream_url__isnull=False))
                   ).order_by("-created_at")[:4]
        return queryset

    def list(self, request, *args, **kwargs):
        """
        For getting list of cameras upto limit 4
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            res = super(CameraListWithLimit, self).list(request, *args, **kwargs)
            if res.data:
                aix_response = {
                        "statusMessage": "Data fetched successfully",
                        "errorStatus": False,
                        "data": res.data,
                        "statusCode": status.HTTP_200_OK,
                    }
            else:
                aix_response = {
                        "statusMessage": "No Data",
                        "errorStatus": False,
                        "data": res.data,
                        "statusCode": status.HTTP_200_OK,
                    }
        except Exception as err:
            aix_response = {
                    "statusMessage": str(err),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class CamDetailView(APIView):
    """
    File Cam detail view.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    serializer_class = CamDetailSerialzier

    def get(self, request):
        """
        For fetching detail of camera
        :param request:
        :return:
        """
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            id = request.query_params.get("id")
            if id:
                aix_response = CameraController.get_cam_detail(id=id)
            else:
                aix_response = {
                        "statusMessage": "Please provide id",
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "errorStatus": True,
                    }
        except Exception as e:
            aix_response = {
                    "statusMessage": "Fetching detail failed with exception {}".format(
                        str(e)
                    ),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class UpdateCamStatus(APIView):
    """
    Cam status detail view.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def patch(self, request):
        """
         Cam status changing
        :param request:
        :return:
        """
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            ip = request.data.get("ip")
            cam_status = request.data.get("status")
            if ip:
                update_status, exception_message, camera_object, aix_response = CameraController.update_camera_satus(ip=ip, cam_status=cam_status)
            else:
                aix_response = {
                        "statusMessage": "Please provide IP",
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "errorStatus": True,
                    }
        except Exception as e:
            aix_response = {
                    "statusMessage": "Unable to update status failed with exception {}".format(
                        str(e)
                    ),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class UpdateCamDetail(APIView):
    """
    Cam status detail view.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def patch(self, request):
        """
         Cam status changing
        :param ip:
        :param request:
        :return:
        """
        kafka_con = Kafka()
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            ip = request.data.get("ip")
            if Camera.objects.filter(ip=ip).first():
                data = request.data
                validated_data = CameraUpdateSerialzier(data=data)
                if validated_data.is_valid():
                    data = validated_data.data
                    data["user_role"] = RequestHandler.get_user_role(request=request)
                    data["service_type"] = RequestHandler.get_service_type(request=request)
                    data["is_stream"] = False
                    data["is_live_stream"] = False
                    if ip:
                        update_status, exception_message, camera_object, aix_response = CameraController.update_camera(ip=ip,
                                                                                                         data=data)
                        if update_status:
                            if camera_object.active_status is True:
                                kafka_data_for_camera = {
                                    "ip": camera_object.ip,
                                    "port": camera_object.port,
                                    "name": camera_object.camera_name,
                                    "username": camera_object.username,
                                    "password": camera_object.password,
                                    "threats": camera_object.threats,
                                    "is_drone_camera": camera_object.is_drone_camera,
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
                                    topic=os.getenv("KAFKA_CAMERA_TOPIC_UPDATE"),
                                    values=kafka_data_for_camera,
                                )
                                time.sleep(10)
                                kill_node_ports(streaming_port=camera_object.streaming_port,
                                                ai_streaming_port=camera_object.ai_streaming_port)

                    else:
                        aix_response = {
                                "statusMessage": "Please provide IP",
                                "data": [],
                                "statusCode": status.HTTP_400_BAD_REQUEST,
                                "errorStatus": True,
                            }
                else:
                    aix_response = {
                            "statusMessage": validated_data.errors,
                            "data": [],
                            "statusCode": status.HTTP_400_BAD_REQUEST,
                            "errorStatus": True,
                        }
            else:
                aix_response = {
                        "statusMessage": "Camera not found",
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "errorStatus": True,
                    }

        except Exception as e:
            aix_response = {
                    "statusMessage": "Unable to update status failed with exception {}".format(
                        str(e)
                    ),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class StartStream(APIView):
    """
    File uploading view.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        aix_response = {}
        """
        API for starting camera on camera
        :param request:
        :return:
        """
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            aix_response = CameraController.get_camera_stream(request=request)
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
            return Response(aix_response)


class CamEventsFilterView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        aix_response = {}
        try:
            ip = request.query_params.get("ip", None)
            search_obj = ElasticSearchHandler()
            filtered_data = search_obj.events_filter_by_ip(ip)
            aix_response = {
                    "statusMessage": "Query Searched Successfully!",
                    "data": filtered_data,
                    "statusCode": status.HTTP_200_OK,
                    "errorStatus": False,
                }
        except Exception as e:
            aix_response = {
                "statusMessage": f"{e}",
                "data": [],
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "errorStatus": True,
            }
        finally:
            return Response(aix_response)


class TestConnectionAddingCamera(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        aix_response = {}
        try:
            aix_response = CameraController.test_connection_adding_camera(request)
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class SearchCameraView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            aix_response = CameraController.search_camera(request)
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class CamAlertsFilterView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            ip = request.query_params.get("ip", None)
            search_obj = ElasticSearchHandler()
            filtered_data = search_obj.alerts_filter_by_ip(ip)
            aix_response = {
                    "statusMessage": "Query Searched Successfully!",
                    "data": filtered_data,
                    "statusCode": status.HTTP_200_OK,
                    "errorStatus": False,
                }
        except Exception as e:
            aix_response = {
                    "statusMessage": f"{e}",
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class CamEventAggregateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            ip = request.query_params.get("ip", None)
            camera_name = Camera.objects.filter(ip=ip).first()
            search_obj = ElasticSearchHandler()
            aix_response = search_obj.events_aggregation(ip, camera_name)
        except Exception as e:
            aix_response = {
                    "statusMessage": f"{e}",
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class CamThreatAlertView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            ip = request.query_params.get("ip", None)
            start_time = request.query_params.get("start_time", None)
            end_time = request.query_params.get("end_time", None)
            search_obj = ElasticSearchHandler()
            aix_response = search_obj.threat_alert_aggregation(ip, start_time, end_time)
        except Exception as e:
            aix_response = {
                    "statusMessage": f"{e}",
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class CamForceAlertView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            ip = request.query_params.get("ip", None)
            start_time = request.query_params.get("start_time", None)
            end_time = request.query_params.get("end_time", None)
            search_obj = ElasticSearchHandler()
            aix_response = search_obj.force_alert_aggregation(ip, start_time, end_time)
        except Exception as e:
            aix_response = {
                    "statusMessage": f"{e}",
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }

        finally:
            return Response(aix_response)


class CamAssetCountView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            ip = request.query_params.get("ip", None)
            start_time = request.query_params.get("start_time", None)
            end_time = request.query_params.get("end_time", None)
            required_cameras = RequestHandler.get_request_data(request, "required_cameras")
            required_events = RequestHandler.get_request_data(request, "required_events")
            search_obj = ElasticSearchHandler()
            aix_response = search_obj.asset_count_aggregation(ip, start_time, end_time, required_cameras, required_events)
        except Exception as e:
            aix_response = {
                    "statusMessage": f"{e}",
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class CamForceCountView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            start_time = request.query_params.get("start_time", None)
            end_time = request.query_params.get("end_time", None)
            search_obj = ElasticSearchHandler()
            aix_response = search_obj.force_count_aggregation(start_time, end_time)
        except Exception as e:
            aix_response = {
                    "statusMessage": f"{e}",
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class camLegendsCountView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            ip = request.query_params.get("ip", None)
            start_time = request.query_params.get("start_time", None)
            end_time = request.query_params.get("end_time", None)
            force = RequestHandler.get_request_data(request, "force")
            search_obj = ElasticSearchHandler()
            aix_response = search_obj.legend_count_aggregation(ip, start_time, end_time, force)
        except Exception as e:
            aix_response ={
                    "statusMessage": f"{e}",
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class ImageAlertPath(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            alert_id = request.query_params.get("alert_id", None)
            search_obj = ElasticSearchHandler()
            aix_response = search_obj.image_alert_path(alert_id)
        except Exception as e:
            aix_response = {
                    "statusMessage": f"{e}",
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class camImageAlertView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            ip = request.query_params.get("ip", None)
            start_time = request.query_params.get("start_time", None)
            end_time = request.query_params.get("end_time", None)
            search_obj = ElasticSearchHandler()
            aix_response = search_obj.image_alert_aggregation(ip, start_time, end_time)
        except Exception as e:
            aix_response = {
                    "statusMessage": f"{e}",
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class SinglePageGraphView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            ip = request.query_params.get("ip", None)
            required_events = RequestHandler.get_request_data(request, "required_events")
            search_obj = ElasticSearchHandler()
            aix_response = search_obj.single_page_graph_aggregation(ip, required_events)
        except Exception as e:
            aix_response = {
                    "statusMessage": f"{e}",
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)
