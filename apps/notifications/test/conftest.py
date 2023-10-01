from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User, UserRoles

import pytest


@pytest.fixture
def api_client():
    UserRoles.objects.get_or_create(id=1, role_key=1, role_name="Mission Commander")
    user = User.objects.create_superuser('admin@email.com', 'admin', "Admin@123", is_enable=True)
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client