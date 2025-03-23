from django.urls import path
from .consumers import TaeAIConsumer

websocket_urlpatterns = [
    path("ws/ai_chat/", TaeAIConsumer.as_asgi()),
]
