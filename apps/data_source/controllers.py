import os
import pytz
from rest_framework import status
from customutils.request_handlers import RequestHandler, get_file_name_type
from customutils.custom_logging import MULHIM_LOGS
from customutils.kafka_utils import Kafka
from customutils.data_handler import (
    get_value_from_data,
    dict_keys_values_to_str,
    dict_keys_values_to_list,
)
from .enums.type import DataTypeChoices
from apps.data_source.serializers import (
    DataSourceSerializer,
    DataSourceResponseSerializer,
    DataSourceResponseSerializerVideo,
    FinalDataSourceResponseSerializer,
    ImageFileDetailSerialzier,
    VideoDetailSerialzier,
    DataSourceResponseSerializerSatellite,
)
from customutils.FTP_utils import FtpUpload
from .models import DataSource, DataSourceResponse
from django.utils import timezone

class FileUpload:
    FTP_connection_exception = False
    ftp_ = None
    base_url = ""
    response = ""
    kafka_data = ""

    @classmethod
    def save_files(cls, request, file_list):
        ftp_, ftp_connection_exception = FtpUpload.connect_ftp()
        kafka_con = Kafka()

        try:
            if not ftp_connection_exception:
                for file in file_list:
                    filename, file_extension = os.path.splitext(file.name)
                    if request.data.get("reconnaissance", "false").lower() == "true":
                        if file_extension not in [".tif", ".tiff"]:
                            aix_response = {
                                "statusMessage": "Reconnaissance mode is enable, Please upload tiff file",
                                "errorStatus": True,
                                "data": {"file_type": file_extension + " file"},
                                "statusCode": status.HTTP_400_BAD_REQUEST,
                            }
                    elif request.data.get("reconnaissance", "false").lower() == "false":
                        if file_extension in [".tif", ".tiff"]:
                            aix_response = {
                                "statusMessage": "Reconnaissance mode is disabled, Please upload jpeg file",
                                "errorStatus": True,
                                "data": {"file_type": file_extension + " file"},
                                "statusCode": status.HTTP_400_BAD_REQUEST,
                            }
                    dir_name = ftp_.create_directory_name()
                    filename, file_type = get_file_name_type(file=file)
                    if (
                            file_type == DataTypeChoices.IMAGE
                            or file_type == DataTypeChoices.SATELLITE
                    ):
                        cls.base_url = ftp_.add_target_image(
                            file, f"Images/{dir_name}", file_extension=file_extension
                        )
                        if file_extension in [".tif", ".tiff"]:
                            if file_extension == ".tif":
                                os.remove(file.name[:-3] + "jpeg")
                            elif file_extension == ".tiff":
                                os.remove(file.name[:-4] + "jpeg")
                    elif file_type == DataTypeChoices.VIDEO:
                        cls.base_url = ftp_.add_target_image(
                            file, f"Videos/{dir_name}", file_extension=file_extension
                        )
                    if not cls.base_url:
                        raise Exception
                    else:
                        request.data["base_url"] = ftp_.create_image_link(
                            directory=cls.base_url, file_name=file.name
                        )
                        if type(request.data["service_type"]) is str:
                            request.data["service_type"] = RequestHandler.get_service_type(request=request)
                        request.data["file_name"] = filename
                        request.data["type"] = file_type
                        request.data["user"] = RequestHandler.get_user_id(
                            request=request
                        )
                        recon_fixed = request.POST.get("recon_fixed", "false").lower()
                        recon_detection = request.POST.get(
                            "recon_detection", "false"
                        ).lower()
                        validated_data = DataSourceSerializer(data=request.data)
                        if validated_data.is_valid():
                            upload_status, data_source = DataSourceSerializer.create(
                                validated_data=validated_data
                            )
                            if upload_status:
                                reconnaissance = request.POST.get(
                                    "reconnaissance", "false"
                                ).lower()
                                if reconnaissance == "true":
                                    # recon_fixed = request.POST.get("recon_fixed", "false").lower()
                                    # recon_detection = request.POST.get("recon_detection", "false").lower()
                                    if recon_fixed == "true":
                                        cls.kafka_data = {
                                            "kafka_uuid": data_source.kafka_uuid.hex,
                                            "base_url": data_source.base_url,
                                            "file_type": data_source.type,
                                            "ai_Service": data_source.service_type.service_key,
                                            "reconnaissance": True,
                                            "recon_detection": False,
                                            "recon_fixed": True,
                                            "drone_image": False,
                                            "drone_video": False,
                                        }
                                    elif recon_detection == "true":
                                        cls.kafka_data = {
                                            "kafka_uuid": data_source.kafka_uuid.hex,
                                            "base_url": data_source.base_url,
                                            "file_type": data_source.type,
                                            "ai_Service": data_source.service_type.service_key,
                                            "reconnaissance": True,
                                            "recon_detection": True,
                                            "recon_fixed": False,
                                            "drone_image": False,
                                            "drone_video": False,
                                        }
                                else:
                                    if data_source.service_type.service_key == "drone_detection":
                                        if data_source.type == DataTypeChoices.IMAGE.value:
                                            cls.kafka_data = {
                                                "kafka_uuid": data_source.kafka_uuid.hex,
                                                "base_url": data_source.base_url,
                                                "file_type": data_source.type,
                                                "ai_Service": data_source.service_type.service_key,
                                                "reconnaissance": False,
                                                "recon_detection": False,
                                                "recon_fixed": False,
                                                "drone_image": True,
                                                "drone_video": False,
                                            }
                                        elif data_source.type == DataTypeChoices.VIDEO.value:
                                            cls.kafka_data = {
                                                "kafka_uuid": data_source.kafka_uuid.hex,
                                                "base_url": data_source.base_url,
                                                "file_type": data_source.type,
                                                "ai_Service": data_source.service_type.service_key,
                                                "reconnaissance": False,
                                                "recon_detection": False,
                                                "recon_fixed": False,
                                                "drone_image": False,
                                                "drone_video": True,
                                            }
                                    else:
                                        cls.kafka_data = {
                                            "kafka_uuid": data_source.kafka_uuid.hex,
                                            "base_url": data_source.base_url,
                                            "file_type": data_source.type,
                                            "ai_Service": data_source.service_type.service_key,
                                            "reconnaissance": False,
                                            "recon_detection": False,
                                            "recon_fixed": False,
                                            "drone_image": False,
                                            "drone_video": False,
                                        }
                                if file_type in [
                                    DataTypeChoices.IMAGE.value,
                                    DataTypeChoices.SATELLITE.value,
                                ]:
                                    kafka_con.kafka_producer(
                                        topic="mulhim-images", values=cls.kafka_data
                                    )
                                    MULHIM_LOGS.info("Produced Kafka event")
                                elif file_type == DataTypeChoices.VIDEO:
                                    kafka_con.kafka_producer(
                                        topic="mulhim-videos", values=cls.kafka_data
                                    )
                                    MULHIM_LOGS.info("Produced Kafka event")
                                if file_extension in [".tif", ".tiff"]:
                                    aix_response = {
                                            "statusMessage": "File uploaded Successfully",
                                            "errorStatus": False,
                                            "data": {
                                                "file_type": DataTypeChoices.SATELLITE,
                                                "recon_fixed": request.data.get(
                                                    "recon_fixed"
                                                ),
                                                "recon_detection": request.data.get(
                                                    "recon_detection"
                                                ),
                                            },
                                            "statusCode": status.HTTP_200_OK,
                                        }
                                else:
                                    aix_response = {
                                            "statusMessage": "File uploaded Successfully",
                                            "errorStatus": False,
                                            "data": {"file_type": data_source.type},
                                            "statusCode": status.HTTP_200_OK,
                                        }
                        else:
                            aix_response = {
                                    "statusMessage": "Invalid Data".format(
                                        validated_data.errors
                                    ),
                                    "data": [],
                                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    "errorStatus": True,
                                }
                ftp_.quit_server()
                return aix_response

            else:
                aix_response = {
                        "statusMessage": "FTP Connection failed with exception, {}".format(
                            ftp_
                        ),
                        "data": [],
                        "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "errorStatus": True,
                    }
                return aix_response
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
            return aix_response


