from django.db import models


class Notification(models.Model):
    alert_id = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField(max_length=1024, null=True, blank=True)
    threat = models.CharField(max_length=255, null=True, blank=True)
    priority = models.CharField(max_length=255, null=True, blank=True)
    camera_ip = models.CharField(max_length=25, null=True, blank=True)
    is_read = models.BooleanField(default=False, null=True, blank=True)
    camera_name = models.CharField(max_length=255, null=True, blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    lng = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now_add=True, null=False)
    is_view = models.BooleanField(default=False, null=True, blank=True)
    object_id = models.CharField(max_length=255, null=True, blank=True)



    @classmethod
    def notification_list(cls, priority=None):
        if priority is not None:

            queryset=Notification.objects.filter(priority=priority, is_view=True).order_by("-created_at")
            return queryset
        queryset=Notification.objects.filter(is_view=True).order_by("-created_at")
        return queryset
    @classmethod
    def create(cls, notification_data):
        try:
            Notification.objects.create(**notification_data)
        except:
            pass
