from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from .models import StudyStreak, Achievement, XPSystem, Leaderboard
from .serializers import StudyStreakSerializer, XPSystemSerializer

User = get_user_model()

class StudyStreakViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.streak = StudyStreak.objects.create(user=self.user)
        self.list_url = reverse('study-streak-list')
        self.detail_url = reverse('study-streak-detail', args=[self.streak.id])
        self.update_url = reverse('update-streak', args=[self.user.id])

    def test_list_streaks(self):
        response = self.client.get(self.list_url)
        streaks = StudyStreak.objects.all()
        serializer = StudyStreakSerializer(streaks, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_streak(self):
        response = self.client.get(self.detail_url)
        serializer = StudyStreakSerializer(self.streak)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_streak(self):
        response = self.client.post(self.update_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.streak.refresh_from_db()
        serializer = StudyStreakSerializer(self.streak)
        self.assertEqual(response.data, serializer.data)

class XPSystemViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.xp_system = XPSystem.objects.create(user=self.user)
        self.leaderboard = Leaderboard.objects.create(user=self.user)
        self.list_url = reverse('xp-list')
        self.detail_url = reverse('xp-detail', args=[self.xp_system.id])
        self.add_xp_url = reverse('add-xp', args=[self.user.id])

    def test_list_xp(self):
        response = self.client.get(self.list_url)
        xp_systems = XPSystem.objects.all()
        serializer = XPSystemSerializer(xp_systems, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_xp(self):
        response = self.client.get(self.detail_url)
        serializer = XPSystemSerializer(self.xp_system)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_add_xp(self):
        data = {'amount': 100}
        response = self.client.post(self.add_xp_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.xp_system.refresh_from_db()
        self.assertEqual(self.xp_system.total_xp, 100)

    def test_add_invalid_xp(self):
        data = {'amount': -50}
        response = self.client.post(self.add_xp_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.xp_system.refresh_from_db()
        self.assertEqual(self.xp_system.total_xp, 0)

class LeaderboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.leaderboard = Leaderboard.objects.create(user=self.user)
        self.list_url = reverse('leaderboard-list')
        self.detail_url = reverse('leaderboard-detail', args=[self.leaderboard.id])

    def test_list_leaderboard(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_leaderboard_entry(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
