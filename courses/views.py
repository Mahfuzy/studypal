import time
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Course, Lesson, Enrollment
from .serializers import CourseSerializer, LessonSerializer, EnrollmentSerializer, GenerateFlashcardsSerializer
from study_assistant.ai_service import TaeAI

def generate_flashcards(study_text):
    """Convert study material into flashcards using AI."""
    ai_assistant = TaeAI()
    prompt = f"Convert this study material into flashcards with questions and answers:\n{study_text}"
    return ai_assistant.process_text(prompt)

def generate_course_insights(course_id):
    """Generate AI insights for a course."""
    course = Course.objects.filter(id=course_id).first()
    if not course:
        return "Course not found or deleted."

    cache_key = f'course_insights_{course_id}'
    existing_insights = cache.get(cache_key)

    if existing_insights and course.ai_insights == existing_insights:
        return existing_insights  

    ai_assistant = TaeAI()
    insights = ai_assistant.process_text(
        f"Analyze this course:\nTitle: {course.title}\nDescription: {course.description}"
    )

    course.ai_insights = insights
    course.save()
    cache.set(cache_key, insights, timeout=3600)  
    return insights

def generate_lesson_insights(lesson_id):
    """Generate AI insights for a lesson."""
    lesson = Lesson.objects.filter(id=lesson_id).first()
    if not lesson:
        return "Lesson not found or deleted."

    cache_key = f'lesson_insights_{lesson_id}'
    existing_insights = cache.get(cache_key)

    if existing_insights and lesson.ai_insights == existing_insights:
        return existing_insights  

    ai_assistant = TaeAI()
    insights = ai_assistant.process_text(
        f"Analyze this lesson:\nTitle: {lesson.title}\nContent: {lesson.content}"
    )

    lesson.ai_insights = insights
    lesson.save()
    cache.set(cache_key, insights, timeout=3600)  
    return insights

def generate_enrollment_study_plan(enrollment_id):
    """Generate a personalized study plan for an enrollment."""
    enrollment = Enrollment.objects.filter(id=enrollment_id).first()
    if not enrollment:
        return "Enrollment not found or deleted."

    cache_key = f'enrollment_study_plan_{enrollment_id}'
    existing_plan = cache.get(cache_key)

    if existing_plan and enrollment.study_plan == existing_plan:
        return existing_plan  

    ai_assistant = TaeAI()
    study_plan = ai_assistant.process_text(
        f"Create a personalized study plan for:\nCourse: {enrollment.course.title}\nStudent: {enrollment.student.username}"
    )

    enrollment.study_plan = study_plan
    enrollment.save()
    cache.set(cache_key, study_plan, timeout=3600)  
    return study_plan

def analyze_enrollment_progress(enrollment_id):
    """Analyze student progress based on their course enrollment."""
    enrollment = Enrollment.objects.filter(id=enrollment_id).first()
    if not enrollment:
        return "Enrollment not found or deleted."

    cache_key = f'enrollment_progress_{enrollment_id}'
    existing_analysis = cache.get(cache_key)

    if existing_analysis and enrollment.progress_analysis == existing_analysis:
        return existing_analysis  

    ai_assistant = TaeAI()
    analysis = ai_assistant.process_text(
        f"Analyze progress:\nCourse: {enrollment.course.title}\nProgress: {enrollment.progress}%"
    )

    enrollment.progress_analysis = analysis
    enrollment.save()
    cache.set(cache_key, analysis, timeout=3600)  
    return analysis

# ------------------------- AI Rate-Limiting Helper -------------------------

def rate_limited_ai_request(task_func, obj_id, cache_key, rate_limit=60):
    """
    Prevent excessive AI requests by enforcing a cooldown period.
    Returns cached results if available.
    """
    last_run = cache.get(f'last_run_{cache_key}')
    cached_result = cache.get(cache_key)

    if last_run and time.time() - last_run < rate_limit:
        return cached_result if cached_result else "Rate limit hit, skipping AI request."

    cache.set(f'last_run_{cache_key}', time.time(), timeout=rate_limit)
    return task_func(obj_id)

# ------------------------- API Views -------------------------

class CourseAIStatusView(generics.RetrieveAPIView):
    """Check if AI insights are available for a course."""
    
    def retrieve(self, request, course_id):
        insights = cache.get(f'course_insights_{course_id}')
        return Response({
            "status": "ready" if insights else "processing",
            "insights": insights or "Processing...",
        })

class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        course = serializer.save(instructor=self.request.user)
        rate_limited_ai_request(generate_course_insights, course.id, f'course_insights_{course.id}')

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        course = serializer.save()
        rate_limited_ai_request(generate_course_insights, course.id, f'course_insights_{course.id}')

class LessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Lesson.objects.none()
        return Lesson.objects.filter(course_id=self.kwargs['course_id'])

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs['course_id'])
        lesson = serializer.save(course=course)
        try:
            rate_limited_ai_request(generate_lesson_insights, lesson.id, f'lesson_insights_{lesson.id}')
        except Exception as e:
            print(f"AI request failed for Lesson {lesson.id}: {e}")

class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Lesson.objects.none()
        return Lesson.objects.filter(course_id=self.kwargs['course_id'])

    def perform_update(self, serializer):
        lesson = serializer.save()
        try:
            rate_limited_ai_request(generate_lesson_insights, lesson.id, f'lesson_insights_{lesson.id}')
        except Exception as e:
            print(f"AI request failed for Lesson {lesson.id}: {e}")

class EnrollmentListCreateView(generics.ListCreateAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Enrollment.objects.none()
        return Enrollment.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        enrollment = serializer.save(student=self.request.user)
        rate_limited_ai_request(generate_enrollment_study_plan, enrollment.id, f'enrollment_study_plan_{enrollment.id}')

class EnrollmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Enrollment.objects.none()
        return Enrollment.objects.filter(student=self.request.user)

    def perform_update(self, serializer):
        enrollment = serializer.save()
        previous_progress = cache.get(f'enrollment_progress_{enrollment.id}', 0)
        if enrollment.progress - previous_progress >= 20:
            rate_limited_ai_request(generate_enrollment_study_plan, enrollment.id, f'enrollment_study_plan_{enrollment.id}')
        rate_limited_ai_request(analyze_enrollment_progress, enrollment.id, f'enrollment_progress_{enrollment.id}')

class GenerateFlashcardsView(generics.CreateAPIView):
    """AI-powered flashcard generator"""
    serializer_class = GenerateFlashcardsSerializer
    
    def create(self, request, *args, **kwargs):
        study_text = request.data.get("text")
        if not study_text:
            return Response({"error": "Study text is required"}, status=400)

        flashcards = generate_flashcards(study_text)
        return Response({"flashcards": flashcards}, status=status.HTTP_200_OK)
