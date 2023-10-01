import json
import os
import random
import requests

from apps.camera.models import Camera


def open_port():
    port_open_response = None
    port_stream_response = None
    ai_port_response = None
    docker_port_ml_response = None
    try:
        for num in range(8888, 9999):
            port_open = random.randint(8889, 9998)
            port_stream = random.randint(8889, 9998)
            port_ai = random.randint(8889, 9998)
            docker_port_ml = random.randint(5400, 5500)
            if (port_open != port_stream) and (port_open != port_ai) and (port_stream != port_ai):
                ai_port_available = Camera.objects.filter(ai_streaming_port=port_ai).first()
                port_open_available = Camera.objects.filter(out_port=port_open).first()
                port_stream_available = Camera.objects.filter(streaming_port=port_stream).first()
                docker_port_ml_available = Camera.objects.filter(docker_port_ml=docker_port_ml).first()
                if port_open_available is None and port_stream_available is None and ai_port_available is None and docker_port_ml_available is None:
                    port_open_response = port_open
                    port_stream_response = port_stream
                    ai_port_response = port_ai
                    docker_port_ml_response = docker_port_ml
                    break
    except Exception as e:
        port_open_response = None
        port_stream_response = None
        ai_port_response = None
        docker_port_ml_response = None
    finally:
        return port_open_response, port_stream_response, ai_port_response, docker_port_ml_response


def kill_node_ports(streaming_port, ai_streaming_port):
    url = os.getenv("NODE_SERVER_DELETE_CAM_API")
    payload = json.dumps({
        "streaming_port": streaming_port,
        "ai_streaming_port": ai_streaming_port
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.status_code
