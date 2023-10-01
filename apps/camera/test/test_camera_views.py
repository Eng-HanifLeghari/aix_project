import pytest


@pytest.mark.django_db()
def test_add_camera(api_client):
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
    assert response.json().get("statusCode") == 201


@pytest.mark.django_db()
def test_update_camera(api_client, add_camera):
    data = {
        "ip": "10.100.160.112",
        "location": "Islamabad, Pakistan",
        "username": "",
        "additional_parameters": "live/test.flv",
        "password": "",
        "port": "1935",
        "service_type": "object_detection",
    }
    response = api_client.patch("/camera/update-camera/", data=data, format="json")
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_cam_status(api_client, add_camera):
    data = {
        "ip": "10.100.160.112",
        "status": False
    }
    response = api_client.patch("/camera/cam-status/", data=data)
    assert response.json().get("statusCode") == 201


@pytest.mark.django_db()
def test_cameras_limit(api_client):
    response = api_client.get("/camera/cameras-limit/")
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_all_cameras(api_client):
    response = api_client.get("/camera/all-cameras/")
    assert response.status_code == 200


@pytest.mark.django_db()
def test_cam_detail(api_client):
    response = api_client.get(f"/camera/cam-detail/?id=1")
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_delete_camera(api_client):
    data = {
        "camera_ip": "192.168.24.233"
    }
    response = api_client.delete("/camera/delete-camera/", data=data)
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_multiple_delete_camera(api_client, add_camera):
    data = {
        "camera_ip_list": "['10.100.160.112']"
    }
    response = api_client.delete("/camera/multiple-delete-camera/", data=data)
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_camera_uri(api_client):
    data = {
        "feed_type": "img",
        "camera_ip": "192.168.23.166"
    }
    response = api_client.get("/camera/camera-uri/", data=data)
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_start_stream(api_client, add_camera):
    data = {
        "camera_ip": "10.100.160.112"
    }
    response = api_client.post("/camera/start-stream/", data)
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_cam_events_filtration(api_client):
    response = api_client.get("/camera/cam-events-filtration/")
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_test_camera_connection(api_client):
    data = {
        "ip": "192.168.23.166",
        "port": "554",
        "protocol": "rtsp",
        "username": "admin",
        "password": "Rapidev321",
        "additional_params": "realmonitor?channel=1%26subtype=0"
    }
    response = api_client.post("/camera/test-camera-connection/", data=data)
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_search_camera(api_client):
    data = {
        "search_query": "admin"
    }
    response = api_client.post("/camera/search-camera/", data=data)
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_cam_threat_alert_aggregation(api_client):
    response = api_client.get("/camera/cam_threat_alert_aggregation/")
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_cam_alerts_filtration(api_client):
    response = api_client.get(f"/camera/cam-alerts-filtration/?ip={'192.168.23.157'}")
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_cam_event_aggregation(api_client):
    response = api_client.get("/camera/cam-event-aggregation/")
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_cam_force_alert_aggregation(api_client):
    response = api_client.get("/camera/cam_force_alert_aggregation/")
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_cam_asset_count_aggregation(api_client):
    data = {
        "required_events": [1, 2, 3, 4, 5, 6, 7, 8],
        "required_cameras": ["192.168.23.157"]
    }
    response = api_client.post("/camera/cam_asset_count_aggregation/", data=data)
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_cam_force_count_aggregation(api_client):
    response = api_client.get(f"/camera/cam_force_count_aggregation/?ip={'192.168.23.157'}")
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_cam_legend_count_aggregation(api_client):
    data = {
        "force": [1, 2, 3, 4, 5, 8]
    }
    response = api_client.post("/camera/cam_legend_count_aggregation/?ip='10.100.160.112'", data=data)
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_cam_image_alert_aggregation(api_client):
    response = api_client.get("/camera/cam_image_alert_aggregation/")
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_image_alert_path(api_client):
    data = {
        "index": "streamdetectionsalerts_",
        "alert_id": "threat_value",
        "value": 2
    }
    response = api_client.get("/camera/image-alert-path/", data=data)
    assert response.json().get("statusCode") == 200


@pytest.mark.django_db()
def test_cam_single_page_graph_aggregation(api_client):
    data = {
        "required_events": [1, 2, 3, 4, 5, 6, 7, 8]
    }
    response = api_client.post("/camera/cam_single_page_graph_aggregation/?ip='10.160.100.112'", data=data)
    assert response.json().get("statusCode") == 200
