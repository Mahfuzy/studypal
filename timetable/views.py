import os
import hashlib
from django.utils import timezone
from django.core.cache import cache
from celery.result import AsyncResult
from celery import shared_task
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import StudySession, Exam
from .serializers import StudySessionSerializer, ExamSerializer
from study_assistant.ai_service import TaeAI

# Initialize AI assistant
ai_assistant = TaeAI()

# ✅ Celery Task for AI Processing
@shared_task
def generate_ai_insights(prompt):
    """Processes AI request via Gemini and returns insights"""
    return ai_assistant.process_text(prompt)

# ✅ Study Session List/Create View (with AI-powered insights)
class StudySessionListCreateView(generics.ListCreateAPIView):
    serializer_class = StudySessionSerializer

    def get_queryset(self):
        return StudySession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        session = serializer.save(user=self.request.user)

        # Generate cache key
        query_hash = hashlib.md5(f"session:{session.subject}:{session.duration}".encode()).hexdigest()
        cached_insights = cache.get(query_hash)

        if cached_insights:
            session.ai_insights = cached_insights
            session.save()
        else:
            # Use Celery for async AI processing
            task = generate_ai_insights.delay(
                f"Generate study session tips:\nSubject: {session.subject}\nDuration: {session.duration} minutes"
            )
            session.ai_task_id = task.id  # Store task ID for tracking
            session.save()

# ✅ Study Session Detail (Update AI insights)
class StudySessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudySessionSerializer

    def get_queryset(self):
        return StudySession.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        session = serializer.save()

        query_hash = hashlib.md5(f"update_session:{session.subject}:{session.progress}".encode()).hexdigest()
        cached_insights = cache.get(query_hash)

        if cached_insights:
            session.ai_insights = cached_insights
        else:
            task = generate_ai_insights.delay(
                f"Update study recommendations:\nSubject: {session.subject}\nProgress: {session.progress}%"
            )
            session.ai_task_id = task.id
        session.save()

# ✅ Exam List/Create View (with AI-powered insights)
class ExamListCreateView(generics.ListCreateAPIView):
    serializer_class = ExamSerializer

    def get_queryset(self):
        return Exam.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        exam = serializer.save(user=self.request.user)

        query_hash = hashlib.md5(f"exam:{exam.subject}:{exam.date}".encode()).hexdigest()
        cached_insights = cache.get(query_hash)

        if cached_insights:
            exam.ai_insights = cached_insights
            exam.save()
        else:
            task = generate_ai_insights.delay(
                f"Generate exam preparation plan:\nSubject: {exam.subject}\nDate: {exam.date}"
            )
            exam.ai_task_id = task.id
            exam.save()

# ✅ Exam Detail (Update AI insights)
class ExamDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExamSerializer

    def get_queryset(self):
        return Exam.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        exam = serializer.save()
        days_until_exam = (exam.date - timezone.now().date()).days

        query_hash = hashlib.md5(f"update_exam:{exam.subject}:{days_until_exam}".encode()).hexdigest()
        cached_insights = cache.get(query_hash)

        if cached_insights:
            exam.ai_insights = cached_insights
        else:
            task = generate_ai_insights.delay(
                f"Update exam strategy:\nDays until exam: {days_until_exam}"
            )
            exam.ai_task_id = task.id
        exam.save()

# ✅ Generate Study Timetable (Async AI processing)
class GenerateTimetableView(APIView):
    """Generates an AI-powered study timetable based on user inputs, study sessions, and exams"""

    def post(self, request):
        user = request.user
        available_hours = request.data.get("available_hours", 4)
        custom_study_goals = request.data.get("study_goals", None)
        priority_subjects = request.data.get("priority_subjects", [])

        study_sessions = StudySession.objects.filter(user=user)
        exams = Exam.objects.filter(user=user)

        # Generate cache key
        query_hash = hashlib.md5(f"timetable:{available_hours}:{custom_study_goals}".encode()).hexdigest()
        cached_timetable = cache.get(query_hash)

        if cached_timetable:
            return Response({"timetable": cached_timetable})

        # Prepare AI input prompt
        timetable_input = (
            f"Generate an optimal study timetable:\n"
            f"Study Sessions: {[s.subject for s in study_sessions]}\n"
            f"Upcoming Exams: {[f'{e.subject} on {e.date}' for e in exams]}\n"
            f"Available Study Hours Per Day: {available_hours}\n"
        )

        if not exams and custom_study_goals:
            timetable_input += f"Custom Study Goal: {custom_study_goals}\n"
        if priority_subjects:
            timetable_input += f"Priority Subjects: {priority_subjects}\n"

        task = generate_ai_insights.delay(timetable_input)

        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)

# ✅ Check AI Task Status
class TaskStatusView(APIView):
    """Check the status of an AI Celery task"""

    def get(self, request, task_id):
        task = AsyncResult(task_id)

        if task.state == "PENDING":
            return Response({"status": "Processing"}, status=status.HTTP_202_ACCEPTED)
        elif task.state == "SUCCESS":
            cache.set(task_id, task.result, timeout=86400)  # ✅ Cache AI result
            return Response({"status": "Completed", "response": task.result})
        elif task.state == "FAILURE":
            return Response({"status": "Failed", "error": str(task.result)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"status": task.state}, status=status.HTTP_202_ACCEPTED)
