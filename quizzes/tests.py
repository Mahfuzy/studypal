from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from courses.models import Course
from .models import Quiz, Question, Answer, QuizAttempt

User = get_user_model()

class QuizzesViewsTest(APITestCase):
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
        self.quiz = Quiz.objects.create(
            course=self.course,
            title='Test Quiz',
            description='Test Description'
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            text='Test Question',
            question_type='MULTIPLE_CHOICE',
            points=10
        )
        self.answer = Answer.objects.create(
            question=self.question,
            text='Test Answer',
            is_correct=True
        )
        self.quiz_attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user
        )

    def test_quiz_views(self):
        """Test Quiz endpoints"""
        # List
        response = self.client.get(reverse('quiz-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create
        data = {
            'course': self.course.id,
            'title': 'New Quiz',
            'description': 'New Description'
        }
        response = self.client.post(reverse('quiz-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Detail
        response = self.client.get(reverse('quiz-detail', args=[self.quiz.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Update
        data = {'title': 'Updated Quiz'}
        response = self.client.patch(reverse('quiz-detail', args=[self.quiz.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Delete
        response = self.client.delete(reverse('quiz-detail', args=[self.quiz.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_question_views(self):
        """Test Question endpoints"""
        # List
        response = self.client.get(reverse('question-list', args=[self.quiz.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create
        data = {
            'text': 'New Question',
            'question_type': 'MULTIPLE_CHOICE',
            'points': 10
        }
        response = self.client.post(reverse('question-list', args=[self.quiz.id]), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Detail
        response = self.client.get(reverse('question-detail', args=[self.question.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Update
        data = {'text': 'Updated Question'}
        response = self.client.patch(reverse('question-detail', args=[self.question.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Delete
        response = self.client.delete(reverse('question-detail', args=[self.question.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_answer_views(self):
        """Test Answer endpoints"""
        # List
        response = self.client.get(reverse('answer-list', args=[self.question.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create
        data = {
            'text': 'New Answer',
            'is_correct': True
        }
        response = self.client.post(reverse('answer-list', args=[self.question.id]), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Detail
        response = self.client.get(reverse('answer-detail', args=[self.answer.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Update
        data = {'text': 'Updated Answer'}
        response = self.client.patch(reverse('answer-detail', args=[self.answer.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Delete
        response = self.client.delete(reverse('answer-detail', args=[self.answer.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_quiz_attempt_views(self):
        """Test Quiz Attempt endpoints"""
        # List
        response = self.client.get(reverse('quiz-attempt-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create
        data = {'quiz': self.quiz.id}
        response = self.client.post(reverse('quiz-attempt-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Detail
        response = self.client.get(reverse('quiz-attempt-detail', args=[self.quiz_attempt.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Update
        data = {'status': 'COMPLETED', 'score': 100}
        response = self.client.patch(reverse('quiz-attempt-detail', args=[self.quiz_attempt.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
