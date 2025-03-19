import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from notifications.routing import websocket_urlpatterns  # 🔹 Import your routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studyhub.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Standard Django HTTP requests
    "websocket": AuthMiddlewareStack(  # Add WebSocket support
        URLRouter(websocket_urlpatterns)
    ),
})
