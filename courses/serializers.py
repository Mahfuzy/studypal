from rest_framework import serializers
from .models import Course, Lesson, Enrollment

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'instructor', 'created_at', 
                 'updated_at', 'is_published', 'thumbnail']
        read_only_fields = ['created_at', 'updated_at']

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'content', 'order', 'duration', 
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'student', 'enrolled_at', 'completed_at', 
                 'progress', 'status']
        read_only_fields = ['enrolled_at', 'completed_at', 'progress', 'status']

class GenerateFlashcardsSerializer(serializers.Serializer):
    text = serializers.CharField(required=True)

