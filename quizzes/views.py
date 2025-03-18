from rest_framework import generics
from django.core.cache import cache
from celery import shared_task
from .models import Quiz, Question, Answer, QuizAttempt
from .serializers import QuizSerializer, QuestionSerializer, AnswerSerializer, QuizAttemptSerializer
from study_assistant.ai_service import TaeAI

# ------------------------- Celery Tasks -------------------------

@shared_task
def generate_quiz_insights(quiz_id):
    """AI-generated quiz analysis."""
    quiz = Quiz.objects.filter(id=quiz_id).first()
    if not quiz:
        return "Quiz not found."

    cache_key = f'quiz_insights_{quiz_id}'
    
    # Check if cached insights exist
    existing_insights = cache.get(cache_key)
    if existing_insights and quiz.ai_insights == existing_insights:
        return "Insights already generated."

    ai_assistant = TaeAI()
    insights = ai_assistant.process_text(
        f"Analyze quiz content:\nTitle: {quiz.title}\nDescription: {quiz.description}"
    )

    quiz.ai_insights = insights
    quiz.save()
    cache.set(cache_key, insights, timeout=3600)  # Cache for 1 hour
    return insights

@shared_task
def generate_question_insights(question_id):
    """AI-generated question analysis."""
    question = Question.objects.filter(id=question_id).first()
    if not question:
        return "Question not found."

    cache_key = f'question_insights_{question_id}'
    
    ai_assistant = TaeAI()
    insights = ai_assistant.process_text(
        f"Analyze question:\nText: {question.text}"
    )

    question.ai_insights = insights
    question.save()
    cache.set(cache_key, insights, timeout=3600)
    return insights

@shared_task
def generate_answer_explanation(answer_id):
    """AI-generated answer explanation."""
    answer = Answer.objects.filter(id=answer_id).first()
    if not answer:
        return "Answer not found."

    cache_key = f'answer_explanation_{answer_id}'
    
    ai_assistant = TaeAI()
    insights = ai_assistant.process_text(
        f"Generate explanation for answer:\nText: {answer.text}"
    )

    answer.ai_insights = insights
    answer.save()
    cache.set(cache_key, insights, timeout=3600)
    return insights

@shared_task
def generate_quiz_attempt_analysis(attempt_id):
    """AI-generated quiz attempt performance analysis."""
    attempt = QuizAttempt.objects.filter(id=attempt_id).first()
    if not attempt:
        return "Attempt not found."

    cache_key = f'quiz_attempt_analysis_{attempt_id}'

    ai_assistant = TaeAI()
    insights = ai_assistant.process_text(
        f"Analyze quiz attempt performance:\nScore: {attempt.score}\nTime spent: {attempt.time_spent}"
    )

    attempt.ai_insights = insights
    attempt.save()
    cache.set(cache_key, insights, timeout=3600)
    return insights

# ------------------------- API Views -------------------------

class QuizListCreateView(generics.ListCreateAPIView):
    """List and create quizzes with AI-generated insights."""
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def perform_create(self, serializer):
        quiz = serializer.save()
        generate_quiz_insights.delay(quiz.id)

class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a quiz with AI-powered insights."""
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def perform_update(self, serializer):
        quiz = serializer.save()
        generate_quiz_insights.delay(quiz.id)

class QuestionListCreateView(generics.ListCreateAPIView):
    """List and create questions with AI-assisted insights."""
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.filter(quiz_id=self.kwargs['quiz_id'])

    def perform_create(self, serializer):
        question = serializer.save(quiz_id=self.kwargs['quiz_id'])
        generate_question_insights.delay(question.id)

class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a question with AI-powered improvements."""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def perform_update(self, serializer):
        question = serializer.save()
        generate_question_insights.delay(question.id)

class AnswerListCreateView(generics.ListCreateAPIView):
    """List and create answers with AI-generated explanations."""
    serializer_class = AnswerSerializer

    def get_queryset(self):
        return Answer.objects.filter(question_id=self.kwargs['question_id'])

    def perform_create(self, serializer):
        answer = serializer.save(question_id=self.kwargs['question_id'])
        generate_answer_explanation.delay(answer.id)

class AnswerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an answer with AI-powered assessments."""
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def perform_update(self, serializer):
        answer = serializer.save()
        generate_answer_explanation.delay(answer.id)

class QuizAttemptListCreateView(generics.ListCreateAPIView):
    """List and create quiz attempts with AI-generated recommendations."""
    serializer_class = QuizAttemptSerializer

    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        attempt = serializer.save(user=self.request.user)
        generate_quiz_attempt_analysis.delay(attempt.id)

class QuizAttemptDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update quiz attempts with AI performance analysis."""
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer

    def perform_update(self, serializer):
        attempt = serializer.save()
        generate_quiz_attempt_analysis.delay(attempt.id)
