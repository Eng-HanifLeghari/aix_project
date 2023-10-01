from django.urls import re_path
from apps.data_source.views import *

urlpatterns = [
    # User management
    re_path(r"^upload-file/", FileUploadView.as_view(), name="file_upload_view"),
    re_path(r"^all-files/", FilesList.as_view(), name="get_file_view"),
    re_path(r"^ai-services/", AIServicesList.as_view(), name="get_ai_services_view"),
    re_path(r"^detail-view/", FileDetailView.as_view(), name="get_file_view"),
]
