import pytest
from rest_framework.test import APIClient

client = APIClient()


@pytest.mark.django_db()
def test_all_notifications(api_client):
    response = api_client.get("/notifications/all-notifications/")
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_update_read_status(api_client):
    data = {
        "notification_ids": [1, 2, 3, 4]
    }
    response = api_client.patch("/notifications/update-read-status/", data=data)
    assert response.json().get("statusCode") == 200

