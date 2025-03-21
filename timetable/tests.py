from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from .models import StudySession, Exam
from .serializers import StudySessionSerializer, ExamSerializer
from unittest.mock import patch
import json

User = get_user_model()

class TimetableViewsTest(APITestCase):
    """Test suite for timetable views."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        # Create test study session
        self.study_session = StudySession.objects.create(
            user=self.user,
            subject='Mathematics',
            duration=60,
            progress=0,
            ai_insights='Test insights'
        )

        # Create test exam
        self.exam = Exam.objects.create(
            user=self.user,
            subject='Physics',
            date=timezone.now().date(),
            ai_insights='Test exam insights'
        )

    def test_study_session_list_create(self):
        """Test study session listing and creation."""
        # Test listing study sessions
        url = '/api/timetable/sessions/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Test creating study session
        data = {
            'subject': 'Chemistry',
            'duration': 45,
            'progress': 0
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StudySession.objects.count(), 2)
        self.assertEqual(response.data['subject'], 'Chemistry')

    def test_study_session_detail(self):
        """Test study session retrieval, update, and deletion."""
        url = f'/api/timetable/sessions/{self.study_session.id}/'

        # Test retrieval
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subject'], 'Mathematics')

        # Test update
        data = {
            'subject': 'Mathematics',
            'duration': 90,
            'progress': 50
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['duration'], 90)
        self.assertEqual(response.data['progress'], 50)

        # Test deletion
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(StudySession.objects.count(), 0)

    def test_exam_list_create(self):
        """Test exam listing and creation."""
        # Test listing exams
        url = '/api/timetable/exams/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Test creating exam
        data = {
            'subject': 'Chemistry',
            'date': timezone.now().date(),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Exam.objects.count(), 2)
        self.assertEqual(response.data['subject'], 'Chemistry')

    def test_exam_detail(self):
        """Test exam retrieval, update, and deletion."""
        url = f'/api/timetable/exams/{self.exam.id}/'

        # Test retrieval
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subject'], 'Physics')

        # Test update
        data = {
            'subject': 'Physics',
            'date': timezone.now().date(),
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subject'], 'Physics')

        # Test deletion
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Exam.objects.count(), 0)

    @patch('timetable.views.generate_ai_insights.delay')
    def test_generate_timetable(self, mock_generate_insights):
        """Test timetable generation."""
        url = '/api/timetable/generate/'
        mock_generate_insights.return_value.id = 'test_task_id'

        data = {
            'available_hours': 4,
            'study_goals': 'Complete calculus review',
            'priority_subjects': ['Mathematics', 'Physics']
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue('task_id' in response.data)
        mock_generate_insights.assert_called_once()

    @patch('timetable.views.AsyncResult')
    def test_task_status(self, mock_async_result):
        """Test task status checking."""
        task_id = 'test_task_id'
        url = f'/api/timetable/task-status/{task_id}/'

        # Test pending task
        mock_async_result.return_value.state = 'PENDING'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], 'Processing')

        # Test completed task
        mock_async_result.return_value.state = 'SUCCESS'
        mock_async_result.return_value.result = 'Task completed successfully'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Completed')
        self.assertEqual(response.data['response'], 'Task completed successfully')

        # Test failed task
        mock_async_result.return_value.state = 'FAILURE'
        mock_async_result.return_value.result = 'Task failed'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['status'], 'Failed')
        self.assertEqual(response.data['error'], 'Task failed')
