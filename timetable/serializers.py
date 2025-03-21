from rest_framework import serializers
from .models import StudySession, Exam

class StudySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySession
        fields = ['id', 'user', 'subject', 'start_time', 'end_time', 'is_completed', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'user', 'course_name', 'notes', 'exam_date', 
                 'duration', 'location', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
