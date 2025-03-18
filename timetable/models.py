from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class StudySession(models.Model):
    """Model representing a study session with start and end times"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='study_sessions')
    subject = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time")
        if self.start_time < timezone.now():
            raise ValidationError("Cannot create study sessions in the past")

    def duration(self):
        """Returns the duration of the study session in minutes"""
        return round((self.end_time - self.start_time).total_seconds() / 60)

    def __str__(self):
        return f"{self.subject} ({self.start_time.strftime('%Y-%m-%d %H:%M')} - {self.end_time.strftime('%H:%M')})"

class Exam(models.Model):
    """Model representing an upcoming exam"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exams')
    course_name = models.CharField(max_length=255)
    exam_date = models.DateField()
    notes = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    duration = models.PositiveIntegerField(help_text="Duration in minutes", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['exam_date']

    def clean(self):
        if self.exam_date < timezone.now().date():
            raise ValidationError("Cannot create exams in the past")

    def days_until(self):
        """Returns the number of days until the exam"""
        return (self.exam_date - timezone.now().date()).days

    def __str__(self):
        return f"{self.course_name} exam on {self.exam_date.strftime('%Y-%m-%d')}"
