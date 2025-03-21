import os
import hashlib
from django.utils import timezone
from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import StudySession, Exam
from .serializers import StudySessionSerializer, ExamSerializer
from study_assistant.ai_service import TaeAI
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Initialize AI assistant
ai_assistant = TaeAI()

# ✅ Study Session List/Create View (with AI-powered insights)
class StudySessionListCreateView(generics.ListCreateAPIView):
    """List and create study sessions with AI-powered insights."""
    serializer_class = StudySessionSerializer
    permission_classes = [IsAuthenticated]

    # @swagger_auto_schema(
    #     operation_description="List all study sessions for the current user",
    #     responses={
    #         200: openapi.Response(
    #             description="List of study sessions",
    #             schema=StudySessionSerializer(many=True)
    #         ),
    #         401: "Unauthorized"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Create a new study session with AI insights",
    #     request_body=StudySessionSerializer,
    #     responses={
    #         201: openapi.Response(
    #             description="Study session created successfully",
    #             schema=StudySessionSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized"
    #     }
    # )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return StudySession.objects.none()
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
            # Generate AI insights synchronously
            insights = ai_assistant.process_text(
                f"Generate study session tips:\nSubject: {session.subject}\nDuration: {session.duration} minutes"
            )
            session.ai_insights = insights
            session.save()

# ✅ Study Session Detail (Update AI insights)
class StudySessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a study session with AI insights."""
    serializer_class = StudySessionSerializer
    permission_classes = [IsAuthenticated]

    # @swagger_auto_schema(
    #     operation_description="Retrieve a study session",
    #     responses={
    #         200: openapi.Response(
    #             description="Study session details",
    #             schema=StudySessionSerializer
    #         ),
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Update a study session with new AI insights",
    #     request_body=StudySessionSerializer,
    #     responses={
    #         200: openapi.Response(
    #             description="Study session updated successfully",
    #             schema=StudySessionSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Delete a study session",
    #     responses={
    #         204: "No Content",
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return StudySession.objects.none()
        return StudySession.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        session = serializer.save()

        query_hash = hashlib.md5(f"update_session:{session.subject}:{session.progress}".encode()).hexdigest()
        cached_insights = cache.get(query_hash)

        if cached_insights:
            session.ai_insights = cached_insights
        else:
            insights = ai_assistant.process_text(
                f"Update study recommendations:\nSubject: {session.subject}\nProgress: {session.progress}%"
            )
            session.ai_insights = insights
        session.save()

# ✅ Exam List/Create View (with AI-powered insights)
class ExamListCreateView(generics.ListCreateAPIView):
    """List and create exams with AI-powered insights."""
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    # @swagger_auto_schema(
    #     operation_description="List all exams for the current user",
    #     responses={
    #         200: openapi.Response(
    #             description="List of exams",
    #             schema=ExamSerializer(many=True)
    #         ),
    #         401: "Unauthorized"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Create a new exam with AI insights",
    #     request_body=ExamSerializer,
    #     responses={
    #         201: openapi.Response(
    #             description="Exam created successfully",
    #             schema=ExamSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized"
    #     }
    # )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Exam.objects.none()
        return Exam.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        exam = serializer.save(user=self.request.user)

        query_hash = hashlib.md5(f"exam:{exam.subject}:{exam.date}".encode()).hexdigest()
        cached_insights = cache.get(query_hash)

        if cached_insights:
            exam.ai_insights = cached_insights
            exam.save()
        else:
            insights = ai_assistant.process_text(
                f"Generate exam preparation plan:\nSubject: {exam.subject}\nDate: {exam.date}"
            )
            exam.ai_insights = insights
            exam.save()

# ✅ Exam Detail (Update AI insights)
class ExamDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an exam with AI insights."""
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    # @swagger_auto_schema(
    #     operation_description="Retrieve an exam",
    #     responses={
    #         200: openapi.Response(
    #             description="Exam details",
    #             schema=ExamSerializer
    #         ),
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Update an exam with new AI insights",
    #     request_body=ExamSerializer,
    #     responses={
    #         200: openapi.Response(
    #             description="Exam updated successfully",
    #             schema=ExamSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Delete an exam",
    #     responses={
    #         204: "No Content",
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

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
            insights = ai_assistant.process_text(
                f"Update exam strategy:\nDays until exam: {days_until_exam}"
            )
            exam.ai_insights = insights
        exam.save()

# ✅ Generate Study Timetable
class GenerateTimetableView(APIView):
    """Generates an AI-powered study timetable based on user inputs, study sessions, and exams"""
    permission_classes = [IsAuthenticated]

    # @swagger_auto_schema(
    #     operation_description="Generate an AI-powered study timetable",
    #     request_body=openapi.Schema(
    #         type=openapi.TYPE_OBJECT,
    #         properties={
    #             'available_hours': openapi.Schema(type=openapi.TYPE_INTEGER, description='Available study hours per day'),
    #             'study_goals': openapi.Schema(type=openapi.TYPE_STRING, description='Custom study goals'),
    #             'priority_subjects': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='List of priority subjects')
    #         },
    #         required=['available_hours']
    #     ),
    #     responses={
    #         200: openapi.Response(
    #             description="Timetable generated successfully",
    #             schema=openapi.Schema(
    #                 type=openapi.TYPE_OBJECT,
    #                 properties={
    #                     'timetable': openapi.Schema(type=openapi.TYPE_STRING)
    #                 }
    #             )
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized"
    #     }
    # )
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

        timetable = ai_assistant.process_text(timetable_input)
        cache.set(query_hash, timetable, timeout=86400)  # Cache for 24 hours

        return Response({"timetable": timetable})
