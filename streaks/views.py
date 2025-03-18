from datetime import date
from django.core.cache import cache
from celery import shared_task
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import StudyStreak, Achievement, XPSystem, Badge, Leaderboard
from .serializers import (
    StudyStreakSerializer, AchievementSerializer, XPSystemSerializer,
    BadgeSerializer, LeaderboardSerializer
)
from study_assistant.ai_service import TaeAI  

# ---------------------- Celery Tasks ----------------------

@shared_task
def generate_streak_insights(streak_id):
    streak = StudyStreak.objects.filter(id=streak_id).first()
    if not streak:
        return "Streak not found."

    cache_key = f'streak_insights_{streak_id}'
    
    existing_insights = cache.get(cache_key)
    if existing_insights and streak.ai_insights == existing_insights:
        return "Insights already generated."

    ai_assistant = TaeAI()
    insights = ai_assistant.process_text(
        f"Generate streak motivation:\nCurrent streak: {streak.current_streak} days"
    )

    streak.ai_insights = insights
    streak.save()
    cache.set(cache_key, insights, timeout=3600)
    return insights

@shared_task
def generate_achievement_insights(achievement_id):
    achievement = Achievement.objects.filter(id=achievement_id).first()
    if not achievement:
        return "Achievement not found."

    cache_key = f'achievement_insights_{achievement_id}'
    
    existing_insights = cache.get(cache_key)
    if existing_insights and achievement.ai_insights == existing_insights:
        return "Insights already generated."

    ai_assistant = TaeAI()
    insights = ai_assistant.process_text(
        f"Generate achievement tips:\nTitle: {achievement.title}\nCriteria: {achievement.criteria}"
    )

    achievement.ai_insights = insights
    achievement.save()
    cache.set(cache_key, insights, timeout=3600)
    return insights

@shared_task
def generate_xp_insights(xp_system_id):
    xp_system = XPSystem.objects.filter(id=xp_system_id).first()
    if not xp_system:
        return "XP System not found."

    cache_key = f'xp_insights_{xp_system_id}'

    existing_insights = cache.get(cache_key)
    if existing_insights and xp_system.ai_insights == existing_insights:
        return "Insights already generated."

    ai_assistant = TaeAI()
    insights = ai_assistant.process_text(
        f"Generate XP recommendations:\nLevel: {xp_system.level}\nTotal XP: {xp_system.total_xp}"
    )

    xp_system.ai_insights = insights
    xp_system.save()
    cache.set(cache_key, insights, timeout=3600)
    return insights

@shared_task
def generate_leaderboard_insights():
    cache_key = 'leaderboard_insights'
    
    existing_insights = cache.get(cache_key)
    if existing_insights:
        return "Insights already cached."

    ai_assistant = TaeAI()
    insights = ai_assistant.process_text("Generate leaderboard insights and competition tips")

    cache.set(cache_key, insights, timeout=3600)
    return insights

# ---------------------- API Views with AI Processing ----------------------

class StudyStreakListCreateView(generics.ListCreateAPIView):
    queryset = StudyStreak.objects.all()
    serializer_class = StudyStreakSerializer

    def perform_create(self, serializer):
        streak = serializer.save()
        generate_streak_insights.delay(streak.id)

class StudyStreakDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudyStreak.objects.all()
    serializer_class = StudyStreakSerializer

    def perform_update(self, serializer):
        streak = serializer.save()
        generate_streak_insights.delay(streak.id)

class AchievementListCreateView(generics.ListCreateAPIView):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer

    def perform_create(self, serializer):
        achievement = serializer.save()
        generate_achievement_insights.delay(achievement.id)

class AchievementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer

    def perform_update(self, serializer):
        achievement = serializer.save()
        generate_achievement_insights.delay(achievement.id)

class XPSystemListCreateView(generics.ListCreateAPIView):
    queryset = XPSystem.objects.all()
    serializer_class = XPSystemSerializer

    def perform_create(self, serializer):
        xp_system = serializer.save()
        generate_xp_insights.delay(xp_system.id)

class XPSystemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = XPSystem.objects.all()
    serializer_class = XPSystemSerializer

    def perform_update(self, serializer):
        xp_system = serializer.save()
        generate_xp_insights.delay(xp_system.id)

class LeaderboardListView(generics.ListAPIView):
    queryset = Leaderboard.objects.all()
    serializer_class = LeaderboardSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        insights = cache.get('leaderboard_insights') or "Processing..."
        return Response({
            "leaderboard": response.data,
            "ai_insights": insights
        })

class LeaderboardDetailView(generics.RetrieveAPIView):
    queryset = Leaderboard.objects.all()
    serializer_class = LeaderboardSerializer

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        leaderboard = self.get_object()

        cache_key = f'leaderboard_insights_{leaderboard.id}'
        insights = cache.get(cache_key) or "Processing..."

        return Response({
            "leaderboard": response.data,
            "ai_insights": insights
        })

# ---------------------- Streak & XP Updating ----------------------

class UpdateStreakView(APIView):
    """Updates the user's study streak based on the last study date"""

    def post(self, request, user_id):
        streak, created = StudyStreak.objects.get_or_create(user_id=user_id)
        streak.update_streak()

        rate_limited_ai_request(generate_streak_insights, streak.id, f'streak_insights_{streak.id}')
        
        serializer = StudyStreakSerializer(streak)
        return Response(serializer.data)

class AddXPView(APIView):
    """Add XP to user's XP system"""

    def post(self, request, user_id):
        xp_system, created = XPSystem.objects.get_or_create(user_id=user_id)
        amount = request.data.get('amount', 0)

        try:
            xp_system.add_xp(amount)
            xp_system.user.leaderboard.update_xp()

            rate_limited_ai_request(generate_xp_insights, xp_system.id, f'xp_insights_{xp_system.id}')
            
            serializer = XPSystemSerializer(xp_system)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

# ---------------------- AI Rate-Limiting Helper ----------------------

import time

def rate_limited_ai_request(task_func, obj_id, cache_key, rate_limit=60):
    """ Prevents excessive AI requests by enforcing a time gap. """
    last_run = cache.get(f'last_run_{cache_key}')
    if last_run and time.time() - last_run < rate_limit:
        return f"Rate limit hit, skipping AI request for {cache_key}"
    
    cache.set(f'last_run_{cache_key}', time.time(), timeout=rate_limit)
    task_func.delay(obj_id)
