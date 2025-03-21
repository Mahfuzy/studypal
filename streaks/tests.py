from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import StudyStreak, Achievement, XPSystem, Badge, Leaderboard
from .serializers import StudyStreakSerializer, XPSystemSerializer

User = get_user_model()

class StreaksViewsTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.streak = StudyStreak.objects.create(user=self.user)
        self.achievement = Achievement.objects.create(
            user=self.user,
            title='Test Achievement',
            description='Test Description',
            achievement_type='STUDY'
        )
        self.xp_system = XPSystem.objects.create(user=self.user)
        self.badge = Badge.objects.create(
            user=self.user,
            title='Test Badge',
            description='Test Badge Description'
        )
        self.leaderboard = Leaderboard.objects.create(user=self.user)

    def test_study_streak_views(self):
        """Test Study Streak endpoints"""
        # List
        response = self.client.get(reverse('study-streak-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create
        data = {'user': self.user.id}
        response = self.client.post(reverse('study-streak-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Detail
        response = self.client.get(reverse('study-streak-detail', args=[self.streak.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Update
        data = {'current_streak': 5}
        response = self.client.patch(reverse('study-streak-detail', args=[self.streak.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Delete
        response = self.client.delete(reverse('study-streak-detail', args=[self.streak.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_achievement_views(self):
        """Test Achievement endpoints"""
        # List
        response = self.client.get(reverse('achievement-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create
        data = {
            'user': self.user.id,
            'title': 'New Achievement',
            'description': 'New Description',
            'achievement_type': 'STUDY'
        }
        response = self.client.post(reverse('achievement-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Detail
        response = self.client.get(reverse('achievement-detail', args=[self.achievement.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_xp_system_views(self):
        """Test XP System endpoints"""
        # List
        response = self.client.get(reverse('xp-system-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create
        data = {'user': self.user.id}
        response = self.client.post(reverse('xp-system-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Detail
        response = self.client.get(reverse('xp-system-detail', args=[self.xp_system.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_badge_views(self):
        """Test Badge endpoints"""
        # List
        response = self.client.get(reverse('badge-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create
        data = {
            'user': self.user.id,
            'title': 'New Badge',
            'description': 'New Badge Description'
        }
        response = self.client.post(reverse('badge-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Detail
        response = self.client.get(reverse('badge-detail', args=[self.badge.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_leaderboard_views(self):
        """Test Leaderboard endpoints"""
        # List
        response = self.client.get(reverse('leaderboard-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('leaderboard', response.data)
        self.assertIn('ai_insights', response.data)
        
        # Detail
        response = self.client.get(reverse('leaderboard-detail', args=[self.leaderboard.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('leaderboard', response.data)
        self.assertIn('ai_insights', response.data)

    def test_update_streak_view(self):
        """Test Update Streak endpoint"""
        response = self.client.post(reverse('update-streak', args=[self.user.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_xp_view(self):
        """Test Add XP endpoint"""
        data = {'amount': 100}
        response = self.client.post(reverse('add-xp', args=[self.user.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('xp_system', response.data)
        self.assertIn('new_badges', response.data)
