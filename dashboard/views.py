from datetime import date
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from celery import shared_task
from .models import DashboardStats
from .serializers import DashboardStatsSerializer
from accounts.models import CustomUser
from study_assistant.ai_service import TaeAI
from rest_framework.permissions import IsAuthenticated
# ------------------------- Celery Tasks -------------------------

@shared_task
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

@shared_task
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

# ------------------------- API View -------------------------

class DashboardStatsView(APIView):
    """Retrieve and update a user's dashboard stats"""
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        stats, created = DashboardStats.objects.get_or_create(user=user)

        cache_key = f'dashboard_insights_{user_id}'
        insights = cache.get(cache_key)

        if not insights:
            generate_dashboard_insights.delay(user_id)
            insights = "Processing AI insights..."

        stats.ai_insights = insights
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        stats, created = DashboardStats.objects.get_or_create(user=user)
        data = request.data

        # Update only the fields provided
        stats.total_learning_time += data.get("learning_time", 0)
        stats.completed_courses += data.get("completed_courses", 0)
        stats.unfinished_courses += data.get("unfinished_courses", 0)
        stats.current_streak = data.get("current_streak", stats.current_streak)
        stats.longest_streak = max(stats.longest_streak, stats.current_streak)

        if data.get("next_exam_date"):
            stats.next_exam_date = data["next_exam_date"]

        stats.save()

        # Trigger AI recommendation task
        generate_dashboard_recommendations.delay(
            user_id, 
            data.get("learning_time", 0), 
            stats.completed_courses, 
            stats.unfinished_courses, 
            stats.current_streak
        )

        serializer = DashboardStatsSerializer(stats)
        return Response({
            "message": "Dashboard updated successfully!",
            "recommendations": "Processing AI recommendations...",
            "updated_stats": serializer.data
        }, status=status.HTTP_200_OK)
