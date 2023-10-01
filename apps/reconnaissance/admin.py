from django.contrib import admin
from apps.reconnaissance.models import FootprintsGeometry, ImageServerData, ReconnaissanceAIServices, ReconnaissanceAIResults


@admin.register(FootprintsGeometry)
class FootprintGeometryAdmin(admin.ModelAdmin):
    list_display = ["id", "geometry", "image", "created_at", "updated_at"]


@admin.register(ImageServerData)
class FootImageServerDataAdmin(admin.ModelAdmin):
    list_display = ["id", "filename", "file_path_local", "wms_url", "area_name", "date_of_acquisition", "resolution",
                    "data_source", "base_folder", "image_uuid", "created_at", "updated_at"]


@admin.register(ReconnaissanceAIServices)
class ReconnaissanceAIServicesAdmin(admin.ModelAdmin):
    list_display = ["id", "service_key", "service_name"]


@admin.register(ReconnaissanceAIResults)
class ReconnaissanceAIResultsAdmin(admin.ModelAdmin):
    list_display = ["id", "kafka_uuid", "status", "image"]

