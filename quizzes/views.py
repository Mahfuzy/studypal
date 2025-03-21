from rest_framework import generics
from django.core.cache import cache
from .models import Quiz, Question, Answer, QuizAttempt
from .serializers import QuizSerializer, QuestionSerializer, AnswerSerializer, QuizAttemptSerializer
from study_assistant.ai_service import TaeAI
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# ------------------------- API Views -------------------------

class QuizListCreateView(generics.ListCreateAPIView):
    """List and create quizzes with AI-generated insights."""
    permission_classes = [IsAuthenticated]
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    # @swagger_auto_schema(
    #     operation_description="List all quizzes",
    #     responses={
    #         200: openapi.Response(
    #             description="List of quizzes",
    #             schema=QuizSerializer(many=True)
    #         ),
    #         401: "Unauthorized"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Create a new quiz",
    #     request_body=QuizSerializer,
    #     responses={
    #         201: openapi.Response(
    #             description="Quiz created successfully",
    #             schema=QuizSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized"
    #     }
    # )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        quiz = serializer.save()
        some_task_function()

class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a quiz with AI-powered insights."""
    permission_classes = [IsAuthenticated]
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    # @swagger_auto_schema(
    #     operation_description="Retrieve a quiz",
    #     responses={
    #         200: openapi.Response(
    #             description="Quiz details",
    #             schema=QuizSerializer
    #         ),
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Update a quiz",
    #     request_body=QuizSerializer,
    #     responses={
    #         200: openapi.Response(
    #             description="Quiz updated successfully",
    #             schema=QuizSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Delete a quiz",
    #     responses={
    #         204: "No Content",
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_update(self, serializer):
        quiz = serializer.save()
        some_task_function()

class QuestionListCreateView(generics.ListCreateAPIView):
    """List and create questions with AI-assisted insights."""
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer

    # @swagger_auto_schema(
    #     operation_description="List all questions for a quiz",
    #     responses={
    #         200: openapi.Response(
    #             description="List of questions",
    #             schema=QuestionSerializer(many=True)
    #         ),
    #         401: "Unauthorized",
    #         404: "Quiz not found"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Create a new question",
    #     request_body=QuestionSerializer,
    #     responses={
    #         201: openapi.Response(
    #             description="Question created successfully",
    #             schema=QuestionSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized",
    #         404: "Quiz not found"
    #     }
    # )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return Question.objects.filter(quiz_id=self.kwargs['quiz_id'])

    def perform_create(self, serializer):
        question = serializer.save(quiz_id=self.kwargs['quiz_id'])
        some_task_function()

class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a question with AI-powered improvements."""
    permission_classes = [IsAuthenticated]
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    # @swagger_auto_schema(
    #     operation_description="Retrieve a question",
    #     responses={
    #         200: openapi.Response(
    #             description="Question details",
    #             schema=QuestionSerializer
    #         ),
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Update a question",
    #     request_body=QuestionSerializer,
    #     responses={
    #         200: openapi.Response(
    #             description="Question updated successfully",
    #             schema=QuestionSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Delete a question",
    #     responses={
    #         204: "No Content",
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_update(self, serializer):
        question = serializer.save()
        some_task_function()

class AnswerListCreateView(generics.ListCreateAPIView):
    """List and create answers with AI-generated explanations."""
    permission_classes = [IsAuthenticated]
    serializer_class = AnswerSerializer

    # @swagger_auto_schema(
    #     operation_description="List all answers for a question",
    #     responses={
    #         200: openapi.Response(
    #             description="List of answers",
    #             schema=AnswerSerializer(many=True)
    #         ),
    #         401: "Unauthorized",
    #         404: "Question not found"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Create a new answer",
    #     request_body=AnswerSerializer,
    #     responses={
    #         201: openapi.Response(
    #             description="Answer created successfully",
    #             schema=AnswerSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized",
    #         404: "Question not found"
    #     }
    # )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return Answer.objects.filter(question_id=self.kwargs['question_id'])

    def perform_create(self, serializer):
        answer = serializer.save(question_id=self.kwargs['question_id'])
        some_task_function()

class AnswerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an answer with AI-powered assessments."""
    permission_classes = [IsAuthenticated]
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    # @swagger_auto_schema(
    #     operation_description="Retrieve an answer",
    #     responses={
    #         200: openapi.Response(
    #             description="Answer details",
    #             schema=AnswerSerializer
    #         ),
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Update an answer",
    #     request_body=AnswerSerializer,
    #     responses={
    #         200: openapi.Response(
    #             description="Answer updated successfully",
    #             schema=AnswerSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Delete an answer",
    #     responses={
    #         204: "No Content",
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_update(self, serializer):
        answer = serializer.save()
        some_task_function()

class QuizAttemptListCreateView(generics.ListCreateAPIView):
    """List and create quiz attempts with AI-generated recommendations."""
    permission_classes = [IsAuthenticated]
    serializer_class = QuizAttemptSerializer

    # @swagger_auto_schema(
    #     operation_description="List all quiz attempts for the current user",
    #     responses={
    #         200: openapi.Response(
    #             description="List of quiz attempts",
    #             schema=QuizAttemptSerializer(many=True)
    #         ),
    #         401: "Unauthorized"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Create a new quiz attempt",
    #     request_body=QuizAttemptSerializer,
    #     responses={
    #         201: openapi.Response(
    #             description="Quiz attempt created successfully",
    #             schema=QuizAttemptSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized"
    #     }
    # )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        attempt = serializer.save(user=self.request.user)
        some_task_function()

class QuizAttemptDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update quiz attempts with AI performance analysis."""
    permission_classes = [IsAuthenticated]
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer

    # @swagger_auto_schema(
    #     operation_description="Retrieve a quiz attempt",
    #     responses={
    #         200: openapi.Response(
    #             description="Quiz attempt details",
    #             schema=QuizAttemptSerializer
    #         ),
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Update a quiz attempt",
    #     request_body=QuizAttemptSerializer,
    #     responses={
    #         200: openapi.Response(
    #             description="Quiz attempt updated successfully",
    #             schema=QuizAttemptSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def perform_update(self, serializer):
        attempt = serializer.save()
        some_task_function()

def some_task_function():
    # Task logic here
    pass
