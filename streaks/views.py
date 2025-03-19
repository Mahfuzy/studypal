from datetime import date
import time
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
    """Generate AI-based insights for a study streak."""
    streak = StudyStreak.objects.filter(id=streak_id).first()
    if not streak:
        return "Streak not found."

    cache_key = f'streak_insights_{streak_id}'
    insights = cache.get(cache_key)
    
    if insights and streak.ai_insights == insights:
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
    """Generate AI-based insights for an achievement."""
    achievement = Achievement.objects.filter(id=achievement_id).first()
    if not achievement:
        return "Achievement not found."

    cache_key = f'achievement_insights_{achievement_id}'
    insights = cache.get(cache_key)

    if insights and achievement.ai_insights == insights:
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
    """Generate AI-based XP recommendations."""
    xp_system = XPSystem.objects.filter(id=xp_system_id).first()
    if not xp_system:
        return "XP System not found."

    cache_key = f'xp_insights_{xp_system_id}'
    insights = cache.get(cache_key)

    if insights and xp_system.ai_insights == insights:
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
    """Generate AI-based leaderboard insights."""
    cache_key = 'leaderboard_insights'
    insights = cache.get(cache_key)

    if insights:
        return "Insights already cached."

    ai_assistant = TaeAI()
    insights = ai_assistant.process_text("Generate leaderboard insights and competition tips")

    cache.set(cache_key, insights, timeout=3600)
    return insights

# ---------------------- API Views ----------------------

## 📌 Study Streak Views
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

## 📌 Achievement Views
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

## 📌 XP System Views
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

## 📌 Leaderboard Views
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

# ---------------------- Badge System ----------------------

## 📌 Badge Views
class BadgeListCreateView(generics.ListCreateAPIView):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer

class BadgeDetailView(generics.RetrieveAPIView):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer

# ---------------------- XP & Streak Updates ----------------------

class UpdateStreakView(APIView):
    """Updates the user's study streak and triggers AI insights."""

    def post(self, request, user_id):
        streak, created = StudyStreak.objects.get_or_create(user_id=user_id)
        streak.update_streak()

        rate_limited_ai_request(generate_streak_insights, streak.id, f'streak_insights_{streak.id}')
        
        return Response(StudyStreakSerializer(streak).data)

class AddXPView(APIView):
    """Adds XP to user's XP system and unlocks badges if applicable."""

    def post(self, request, user_id):
        xp_system, created = XPSystem.objects.get_or_create(user_id=user_id)
        amount = request.data.get('amount', 0)

        try:
            xp_system.add_xp(amount)
            xp_system.user.leaderboard.update_xp()

            # 🔹 Unlock new badges
            unlocked_badges = Badge.objects.filter(xp_required__lte=xp_system.total_xp)
            xp_system.user.badges.add(*unlocked_badges)

            rate_limited_ai_request(generate_xp_insights, xp_system.id, f'xp_insights_{xp_system.id}')
            
            return Response({
                "xp_system": XPSystemSerializer(xp_system).data,
                "new_badges": BadgeSerializer(unlocked_badges, many=True).data
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ---------------------- AI Rate-Limiting Helper ----------------------

def rate_limited_ai_request(task_func, obj_id, cache_key, rate_limit=60):
    """Prevents excessive AI requests by enforcing a time gap."""
    last_run = cache.get(f'last_run_{cache_key}')
    if last_run and time.time() - last_run < rate_limit:
        return f"Rate limit hit, skipping AI request for {cache_key}"
    
    cache.set(f'last_run_{cache_key}', time.time(), timeout=rate_limit)
    task_func.delay(obj_id)
