from django.urls import path
from .consumers import AIProcessingConsumer

websocket_urlpatterns = [
    path("ws/task_status/<str:task_id>/", AIProcessingConsumer.as_asgi()),
]
