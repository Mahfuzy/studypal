from django.urls import path
from .views import (
    StudySessionListCreateView, StudySessionDetailView,
    ExamListCreateView, ExamDetailView,
    GenerateTimetableView
)

urlpatterns = [
    # Study Sessions
    path('study-sessions/', StudySessionListCreateView.as_view(), name='study-session-list'),
    path('study-sessions/<int:pk>/', StudySessionDetailView.as_view(), name='study-session-detail'),
    path('exams/', ExamListCreateView.as_view(), name='exam-list'),
    path('exams/<int:pk>/', ExamDetailView.as_view(), name='exam-detail'),
    path('generate-timetable/', GenerateTimetableView.as_view(), name='generate-timetable'),
]
