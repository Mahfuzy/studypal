from django.urls import path
from .views import (
    QuizListCreateView, QuizDetailView,
    QuestionListCreateView, QuestionDetailView, 
    AnswerListCreateView, AnswerDetailView,
    QuizAttemptListCreateView, QuizAttemptDetailView
)

urlpatterns = [
    path('quizzes/', QuizListCreateView.as_view(), name='quiz-list'),
    path('quizzes/<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/<int:quiz_id>/questions/', QuestionListCreateView.as_view(), name='question-list'),
    path('questions/<int:pk>/', QuestionDetailView.as_view(), name='question-detail'),
    path('questions/<int:question_id>/answers/', AnswerListCreateView.as_view(), name='answer-list'), 
    path('answers/<int:pk>/', AnswerDetailView.as_view(), name='answer-detail'),
    path('attempts/', QuizAttemptListCreateView.as_view(), name='quiz-attempt-list'),
    path('attempts/<int:pk>/', QuizAttemptDetailView.as_view(), name='quiz-attempt-detail'),
]
