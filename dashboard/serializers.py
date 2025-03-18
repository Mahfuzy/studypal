from rest_framework import serializers
from .models import DashboardStats
from accounts.serializers import UserSerializer

class DashboardStatsSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = DashboardStats
        fields = "__all__"
