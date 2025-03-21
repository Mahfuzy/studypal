from django.urls import path
from .views import TaeAIView, TaskStatusView

urlpatterns = [
    path('ask/', TaeAIView.as_view(), name='ask-ai'),
    path('task-status/<str:task_id>/', TaskStatusView.as_view(), name='task-status'),
]
