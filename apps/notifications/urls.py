from django.urls import re_path
from apps.notifications.views import NotificationView, UpdateNotificationStatus

urlpatterns = [
    re_path(r"^all-notifications/", NotificationView.as_view(), name="all-notifications"),
    re_path(r"^update-read-status/", UpdateNotificationStatus.as_view(), name="update-notification-status"),
]
