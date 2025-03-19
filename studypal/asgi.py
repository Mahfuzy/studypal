import os
import django
from django.core.asgi import get_asgi_application

# Ensure Django initializes fully before anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studypal.settings')
django.setup()  # 🔹 This ensures apps are ready before importing anything

# Now you can import WebSocket routes
from notifications.routing import websocket_urlpatterns  # 🔹 Move this here

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
