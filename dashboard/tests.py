from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from .models import DashboardStats
from .serializers import DashboardStatsSerializer
from unittest.mock import patch
import json

User = get_user_model()

class DashboardViewsTest(APITestCase):
    """Test suite for dashboard views."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        # Create test dashboard stats
        self.stats = DashboardStats.objects.create(
            user=self.user,
            total_learning_time=120,
            completed_courses=2,
            unfinished_courses=3,
            current_streak=5,
            longest_streak=7,
            next_exam_date=timezone.now().date(),
            ai_insights='Test insights',
            ai_recommendations='Test recommendations'
        )

    @patch('dashboard.views.generate_dashboard_insights.delay')
    def test_get_dashboard_stats(self, mock_generate_insights):
        """Test retrieving dashboard stats."""
        url = f'/api/dashboard/stats/{self.user.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_learning_time'], 120)
        self.assertEqual(response.data['completed_courses'], 2)
        self.assertEqual(response.data['unfinished_courses'], 3)
        self.assertEqual(response.data['current_streak'], 5)
        self.assertEqual(response.data['longest_streak'], 7)
        self.assertEqual(response.data['ai_insights'], 'Test insights')
        mock_generate_insights.assert_called_once_with(self.user.id)

    @patch('dashboard.views.generate_dashboard_recommendations.delay')
    def test_update_dashboard_stats(self, mock_generate_recommendations):
        """Test updating dashboard stats."""
        url = f'/api/dashboard/stats/{self.user.id}/'
        data = {
            'learning_time': 30,
            'completed_courses': 1,
            'unfinished_courses': 1,
            'current_streak': 6,
            'next_exam_date': str(timezone.now().date())
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Dashboard updated successfully!')
        self.assertEqual(response.data['recommendations'], 'Processing AI recommendations...')

        # Verify stats were updated
        updated_stats = response.data['updated_stats']
        self.assertEqual(updated_stats['total_learning_time'], 150)  # 120 + 30
        self.assertEqual(updated_stats['completed_courses'], 3)  # 2 + 1
        self.assertEqual(updated_stats['unfinished_courses'], 4)  # 3 + 1
        self.assertEqual(updated_stats['current_streak'], 6)
        self.assertEqual(updated_stats['longest_streak'], 7)  # max(7, 6)

        # Verify AI recommendations task was called
        mock_generate_recommendations.assert_called_once_with(
            self.user.id,
            30,
            3,
            4,
            6
        )

    def test_get_nonexistent_user_stats(self):
        """Test retrieving stats for nonexistent user."""
        url = '/api/dashboard/stats/999/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_access(self):
        """Test unauthorized access to dashboard stats."""
        self.client.force_authenticate(user=None)
        url = f'/api/dashboard/stats/{self.user.id}/'

        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test POST request
        data = {
            'learning_time': 30,
            'completed_courses': 1
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_stats_with_invalid_data(self):
        """Test updating stats with invalid data."""
        url = f'/api/dashboard/stats/{self.user.id}/'
        data = {
            'learning_time': 'invalid',  # Should be integer
            'completed_courses': -1,  # Should be non-negative
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_longest_streak_update(self):
        """Test longest streak is updated correctly."""
        url = f'/api/dashboard/stats/{self.user.id}/'

        # Update with lower streak
        data = {'current_streak': 3}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['updated_stats']['longest_streak'], 7)  # Unchanged

        # Update with higher streak
        data = {'current_streak': 10}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['updated_stats']['longest_streak'], 10)  # Updated
