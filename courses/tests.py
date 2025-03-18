from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Course, Lesson, Enrollment

User = get_user_model()

class CourseTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass', email='test@test.com')
        self.client.force_authenticate(user=self.user)
        
        self.course_data = {
            'title': 'Test Course',
            'description': 'Test Description',
            'instructor': self.user,
            'is_published': True
        }
        self.course = Course.objects.create(**self.course_data)

    def test_list_courses(self):
        url = reverse('course-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_course(self):
        url = reverse('course-list')
        data = {
            'title': 'New Course',
            'description': 'New Description',
            'is_published': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)

class LessonTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass', email='test@test.com')
        self.client.force_authenticate(user=self.user)
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.user
        )
        
        self.lesson_data = {
            'title': 'Test Lesson',
            'content': 'Test Content',
            'course': self.course,
            'order': 1,
            'duration': 30
        }
        self.lesson = Lesson.objects.create(**self.lesson_data)

    def test_list_lessons(self):
        url = reverse('lesson-list', kwargs={'course_id': self.course.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_lesson(self):
        url = reverse('lesson-list', kwargs={'course_id': self.course.id})
        data = {
            'title': 'New Lesson',
            'content': 'New Content',
            'order': 2,
            'duration': 45
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

class EnrollmentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass', email='test@test.com')
        self.client.force_authenticate(user=self.user)
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.user
        )

    def test_enroll_in_course(self):
        url = reverse('enrollment-list')
        data = {
            'course': self.course.id,
            'status': 'active'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Enrollment.objects.count(), 1)

    def test_list_enrollments(self):
        Enrollment.objects.create(
            student=self.user,
            course=self.course,
            status='active'
        )
        url = reverse('enrollment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_enrollment(self):
        enrollment = Enrollment.objects.create(
            student=self.user,
            course=self.course,
            status='active'
        )
        url = reverse('enrollment-detail', kwargs={'pk': enrollment.id})
        data = {'status': 'completed', 'progress': 100.0}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
