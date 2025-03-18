from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from courses.models import Course
from .models import Quiz, Question, Answer, QuizAttempt

class QuizViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description'
        )
        self.quiz = Quiz.objects.create(
            course=self.course,
            title='Test Quiz',
            description='Test Quiz Description',
            time_limit=30,
            pass_percentage=70
        )
        self.client.force_authenticate(user=self.user)

    def test_list_quizzes(self):
        url = reverse('quiz-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_quiz(self):
        url = reverse('quiz-list')
        data = {
            'course': self.course.id,
            'title': 'New Quiz',
            'description': 'New Quiz Description',
            'time_limit': 20,
            'pass_percentage': 60
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.count(), 2)

    def test_retrieve_quiz(self):
        url = reverse('quiz-detail', args=[self.quiz.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Quiz')

    def test_update_quiz(self):
        url = reverse('quiz-detail', args=[self.quiz.id])
        data = {
            'course': self.course.id,
            'title': 'Updated Quiz',
            'description': 'Updated Description',
            'time_limit': 25,
            'pass_percentage': 75
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.title, 'Updated Quiz')

    def test_delete_quiz(self):
        url = reverse('quiz-detail', args=[self.quiz.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Quiz.objects.count(), 0)

class QuestionViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description'
        )
        self.quiz = Quiz.objects.create(
            course=self.course,
            title='Test Quiz'
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            text='Test Question',
            question_type='multiple_choice'
        )
        self.client.force_authenticate(user=self.user)

    def test_list_questions(self):
        url = reverse('question-list', args=[self.quiz.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_question(self):
        url = reverse('question-list', args=[self.quiz.id])
        data = {
            'text': 'New Question',
            'question_type': 'true_false',
            'points': 2
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 2)

class AnswerViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description'
        )
        self.quiz = Quiz.objects.create(
            course=self.course,
            title='Test Quiz'
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            text='Test Question'
        )
        self.answer = Answer.objects.create(
            question=self.question,
            text='Test Answer',
            is_correct=True
        )
        self.client.force_authenticate(user=self.user)

    def test_list_answers(self):
        url = reverse('answer-list', args=[self.question.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_answer(self):
        url = reverse('answer-list', args=[self.question.id])
        data = {
            'text': 'New Answer',
            'is_correct': False,
            'explanation': 'This is incorrect'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Answer.objects.count(), 2)

class QuizAttemptViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description'
        )
        self.quiz = Quiz.objects.create(
            course=self.course,
            title='Test Quiz'
        )
        self.client.force_authenticate(user=self.user)

    def test_list_attempts(self):
        QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            status='completed',
            score=80
        )
        url = reverse('quiz-attempt-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_attempt(self):
        url = reverse('quiz-attempt-list')
        data = {
            'quiz': self.quiz.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(QuizAttempt.objects.count(), 1)
