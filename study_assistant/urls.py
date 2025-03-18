from django.urls import path
from .views import TaeAIView

urlpatterns = [
    path('ask/', TaeAIView.as_view(), name='ask-ai'),
]
