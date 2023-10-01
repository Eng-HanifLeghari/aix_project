from rest_framework import serializers
from apps.camera.models import Camera, CameraResponse
from apps.data_source.models import AIServices


class CameraAddSerializer(serializers.ModelSerializer):
    """
    For adding camera
    """

    camera_added = False
    camera_response = ""
    user_role = serializers.SerializerMethodField()
    service_type = serializers.SerializerMethodField()

    def get_user_role(self, obj):
        try:
            return obj.user_role.role_name
        except:
            pass

    def get_service_type(self, obj):
        try:
            return obj.service_type.service_name
        except:
            pass

    class Meta:
        model = Camera
        fields = (
            "ip",
            "location",
            "username",
            "user_role",
            "service_type",
            "password",
            "id",
            "port",
            "camera_name",
            "lat",
            "lng",
            "threats",
            "protocol",
            "out_port",
            "streaming_port",
            "ai_streaming_port",
            "additional_parameters",
            "docker_port_ml",
            "is_drone_camera"
        )
        extra_kwargs = {
            "ip": {"required": True},
        }

    def validate(self, data):
        if not data.get("is_drone_camera") and Camera.objects.filter(ip=data["ip"]).exists():
            raise serializers.ValidationError(f"This ip:{data['ip']} is already exists!")
        return data

    @classmethod
    def create(cls, validated_data):
        """
        FOr adding camera
        :param validated_data:
        :return:
        """
        try:
            validated_data["service_type"] = AIServices.objects.filter(pk=validated_data.get("service_type")).first()
            active_camera_count = Camera.objects.filter(active_status=True).count()
            if active_camera_count > 4:
                validated_data["active_status"] = False
            cls.camera_response = Camera.objects.create(**validated_data)
            if cls.camera_response:
                cls.camera_added = True
        except Exception as e:
            cls.camera_added = False
        finally:
            return (
                cls.camera_added,
                cls.camera_response,
            )


class CameraListSerializer(serializers.ModelSerializer):
    """
    For listing all cameras
    """

    camera_added = False
    camera_response = ""
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    ai_service = serializers.SerializerMethodField()

    def get_role(self, obj):
        try:
            return obj.user_role.role_name
        except:
            return None

    def get_lat(self, obj):
        try:
            return float(obj.lat)
        except:
            return None

    def get_lng(self, obj):
        try:
            return float(obj.lng)
        except:
            return None

    def get_ai_service(self, obj):
        try:
            return obj.service_type.service_name
        except:
            return None

    class Meta:
        model = Camera
        fields = (
            "ip",
            "location",
            "username",
            "password",
            "id",
            "port",
            "camera_name",
            "lat",
            "lng",
            "threats",
            "protocol",
            "out_port",
            "role",
            "ai_service",
            "active_status"
        )
        # fields = ("id","ip", "username", "role", "ai_service", "location","active_status")


class CameraDetectionsResponseSerializer(serializers.ModelSerializer):
    """
    Data source response serializer for creation
    """

    camera_response = {}
    save_status = False

    class Meta:
        model = CameraResponse
        fields = ("detections",)
        extra_kwargs = {
            "detections": {"required": True},
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
            ip = validated_data.initial_data.get("camera_ip")
            camera = Camera.objects.filter(ip=ip).first()
            data["camera"] = camera
            cls.camera_response = CameraResponse.objects.create(**data)
            if cls.camera_response:
                cls.save_status = True
        except Exception as e:
            cls.save_status = False
        finally:
            return cls.camera_response, cls.save_status


class CamDetailSerialzier(serializers.ModelSerializer):
    user_role = serializers.SerializerMethodField()
    service_type = serializers.SerializerMethodField()

    def get_user_role(self, obj):
        try:
            return obj.user_role.role_key
        except:
            return None

    def get_service_type(self, obj):
        try:
            return obj.service_type.service_key
        except:
            return None

    class Meta:
        model = Camera
        fields = (
            "user_id",
            "camera_name",
            "ip",
            "port",
            "stream_url",
            "lat",
            "lng",
            "username",
            "password",
            "location",
            "user_role",
            "service_type",
            "streaming_port",
            "ai_streaming_port",
        )


class CameraUpdateSerialzier(serializers.ModelSerializer):
    """
    For adding camera
    """

    camera_added = False
    camera_response = ""

    class Meta:
        model = Camera
        fields = (
            "location",
            "username",
            "password",
            "id",
            "port",
            "camera_name",
            "lat",
            "lng",
            "threats",
            "protocol",
        )
        extra_kwargs = {
            "ip": {"required": True},
        }


class CameraSearchSerializer(serializers.ModelSerializer):
    """
    For adding camera
    """

    camera_added = False
    camera_response = ""
    role = serializers.SerializerMethodField()
    ai_service = serializers.SerializerMethodField()

    def get_role(self, obj):
        try:
            return obj.user_role.role_name
        except:
            pass

    def get_ai_service(self, obj):
        try:
            return obj.service_type.service_name
        except:
            pass

    class Meta:
        model = Camera
        fields = (
            "ip",
            "location",
            "username",
            "role",
            "ai_service",
            "password",
            "id",
            "port",
            "camera_name",
            "active_status",
            "lat",
            "lng",
            "threats",
            "protocol",
            "out_port",
            "streaming_port",
            "ai_streaming_port",
            "additional_parameters"
        )
        extra_kwargs = {
            "ip": {"required": True},
        }

