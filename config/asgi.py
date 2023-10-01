"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
import django

django.setup()

from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from apps.camera.camera_utils import routing as camera_routing
from apps.data_source.data_source_utils import routing as datasource_routing
from apps.reconnaissance.reconnaissance_utils import routing as reconnaissance_routing
from config.settings.channelsmiddleware import JwtAuthMiddlewareStack

# application = get_asgi_application()
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            JwtAuthMiddlewareStack(
                URLRouter(
                    datasource_routing.websocket_urlpatterns
                    + camera_routing.websocket_urlpatterns
                    + reconnaissance_routing.websocket_urlpatterns
                )
            )
        ),
    }
)
