from django.utils import timezone
from django.db import models
from rest_framework import status
from .camera_utils.camera_enums import PROTOCOL_CHOICES
from ..data_source.models import AIServices
from ..users.models import User, UserRoles
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.


class Camera(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="camera_user")
    camera_name = models.CharField(null=False, max_length=25, default="Camera")
    ip = models.CharField(null=False, max_length=25)
    container_id = models.CharField(null=True, max_length=250, default=None)
    port = models.IntegerField(null=False)
    stream_url = models.CharField(max_length=250, default=None, null=True)
    camera_feed_url = models.CharField(max_length=250, default=None, null=True)
    user_role = models.ForeignKey(UserRoles, on_delete=models.SET_NULL, related_name="camera_user_role", null=True)
    service_type = models.ForeignKey(AIServices, on_delete=models.SET_NULL, related_name="service_type", null=True)
    protocol = models.CharField(max_length=4, choices=PROTOCOL_CHOICES, null=True)
    threats = models.JSONField(null=True)
    lat = models.DecimalField(max_digits=20, decimal_places=17, default=0.0)
    lng = models.DecimalField(max_digits=20, decimal_places=17, default=0.0)
    additional_parameters = models.CharField(max_length=500, null=True, blank=True)
    out_port = models.IntegerField(
        unique=True,
        default=None,
        null=True,
        validators=[MaxValueValidator(9999), MinValueValidator(8888)]
    )
    streaming_port = models.IntegerField(
        unique=True,
        null=True,
        default=None,
        validators=[MaxValueValidator(9999), MinValueValidator(8888)]
    )
    ai_streaming_port = models.IntegerField(
        unique=True,
        null=True,
        default=None,
        validators=[MaxValueValidator(9999), MinValueValidator(8888)]
    )
    docker_port_ml = models.IntegerField(
        unique=True,
        null=True,
        default=None,
        validators=[MaxValueValidator(5500), MinValueValidator(5400)]
    )
    is_drone_camera = models.BooleanField(null=True, default=False)
    active_status = models.BooleanField(null=True, default=True)
    is_stream = models.BooleanField(null=True, default=False)
    is_live_stream = models.BooleanField(default=False)
    username = models.CharField(max_length=30,null=True,blank=True)
    password = models.CharField(max_length=128,null=True,blank=True)
    location = models.CharField(max_length=228, null=True)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now_add=True, null=False)
    is_deleted = models.BooleanField(default=False)

    @classmethod
    def update_cam_urls(cls, ip, stream_url, container_id , camera_feed_url):
        """

        :param container_id:
        :param ip:
        :param stream_url:
        :return:
        """
        update_status = False
        exception_message = ""
        camera_object = ""
        try:
            obj = Camera.objects.filter(ip=ip).first()
            obj.stream_url = stream_url
            obj.camera_feed_url = camera_feed_url
            obj.container_id = container_id
            obj.save()
            camera_object = obj
            update_status = True
        except Exception as e:
            exception_message = str(e)
        finally:
            return update_status, exception_message, camera_object

    @classmethod
    def update_cam_status(cls, ip, cam_status):
        """

        :param ip:
        :param cam_status:
        :return:
        """
        update_status = False
        exception_message = ""
        camera_object = ""
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            obj = Camera.objects.filter(ip=ip).first()
            if obj:
                if cam_status:
                    obj.active_status = True
                elif not cam_status:
                    obj.active_status = False

                obj.is_stream = False
                obj.is_live_stream = False
                obj.updated_at = timezone.now()
                obj.save()
                camera_object = obj
                update_status = True
            else:
                aix_response.update(
                    {
                        "statusMessage": "Record not found",
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "errorStatus": True,
                    }
                )

        except Exception as e:
            exception_message = str(e)
        finally:
            return update_status, exception_message, camera_object

    @classmethod
    def update_cam_detail(cls, ip, data):
        """

        :param ip:
        :param data:
        :return:
        """
        update_status = False
        exception_message = ""
        camera_object = ""
        try:
            data["service_type"] = AIServices.objects.filter(pk=data.get("service_type")).first()
            Camera.objects.filter(ip=ip).update(**data)
            camera_object = Camera.objects.get(ip=ip)
            update_status = True
        except Exception as e:
            exception_message = str(e)
        finally:
            return update_status, exception_message, camera_object

    @classmethod
    def delete_cam(cls, ip):
        """
        FOr deleting cam
        :param ip:
        :return:
        """
        delete_status = False
        exception_message = ""
        cam_obj = None
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            obj = Camera.objects.filter(ip=ip).first()
            if obj:
                cam_obj = obj
                obj.delete()
                delete_status = True
            else:
                aix_response.update(
                    {
                        "statusMessage": "Camera record not found",
                        "errorStatus": False,
                        "data": [],
                        "statusCode": status.HTTP_200_OK,
                    }
                )
        except Exception as e:
            exception_message = str(e)
        finally:
            return delete_status, exception_message, cam_obj

    @classmethod
    def get_camera_uri(cls, ip, feed_type):
        """
        Getter for camera feed URI
        :param feed_type:
        :param ip:
        :return:
        """
        fetch_status = False
        exception_message = ""
        stream_uri = ""
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            obj = Camera.objects.filter(ip=ip).first()
            if obj:
                stream_uri = obj.stream_url
                fetch_status = True
            else:
                aix_response.update(
                    {
                        "statusMessage": "Camera record not found",
                        "errorStatus": False,
                        "data": [],
                        "statusCode": status.HTTP_200_OK,
                    }
                )
        except Exception as e:
            exception_message = str(e)
        finally:
            return fetch_status, exception_message, stream_uri


class CameraResponse(models.Model):
    camera = models.ForeignKey(
        Camera, on_delete=models.CASCADE, related_name="cameraresponse_camera"
    )
    detections = models.JSONField(null=False)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now_add=True, null=False)
    is_deleted = models.BooleanField(default=False)

# class Protocol(models.Model):
#     """
#     For defining services
#     """
#
#     id = models.IntegerField(primary_key=True)
#     protocol_key = models.PositiveSmallIntegerField(blank=True, null=True)
#     protocol_name = models.CharField(blank=True, null=True, max_length=40)
#
#     @classmethod
#     def get_protocol(cls, protocol_key=None):
#         return get_object_or_404(Protocol, protocol_key=protocol_key)
