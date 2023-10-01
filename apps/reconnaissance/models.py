from django.db import models
from django.contrib.gis.db import models as gismodels
import uuid


class ImageServerData(models.Model):
    filename = models.CharField(max_length=100, blank=True, null=True)
    file_path_local = models.CharField(max_length=500, blank=True, null=True)
    wms_url = models.CharField(max_length=1000, blank=True, null=True)
    area_name = models.CharField(max_length=500, blank=True, null=True)
    date_of_acquisition = models.DateField(blank=True, null=True)
    resolution = models.IntegerField(blank=True, null=True)
    data_source = models.IntegerField(blank=True, null=True)
    base_folder = models.CharField(max_length=1024, null=True, blank=True)
    layer_name = models.CharField(max_length=1024, null=True, blank=True)
    image_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.filename

    class Meta:
        verbose_name = "Image Server Data"
        verbose_name_plural = "Image Server Data"
        ordering = ["-created_at"]


class FootprintsGeometry(models.Model):
    geometry = gismodels.GeometryField(srid=4326, blank=True, null=True)
    image = models.OneToOneField(ImageServerData, on_delete=models.CASCADE, related_name="image_server_data")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.image.filename

    class Meta:
        verbose_name = "Foot Print Geometry"
        verbose_name_plural = "Foot Print Geometry"
        ordering = ["-created_at"]

    @classmethod
    def image_server_list(cls, location=None, data_source=None):
        if location is not None:
            queryset = FootprintsGeometry.objects.filter(image__area_name__icontains=location, image__data_source=data_source).order_by(
                "-created_at")
            return queryset
        queryset = ImageServerData.objects.all()
        return queryset


class ReconnaissanceAIServices(models.Model):
    id = models.IntegerField(primary_key=True)
    service_key = models.CharField(blank=True, null=True, max_length=40)
    service_name = models.CharField(blank=True, null=True, max_length=40)

    def __str__(self):
        return self.service_name

    class Meta:
        verbose_name = "Reconnaissance AI Service"
        verbose_name_plural = "Reconnaissance AI Services"


class ReconnaissanceAIResults(models.Model):
    STATUS = [
        ("processing", "Processing"),
        ("failed", "Failed"),
        ("completed", "Completed")
    ]
    kafka_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, choices=STATUS, default="processing")
    complete_ai_date = models.DateTimeField(null=True, blank=True)
    image = models.ForeignKey(ImageServerData, on_delete=models.CASCADE, related_name="reconnaissance_image")
    reconnaissance_ai_service = models.ForeignKey(ReconnaissanceAIServices, on_delete=models.CASCADE, related_name="reconnaissance_services")
    is_processing = models.BooleanField(default=False)
    geojson_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.filename

    class Meta:
        verbose_name = "Reconnaissance AI Result"
        verbose_name_plural = "Reconnaissance AI Results"
