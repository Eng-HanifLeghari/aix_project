import pytest
from rest_framework.test import APIClient

from apps.users.models import User

client = APIClient()


@pytest.mark.django_db()
def test_user_login(api_client):
    payload = {
        "email": "admin@email.com",
        "password": "Admin@123"
    }
    response = client.post("/users/login/", data=payload)
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_user_register(api_client):
    payload = {
        "member_id": "d2jkj3111",
        "user": {
            "id": "",
            "username": "Staging",
            "email": "staging12@email.com",
            "role": 1,
            "is_enable": True,
            "password": "staging123",
            "password2": "staging123"
        }
    }
    response = api_client.post("/users/signup/", data=payload, format="json")
    assert response.json().get("statusCode") == 201


@pytest.mark.django_db()
def test_update_user(api_client):
    payload = {
        "user":{
            "first_name": "first",
            "last_name": "last",
            "is_enable": True,
            "role": 1
        },
        "title" : "staging1",
        "address" : "H-131",
        "dob" : "1996-02-13",
        "country" : "Paistani",
        "city" : "islamabad",
        "zip" : "11",
        "phone": "11"
    }
    user_id = User.objects.get(email="admin@email.com").id
    response = api_client.patch(f"/users/update-user/{user_id}/", data=payload, format='json')
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_user_status(api_client):
    response = api_client.get("/users/user-status/1/")
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_all_users(api_client):
    response = api_client.get("/users/all-users/")
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_update_pass(api_client):
    data = {
        "enter_new_password": "staging123",
        "confirm_password": "staging123"
    }
    response = api_client.put("/users/update-pass/", data=data)
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_user_roles(api_client):
    response = api_client.get("/users/user-roles/")
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_email_checker(api_client):
    payload = {
        "email": "admin@gmail.com"
    }
    response = api_client.post("/users/email-checker/", data=payload)
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_delete_user(api_client):
    payload = {
        "email": "admin@gmail.com"
    }
    response = api_client.delete("/users/delete-user/1/", data=payload)
    assert response.json().get("statusCode") == 200
