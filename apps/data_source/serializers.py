from rest_framework import serializers
from customutils.data_handler import dict_keys_values_to_list
from apps.data_source.enums.type import DataTypeChoices
from apps.data_source.models import DataSource, DataSourceResponse, AIServices
from apps.users.models import UserProfile, User


class DataSourceSerializer(serializers.ModelSerializer):
    """
    Data source e.g.Image, Video serializer
    """

    upload_status = False
    data_source = None

    class Meta:
        model = DataSource
        fields = (
            "file_name",
            "type",
            "base_url",
            "user",
            "recon_fixed",
            "recon_detection",
            "drone_image",
            "drone_video",
            "service_type"
        )
        extra_kwargs = {"type": {"required": True}, "base_url": {"required": True}}

    @classmethod
    def create(cls, validated_data):
        """
        Method for creating record of uploaded file
        :param validated_data:
        :return: data object
        """
        try:
            data = validated_data.data
            data["processed_url"] = ""
            user = User.objects.get(id=data.get("user"))
            data["user"] = user
            data["service_type"] = AIServices.objects.filter(pk=data.get("service_type")).first()
            cls.data_source = DataSource.objects.create(**data)
            if cls.data_source:
                cls.upload_status = True
            # return data_source
        except:
            cls.upload_status = False
        finally:
            return cls.upload_status, cls.data_source


class DataSourceListSerializer(serializers.ModelSerializer):
    """
    Data source e.g.Image, Video serializer
    """

    upload_status = False
    response_data = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    service_type = serializers.SerializerMethodField()



    def get_service_type(self , obj):
        try:
            service_type = AIServices.objects.get(pk= obj.get("service_type")).service_key
            return service_type
        except:
            return None

    def get_created_at(self, obj):
        try:
            return obj.get("created_at").strftime("%d/%m/%Y , %H:%M:%S")
        except:
            return None

    def get_user_name(self, obj):
        try:
            return obj.get("user__username")
        except:
            pass

    def get_response_data(self, obj):
        try:
            if obj.get("type") == DataTypeChoices.IMAGE:
                response = (
                    DataSourceResponse.objects.filter(data_source_id=obj.get("id"))
                    .values(
                        "confidence",
                        "bbox",
                        "label",
                        "object_count",
                        "target",
                        "time_taken",
                    )
                    .first()
                )
                response = DataSourceResponseSerializer(data=response)
                if response.is_valid():
                    data = response.data
                    data = dict_keys_values_to_list(
                        data=data, keys=["confidence", "bbox", "label"]
                    )
                    return data
            elif obj.get("type") == DataTypeChoices.VIDEO:
                response = (
                    DataSourceResponse.objects.filter(data_source_id=obj.get("id"))
                    .values("video_metadata")
                    .first()
                )
                response = DataSourceResponseSerializerVideo(data=response)
                if response.is_valid():
                    data = response.data
                    return data
            elif obj.get("type") == DataTypeChoices.SATELLITE:
                response = (
                    DataSourceResponse.objects.filter(data_source_id=obj.get("id"))
                    .values("satellite_image_data")
                    .first()
                )
                response = DataSourceResponseSerializerSatellite(data=response)
                if response.is_valid():
                    data = response.data
                    return data
        except:
            return {}

    class Meta:
        model = DataSource
        fields = (
            "file_name",
            "type",
            "base_url",
            "processed_url",
            "user_id",
            "id",
            "response_data",
            "recon_fixed",
            "recon_detection",
            "user_name",
            "created_at",
            "drone_image",
            "drone_video",
            "service_type",
        )
        extra_kwargs = {"type": {"required": True}, "base_url": {"required": True}}


class DataSourceResponseSerializer(serializers.ModelSerializer):
    """
    Data source response serializer for creation
    """

    data_source_response = ""
    response_update_status = False

    class Meta:
        model = DataSourceResponse
        fields = ("confidence", "bbox", "label", "object_count", "target", "time_taken")
        # extra_kwargs = {
        #     'kafka_uuid': {'required': True},
        # }

    @classmethod
    def create(cls, validated_data):
        """
        Method for creating processed image record of uploaded file
        :param validated_data:
        :return: data object
        """
        try:
            data = validated_data.data
            kafka_uuid = validated_data.initial_data.get("kafka_uuid")
            data_source = DataSource.objects.get(kafka_uuid=kafka_uuid)
            data["data_source"] = data_source
            cls.data_source_response = DataSourceResponse.objects.create(**data)
            if cls.data_source_response:
                cls.response_update_status = True
        except Exception as e:
            cls.response_update_status = False
        finally:
            return cls.data_source_response, cls.response_update_status


class DataSourceResponseSerializerVideo(serializers.ModelSerializer):
    """
    Data source response serializer for creation
    """

    data_source_video_response = ""
    response_update_status = False

    class Meta:
        model = DataSourceResponse
        fields = ("video_metadata",)
        extra_kwargs = {
            "video_metadata": {"required": True},
        }

    @classmethod
    def create(cls, validated_data):
        """
        Method for creating processed image record of uploaded file
        :param validated_data:
        :return: data object
        """
        try:
            data = validated_data.data
            kafka_uuid = validated_data.initial_data.get("kafka_uuid")
            data_source = DataSource.objects.get(kafka_uuid=kafka_uuid)
            data["data_source"] = data_source
            cls.data_source_video_response = DataSourceResponse.objects.create(**data)
            if cls.data_source_video_response:
                cls.response_update_status = True
        except Exception as e:
            cls.upload_status = False
        finally:
            return cls.data_source_video_response, cls.response_update_status


class FinalDataSourceResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSourceResponse
        fields = "__all__"


class ImageFileDetailSerialzier(serializers.ModelSerializer):
    class Meta:
        model = DataSourceResponse
        fields = ("confidence", "bbox", "label", "object_count", "target", "time_taken")


class VideoDetailSerialzier(serializers.ModelSerializer):
    class Meta:
        model = DataSourceResponse
        fields = ("video_metadata",)


class DataSourceResponseSerializerSatellite(serializers.ModelSerializer):
    """
    Data source response serializer for creation
    """

    data_source_image_response_satellite = ""
    response_update_status = False

    class Meta:
        model = DataSourceResponse
        fields = ("satellite_image_data",)
        extra_kwargs = {
            "satellite_image_data": {"required": True},
        }

    @classmethod
    def create(cls, validated_data):
        """
        Method for creating processed image record of uploaded file
        :param validated_data:
        :return: data object
        """
        try:
            data = validated_data.data
            kafka_uuid = validated_data.initial_data.get("kafka_uuid")
            data_source = DataSource.objects.get(kafka_uuid=kafka_uuid)
            data["data_source"] = data_source
            cls.data_source_image_response_satellite = (
                DataSourceResponse.objects.create(**data)
            )
            if cls.data_source_image_response_satellite:
                cls.response_update_status = True
        except Exception as e:
            cls.response_update_status = False
        finally:
            return cls.data_source_image_response_satellite, cls.response_update_status



class AIServiceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIServices
        fields = ("service_key" , "service_name",)