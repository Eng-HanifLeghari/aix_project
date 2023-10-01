from rest_framework import serializers
from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    @staticmethod
    def get_created_at(obj):
        try:
            return obj.created_at.strftime('%d-%m-%Y %H:%M:%S')
        except Exception as e:
            pass

    @staticmethod
    def get_updated_at(obj):
        try:
            return obj.updated_at.strftime('%d-%m-%Y %H:%M:%S')
        except Exception as e:
            pass

    class Meta:
        model = Notification
        # fields = "__all__"

        fields = ("id",
                  "created_at",
                  "text",
                  "threat",
                  "priority",
                  "camera_ip",
                  "camera_name",
                  "lat",
                  "lng",
                  "is_read",
                  "alert_id",
                  "object_id",
                  "updated_at",)

    # fields = "__all__"
