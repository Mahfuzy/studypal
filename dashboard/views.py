from datetime import date
from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from .models import DashboardStats
from .serializers import DashboardStatsSerializer
from accounts.models import CustomUser
from study_assistant.ai_service import TaeAI
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# ------------------------- Helper Functions -------------------------

def generate_dashboard_insights(user_id):
    """AI-generated learning progress analysis."""
    user = CustomUser.objects.filter(id=user_id).first()
    if not user:
        return "User not found."

    stats = DashboardStats.objects.filter(user=user).first()
    if not stats:
        return "Dashboard stats not found."

    cache_key = f'dashboard_insights_{user_id}'
    
    # Check if cached insights exist
    existing_insights = cache.get(cache_key)
    if existing_insights and stats.ai_insights == existing_insights:
        return "Insights already generated."

    ai_assistant = TaeAI()
    insights = ai_assistant.process_text(
        f"Analyze learning stats:\n"
        f"Total Learning Time: {stats.total_learning_time} minutes\n"
        f"Completed Courses: {stats.completed_courses}\n"
        f"Current Streak: {stats.current_streak} days\n"
        f"Next Exam Date: {stats.next_exam_date}"
    )

    stats.ai_insights = insights
    stats.save()
    cache.set(cache_key, insights, timeout=3600)  # Cache for 1 hour
    return insights

def generate_dashboard_recommendations(user_id, learning_time, completed_courses, unfinished_courses, current_streak):
    """AI-generated learning recommendations based on latest stats."""
    user = CustomUser.objects.filter(id=user_id).first()
    if not user:
        return "User not found."

    stats = DashboardStats.objects.filter(user=user).first()
    if not stats:
        return "Dashboard stats not found."

    cache_key = f'dashboard_recommendations_{user_id}'

    ai_assistant = TaeAI()
    recommendations = ai_assistant.process_text(
        f"Generate learning recommendations:\n"
        f"Recent Learning Time: {learning_time} minutes\n"
        f"Current Streak: {current_streak} days\n"
        f"Courses Progress: {completed_courses} completed, {unfinished_courses} in progress"
    )

    stats.ai_recommendations = recommendations
    stats.save()
    cache.set(cache_key, recommendations, timeout=3600)  # Cache for 1 hour
    return recommendations

# ------------------------- API Views -------------------------

class DashboardStatsRetrieveView(generics.RetrieveAPIView):
    """Retrieve a user's dashboard stats with AI-powered insights."""
    permission_classes = [IsAuthenticated]
    serializer_class = DashboardStatsSerializer
    lookup_field = 'user_id'
    lookup_url_kwarg = 'user_id'

    def get_object(self):
        user = get_object_or_404(CustomUser, id=self.kwargs['user_id'])
        stats, created = DashboardStats.objects.get_or_create(user=user)

        cache_key = f'dashboard_insights_{self.kwargs["user_id"]}'
        insights = cache.get(cache_key)

        if not insights:
            insights = generate_dashboard_insights(self.kwargs['user_id'])

        stats.ai_insights = insights
        return stats