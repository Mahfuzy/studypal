from django.urls import path
from .views import (
    StudyStreakListCreateView, StudyStreakDetailView, UpdateStreakView,
    AchievementListCreateView, AchievementDetailView,
    XPSystemListCreateView, XPSystemDetailView, AddXPView,
    BadgeListCreateView, BadgeDetailView,
    LeaderboardListView, LeaderboardDetailView
)

urlpatterns = [
    path('study-streaks/', StudyStreakListCreateView.as_view(), name='study-streak-list'),
    path('study-streaks/<int:pk>/', StudyStreakDetailView.as_view(), name='study-streak-detail'),
    path('study-streaks/update/<int:user_id>/', UpdateStreakView.as_view(), name='update-streak'),
    path('achievements/', AchievementListCreateView.as_view(), name='achievement-list'),
    path('achievements/<int:pk>/', AchievementDetailView.as_view(), name='achievement-detail'),
    path('xp/', XPSystemListCreateView.as_view(), name='xp-list'),
    path('xp/<int:pk>/', XPSystemDetailView.as_view(), name='xp-detail'),
    path('xp/add/<int:user_id>/', AddXPView.as_view(), name='add-xp'),
    path('badges/', BadgeListCreateView.as_view(), name='badge-list'),
    path('badges/<int:pk>/', BadgeDetailView.as_view(), name='badge-detail'),
    path('leaderboard/', LeaderboardListView.as_view(), name='leaderboard-list'),
    path('leaderboard/<int:pk>/', LeaderboardDetailView.as_view(), name='leaderboard-detail'),
]
