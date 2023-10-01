from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.data_source.models import AIServices
from apps.users.models import User, UserRoles

import pytest


@pytest.fixture
def api_client():
    AIServices.objects.get_or_create(id=1, service_key="object_detection", service_name="Object Detection")
    UserRoles.objects.get_or_create(id=1, role_key=1, role_name="Mission Commander")
    user = User.objects.create_superuser('admin@email.com', 'admin', "Admin@123", is_enable=True)
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture()
def add_camera(api_client):
    data = {
        "ip": "10.100.160.112",
        "location": "Islamabad, Pakistan",
        "username": "",
        "additional_parameters": "live/test.flv",
        "password": "",
        "port": "1935",
        "is_drone_camera": True,
        "camera_name": "Drone Camera",
        "role_key": 1,
        "service_type": "object_detection",
        "protocol": "rtmp",
        "threats": {"1": 3, "8": 1},
        "lat": 12.2131,
        "lng": 41.128641
    }
    response = api_client.post("/camera/add-camera/", data=data, format="json")
    return response
