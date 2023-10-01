import uuid
from django.db import models
from django.utils import timezone
from .enums.type import DataTypeChoices
from django.shortcuts import get_object_or_404
from ..users.models import User


class AIServices(models.Model):
    """
    For defining services
    """

    id = models.IntegerField(primary_key=True)
    service_key = models.CharField(blank=True, null=True, max_length=40)
    service_name = models.CharField(blank=True, null=True, max_length=40)

    @classmethod
    def get_service(cls, service_key=None):
        return get_object_or_404(AIServices, service_key=service_key)


class DataSource(models.Model):
    """
    Model for getting data source
    """

    type = models.CharField(
        max_length=2,
        choices=DataTypeChoices.choices,
        default=DataTypeChoices.VIDEO,
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user", null=True
    )
    # user = models.ForeignKey= settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    file_name = models.CharField(max_length=255, default=None)
    base_url = models.CharField(max_length=200)
    processed_url = models.CharField(max_length=200, default=None, null=True)
    recon_fixed = models.BooleanField(default=False)
    drone_image = models.BooleanField(default=False)
    drone_video = models.BooleanField(default=False)
    service_type = models.ForeignKey(AIServices, on_delete=models.SET_NULL, related_name="data_service_type", null=True)
    recon_detection = models.BooleanField(default=False)
    kafka_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(db_index=True)
    updated_at = models.DateTimeField(db_index=True, null=False)
    is_deleted = models.BooleanField(default=False)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        """For getting type of data"""
        return "{}".format(self.type)

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(DataSource, self).save(*args, **kwargs)

    @classmethod
    def update_processedurl(cls, kafka_uuid, processed_url):
        update_status = False
        exception_message = ""
        try:
            obj = DataSource.objects.get(kafka_uuid=kafka_uuid)
            obj.processed_url = processed_url
            obj.is_processed = True
            obj.save()
            update_status = True
        except Exception as e:
            exception_message = str(e)
        finally:
            return update_status, exception_message

    @classmethod
    def save_base_url(self, base_url):
        """
        Setter for saving base_url
        :param base_url:
        :return:
        """
        self.base_url = base_url


class DataSourceResponse(models.Model):
    data_source = models.ForeignKey(
        DataSource, on_delete=models.CASCADE, related_name="datasource"
    )
    confidence = models.TextField(null=True)
    object_count = models.JSONField(null=True)
    label = models.TextField(null=True)
    bbox = models.TextField(null=True)
    target = models.TextField(null=True)
    time_taken = models.CharField(null=True, max_length=30)
    video_metadata = models.JSONField(null=True)
    satellite_image_data = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now_add=True, null=False)
    is_deleted = models.BooleanField(default=False)



