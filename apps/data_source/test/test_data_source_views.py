from io import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile
import pytest
from rest_framework.test import APIClient

client = APIClient()


@pytest.mark.django_db()
def test_upload_file(api_client):
    with open("/home/ali-jad/Downloads/army1.jpeg", "rb") as file:
        data = {
            "service_type": "object_detection",
            "file": SimpleUploadedFile(file.name, file.read(), content_type="image/jpeg")
        }
        headers = {'content_type': 'multipart/form-data'}
        response = api_client.post("/data-source/upload-file/", data=data, headers=headers)
        print("res: ", response.json())
        assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_all_files(api_client):
    response = api_client.get("/data-source/all-files/")
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_ai_services(api_client):
    response = api_client.get("/data-source/ai-services/")
    print(response)
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_detail_view(api_client):
    response = api_client.get("/data-source/detail-view/?id=1")
    print(response)
    assert response.json().get("statusCode") == 200