class FileResponseController:
    data_source_response = ""
    response_update_status = False
    validated_data = ""
    is_image_data = False

    @classmethod
    def update_processed_url(cls, data):
        try:
            kafka_uuid = get_value_from_data(data=data, key="kafka_uuid")
            processed_url = get_value_from_data(data=data, key="processed_url")
            if processed_url:
                if data.get("file_type") == DataTypeChoices.SATELLITE:
                    filename, file_extension = os.path.splitext(
                        data.get("processed_url")
                    )
                    if file_extension == ".tif":
                        processed_url = processed_url[:-3] + "jpeg"
                    elif file_extension == ".tiff":
                        processed_url = processed_url[:-4] + "jpeg"
                    else:
                        processed_url = processed_url[:-3] + "jpeg"
                update_status, exception_message = DataSource.update_processedurl(
                    kafka_uuid=kafka_uuid, processed_url=processed_url
                )
                return update_status, exception_message
            else:
                return False, "Kafka data is not valid"

        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
            return aix_response

    @classmethod
    def save_datasource_response(cls, data):
        try:
            print("Data received in save_datasource_response_image controller")
            data = dict_keys_values_to_str(
                data=data, keys=["confidence", "bbox", "label"]
            )
            validated_data = DataSourceResponseSerializer(data=data)
            if validated_data.is_valid():
                validated_data.data.update({"kafka_uuid": data.get("kafka_uuid")})
                (
                    cls.data_source_response,
                    cls.response_update_status,
                ) = DataSourceResponseSerializer.create(validated_data=validated_data)
        except:
            pass
        finally:
            if cls.response_update_status:
                return cls.data_source_response, cls.response_update_status
            else:
                return {}, cls.response_update_status

    @classmethod
    def save_datasource_response_satellite(cls, data):
        try:
            print("Data received in save_datasource_response_satellite controller")
            # tod helper function
            validated_data = DataSourceResponseSerializerSatellite(data=data)
            if validated_data.is_valid():
                validated_data.data.update({"kafka_uuid": data.get("kafka_uuid")})
                (
                    cls.data_source_response,
                    cls.response_update_status,
                ) = DataSourceResponseSerializerSatellite.create(
                    validated_data=validated_data
                )
        except:
            pass
        finally:
            if cls.response_update_status:
                return cls.data_source_response, cls.response_update_status
            else:
                return {}, cls.response_update_status

    @classmethod
    def save_datasource_response_video(cls, meta_data):
        video_response_update_status = False
        cls.data_source_response = {}
        cls.response_update_status = False

        try:
            print("Data received in video save_datasource_response controller")
            validated_data = DataSourceResponseSerializerVideo(data=meta_data)
            if validated_data.is_valid():
                validated_data.data.update({"kafka_uuid": meta_data.get("kafka_uuid")})
                (
                    cls.data_source_response,
                    cls.response_update_status,
                ) = DataSourceResponseSerializerVideo.create(
                    validated_data=validated_data
                )
        except Exception as e:
            print("Exception in video save_data_source_response controller")
            cls.response_update_status = False
            cls.data_source_response = {}
        finally:
            return cls.data_source_response, cls.response_update_status

    @classmethod
    def create_response_for_channels(cls, data, datasource_object):
        try:
            data["base_url"] = datasource_object.data_source.base_url
            data["datasource_id"] = datasource_object.data_source_id
            data["user_id"] = datasource_object.data_source.user_id
            data["file_name"] = datasource_object.data_source.file_name
            data["service_type"] = datasource_object.data_source.service_type.service_key
            data["user_name"] = datasource_object.data_source.user.username
            data["created_at"] = str(timezone.localtime(datasource_object.data_source.created_at, pytz.timezone(os.getenv("TIME_ZONE"))).strftime("%d-%m-%Y %H:%M"))
            data.pop("status_code")
            data.pop("kafka_uuid")
            if datasource_object.data_source.type == DataTypeChoices.IMAGE:
                if not data.get("reconnaissance"):
                    data = dict_keys_values_to_list(
                        data=data, keys=["confidence", "bbox", "label"]
                    )
        except Exception as e:
            print("In create_response_for_channels ", str(e))
        finally:
            return data

    @classmethod
    def get_file_detail(cls, datasource_id):
        cls.is_image_data = False
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            data_obj = DataSourceResponse.objects.filter(
                data_source_id=datasource_id, data_source__is_processed=True
            )
            file_type = data_obj.first().data_source.type
            if file_type == DataTypeChoices.IMAGE:
                cls.validated_data = ImageFileDetailSerialzier(
                    data=data_obj.values().first()
                )
                cls.is_image_data = True
            elif file_type == DataTypeChoices.VIDEO:
                cls.validated_data = VideoDetailSerialzier(
                    data=data_obj.values().first()
                )
            if cls.validated_data.is_valid():
                detail = cls.validated_data.data
                if cls.is_image_data:
                    detail = dict_keys_values_to_list(
                        data=detail, keys=["confidence", "bbox", "label"]
                    )
                detail["processed_url"] = data_obj.first().data_source.processed_url
                detail["file_name"] = data_obj.first().data_source.file_name
                aix_response = {
                        "statusMessage": "Data Fetched Successfully",
                        "errorStatus": False,
                        "data": detail,
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
