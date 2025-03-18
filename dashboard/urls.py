from django.urls import path
from .views import DashboardStatsView

urlpatterns = [
    path('dashboard/<int:user_id>/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
