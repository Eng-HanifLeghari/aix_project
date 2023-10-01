from django.urls import re_path
from .socketconsumers import CameraConsumer, CameraConsumerGetStreamUrl, CameraAlertsAll, \
    HighAlertImage, AIXCAMHighPRIORITYALERTS, AIXCAMMediumPRIORITYALERTS, AIXCAMLowPRIORITYALERTS, \
    RestartCameraStreaming

# For websockets related to camera
websocket_urlpatterns = [
    re_path(r"^camera-detections", CameraConsumer.as_asgi()),
    re_path(r"^camera-stream-url", CameraConsumerGetStreamUrl.as_asgi()),
    re_path(r"^alerts", CameraAlertsAll.as_asgi()),
    re_path(r"^high-alert-notifications", AIXCAMHighPRIORITYALERTS.as_asgi()),
    re_path(r"^medium-alert-notifications", AIXCAMMediumPRIORITYALERTS.as_asgi()),
    re_path(r"^low-alert-notifications", AIXCAMLowPRIORITYALERTS.as_asgi()),
    re_path(r"^high-alert-image", HighAlertImage.as_asgi()),
    re_path(r"^restart-camera-streaming", RestartCameraStreaming.as_asgi())
]
