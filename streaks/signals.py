from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import StudyStreak, Achievement, XPSystem, Leaderboard
from quizzes.models import QuizAttempt
from courses.models import Enrollment

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_gamification(sender, instance, created, **kwargs):
    """Create gamification objects when a new user is created"""
    if created:
        StudyStreak.objects.create(user=instance)
        XPSystem.objects.create(user=instance)
        Leaderboard.objects.create(user=instance)

@receiver(post_save, sender=QuizAttempt)
def handle_quiz_completion(sender, instance, **kwargs):
    """Handle quiz completion achievements and XP"""
    if instance.status == 'completed':
        # Add XP for completing quiz
        xp_amount = int(instance.score)  # XP based on quiz score
        instance.user.xp.add_xp(xp_amount)
        instance.user.leaderboard.update_xp()

        # Check for achievements
        if instance.passed:
            Achievement.objects.create(
                user=instance.user,
                title="Quiz Master",
                description=f"Passed {instance.quiz.title} with {instance.score}%",
                achievement_type='quiz',
                points=50
            )

@receiver(post_save, sender=Enrollment)
def handle_course_completion(sender, instance, **kwargs):
    """Handle course completion achievements and XP"""
    if instance.status == 'completed' and instance.completed_at:
        # Add XP for completing course
        xp_amount = 100  # Base XP for course completion
        instance.student.xp.add_xp(xp_amount)
        instance.student.leaderboard.update_xp()

        # Create achievement
        Achievement.objects.create(
            user=instance.student,
            title="Course Champion",
            description=f"Completed {instance.course.title}",
            achievement_type='course',
            points=100
        )

@receiver(post_save, sender=StudyStreak)
def handle_streak_milestones(sender, instance, **kwargs):
    """Handle streak-based achievements"""
    streak_milestones = {
        7: ("Week Warrior", "Maintained a 7-day study streak", 70),
        30: ("Monthly Master", "Maintained a 30-day study streak", 300),
        100: ("Centurion", "Maintained a 100-day study streak", 1000),
    }

    for days, (title, desc, points) in streak_milestones.items():
        if instance.current_streak == days:
            Achievement.objects.create(
                user=instance.user,
                title=title,
                description=desc,
                achievement_type='streak',
                points=points
            )
            # Add XP for streak milestone
            instance.user.xp.add_xp(points)
            instance.user.leaderboard.update_xp()
