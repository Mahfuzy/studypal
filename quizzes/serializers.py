from rest_framework import serializers
from .models import Quiz, Question, Answer, QuizAttempt

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct', 'explanation']

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'points', 'order', 'answers']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'course', 'title', 'description', 'time_limit',
            'pass_percentage', 'created_at', 'updated_at',
            'is_published', 'questions'
        ]

class QuizAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'user', 'score', 'started_at',
            'completed_at', 'status', 'time_spent', 'passed'
        ]
        read_only_fields = ['user', 'score', 'started_at', 'completed_at', 'time_spent', 'passed']

