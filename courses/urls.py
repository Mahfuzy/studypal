from django.urls import path
from .views import (
    CourseListCreateView, CourseDetailView, GenerateFlashcardsView,
    LessonListCreateView, LessonDetailView,
    EnrollmentListCreateView, EnrollmentDetailView
)

urlpatterns = [
    path('courses/', CourseListCreateView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:course_id>/lessons/', LessonListCreateView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('enrollments/', EnrollmentListCreateView.as_view(), name='enrollment-list'),
    path('enrollments/<int:pk>/', EnrollmentDetailView.as_view(), name='enrollment-detail'),
    path('generate-flashcards/', GenerateFlashcardsView.as_view(), name='generate-flashcards'),
]
