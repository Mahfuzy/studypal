from rest_framework import serializers
from .models import StudyStreak, Achievement, XPSystem, Badge, Leaderboard

class StudyStreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyStreak
        fields = ['id', 'user', 'current_streak', 'longest_streak', 'last_study_date', 
                 'total_study_days', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'user', 'title', 'description', 'achievement_type', 
                 'icon', 'awarded_on', 'points', 'is_public']
        read_only_fields = ['awarded_on']

class XPSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = XPSystem
        fields = ['id', 'user', 'total_xp', 'level']
        read_only_fields = ['level']

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['id', 'user', 'title', 'description', 'icon', 'awarded_on']
        read_only_fields = ['awarded_on']

class LeaderboardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Leaderboard
        fields = ['id', 'user', 'username', 'total_xp']
        read_only_fields = ['total_xp']
