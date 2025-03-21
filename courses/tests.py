from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Course, Lesson, Enrollment

User = get_user_model()

class CoursesViewsTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.user
        )
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            content='Test Content',
            course=self.course
        )
        self.enrollment = Enrollment.objects.create(
            student=self.user,
            course=self.course
        )

    def test_course_views(self):
        """Test Course endpoints"""
        # List
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create
        data = {
            'title': 'New Course',
            'description': 'New Description'
        }
        response = self.client.post(reverse('course-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Detail
        response = self.client.get(reverse('course-detail', args=[self.course.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Update
        data = {'title': 'Updated Course'}
        response = self.client.patch(reverse('course-detail', args=[self.course.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Delete
        response = self.client.delete(reverse('course-detail', args=[self.course.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_lesson_views(self):
        """Test Lesson endpoints"""
        # List
        response = self.client.get(reverse('lesson-list', args=[self.course.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create
        data = {
            'title': 'New Lesson',
            'content': 'New Content'
        }
        response = self.client.post(reverse('lesson-list', args=[self.course.id]), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Detail
        response = self.client.get(reverse('lesson-detail', args=[self.course.id, self.lesson.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Update
        data = {'title': 'Updated Lesson'}
        response = self.client.patch(reverse('lesson-detail', args=[self.course.id, self.lesson.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Delete
        response = self.client.delete(reverse('lesson-detail', args=[self.course.id, self.lesson.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_enrollment_views(self):
        """Test Enrollment endpoints"""
        # List
        response = self.client.get(reverse('enrollment-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create
        data = {'course': self.course.id}
        response = self.client.post(reverse('enrollment-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Detail
        response = self.client.get(reverse('enrollment-detail', args=[self.enrollment.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Update
        data = {'progress': 50}
        response = self.client.patch(reverse('enrollment-detail', args=[self.enrollment.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Delete
        response = self.client.delete(reverse('enrollment-detail', args=[self.enrollment.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_course_ai_status_view(self):
        """Test Course AI Status endpoint"""
        response = self.client.get(reverse('course-ai-status', args=[self.course.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('insights', response.data)

    def test_generate_flashcards_view(self):
        """Test Generate Flashcards endpoint"""
        data = {'text': 'Study material for flashcards'}
        response = self.client.post(reverse('generate-flashcards'), data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('task_id', response.data)
