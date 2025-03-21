from django.urls import path
from .views import DashboardStatsRetrieveView

urlpatterns = [
    path('dashboard/<int:user_id>/stats/', DashboardStatsRetrieveView.as_view(), name='dashboard-stats-retrieve'),
]
