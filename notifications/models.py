from django.db import models
from django.contrib.auth import get_user_model
from django.core.cache import cache
from celery import shared_task

User = get_user_model()

class Notification(models.Model):
    """Stores notifications for users"""
    NOTIFICATION_TYPES = (
        ('achievement', 'Achievement'),
        ('streak', 'Streak'),
        ('study_reminder', 'Study Reminder'), 
        ('exam_reminder', 'Exam Reminder'),
        ('course_update', 'Course Update'),
        ('quiz_result', 'Quiz Result'),
        ('ai_insight', 'AI Insight'),
        ('system', 'System')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    source_id = models.IntegerField(null=True, blank=True)  # ID of related object (quiz, course etc)
    source_model = models.CharField(max_length=50, null=True, blank=True)  # Model name of source
    ai_enhanced = models.BooleanField(default=False)
    ai_insights = models.TextField(null=True, blank=True)
    priority = models.IntegerField(default=0)  # Higher number = higher priority

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

    @property
    def is_ai_enhanced(self):
        return bool(self.ai_insights)

class NotificationPreference(models.Model):
    """Stores user preferences for notifications"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="notification_prefs")
    email_notifications = models.BooleanField(default=True) 
    push_notifications = models.BooleanField(default=True)
    web_notifications = models.BooleanField(default=True)
    
    # Granular notification preferences
    achievement_notifications = models.BooleanField(default=True)
    streak_notifications = models.BooleanField(default=True)
    study_reminder_notifications = models.BooleanField(default=True)
    exam_reminder_notifications = models.BooleanField(default=True)
    course_update_notifications = models.BooleanField(default=True)
    quiz_result_notifications = models.BooleanField(default=True)
    ai_insight_notifications = models.BooleanField(default=True)
    
    # Notification frequency preferences
    daily_notification_limit = models.IntegerField(default=10)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"Preferences of {self.user.username}"

    def can_send_notification(self, notification_type):
        """Check if a notification type is enabled"""
        pref_map = {
            'achievement': self.achievement_notifications,
            'streak': self.streak_notifications,
            'study_reminder': self.study_reminder_notifications,
            'exam_reminder': self.exam_reminder_notifications,
            'course_update': self.course_update_notifications,
            'quiz_result': self.quiz_result_notifications,
            'ai_insight': self.ai_insight_notifications,
        }
        return pref_map.get(notification_type, True)
