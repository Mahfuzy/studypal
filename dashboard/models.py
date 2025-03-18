from django.conf import settings
from django.db import models

class DashboardStats(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Placeholder for user handling later
    total_learning_time = models.PositiveIntegerField(default=0)  # Minutes
    completed_courses = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    unfinished_courses = models.PositiveIntegerField(default=0)
    next_exam_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Dashboard Stats for User {self.user_id}"
