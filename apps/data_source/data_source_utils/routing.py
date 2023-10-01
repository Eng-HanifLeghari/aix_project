from django.urls import re_path
from .socketconsumers import (
    AIXImageConsumer,
    AIXVideoConsumer,
    AIXReconFixedImageConsumer,
    AIXReconDetectionsImageConsumer, BDMSocketConsumer,
)

websocket_urlpatterns = [
    re_path(r"^image", AIXImageConsumer.as_asgi()),
    re_path(r"^fixedReconImage", AIXReconFixedImageConsumer.as_asgi()),
    re_path(r"^detectionReconImage", AIXReconDetectionsImageConsumer.as_asgi()),
    re_path(r"^video", AIXVideoConsumer.as_asgi()),
    re_path(r"^bdm-socket", BDMSocketConsumer.as_asgi()),
]
