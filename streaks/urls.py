from django.urls import path
from .views import (
    StudyStreakListCreateView, StudyStreakDetailView, UpdateStreakView,
    AchievementListCreateView, AchievementDetailView,
    XPSystemListCreateView, XPSystemDetailView, AddXPView,
    LeaderboardListView, LeaderboardDetailView,
    BadgeListCreateView, BadgeDetailView
)

urlpatterns = [
    path('study-streaks/', StudyStreakListCreateView.as_view(), name='study-streak-list'),
    path('study-streaks/<int:pk>/', StudyStreakDetailView.as_view(), name='study-streak-detail'),
    path('study-streaks/update/<int:user_id>/', UpdateStreakView.as_view(), name='update-streak'),
    path('achievements/', AchievementListCreateView.as_view(), name='achievement-list'),
    path('achievements/<int:pk>/', AchievementDetailView.as_view(), name='achievement-detail'),
    path('xp-system/', XPSystemListCreateView.as_view(), name='xp-system-list'),
    path('xp-system/<int:pk>/', XPSystemDetailView.as_view(), name='xp-system-detail'),
    path('xp-system/add-xp/<int:user_id>/', AddXPView.as_view(), name='add-xp'),
    path('leaderboard/', LeaderboardListView.as_view(), name='leaderboard-list'),
    path('leaderboard/<int:pk>/', LeaderboardDetailView.as_view(), name='leaderboard-detail'),
    path('badges/', BadgeListCreateView.as_view(), name='badge-list'),
    path('badges/<int:pk>/', BadgeDetailView.as_view(), name='badge-detail'),
]
