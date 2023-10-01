from django.urls import re_path, path
from apps.reconnaissance.reconnaissance_utils.socketconsumers import ReconnaissanceAIResultConsumer, \
    ReconnaissanceAIProcessingConsumer

websocket_urlpatterns = [
    re_path(r"^reconnaissance_ai_results", ReconnaissanceAIResultConsumer.as_asgi()),
    re_path(r"^reconnaissance_ai_processing", ReconnaissanceAIProcessingConsumer.as_asgi()),
]
