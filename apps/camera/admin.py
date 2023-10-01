from django.contrib import admin

from apps.camera.models import Camera, CameraResponse
from apps.data_source.models import AIServices

# Register your models here.
admin.site.register(Camera)
admin.site.register(CameraResponse)

