from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from cloudinary.models import CloudinaryField

class StudyStreak(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='study_streaks')
    current_streak = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    longest_streak = models.IntegerField(default=0, validators=[MinValueValidator(0)]) 
    last_study_date = models.DateField(null=True, blank=True)
    total_study_days = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-current_streak']
        verbose_name_plural = "Study Streaks"

    def __str__(self):
        return f"{self.user.username}'s Streak: {self.current_streak} days"

    def update_streak(self, study_date=None):
        """Update the user's study streak based on study date"""
        if not study_date:
            study_date = timezone.now().date()
        
        if not self.last_study_date:
            self.current_streak = 1
        elif (study_date - self.last_study_date).days == 1:
            self.current_streak += 1
        elif (study_date - self.last_study_date).days == 0:
            return  # Already studied today
        else:
            self.current_streak = 1
        
        self.total_study_days += 1
        self.longest_streak = max(self.longest_streak, self.current_streak)
        self.last_study_date = study_date
        self.save()

class Achievement(models.Model):
    ACHIEVEMENT_TYPES = (
        ('streak', 'Streak Milestone'),
        ('quiz', 'Quiz Performance'),
        ('course', 'Course Completion'),
        ('engagement', 'Platform Engagement')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=255)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    icon = CloudinaryField(null=True, blank=True)
    awarded_on = models.DateTimeField(auto_now_add=True)
    points = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ['-awarded_on']
        verbose_name_plural = "Achievements"

    def __str__(self):
        return f"{self.title} - Awarded to {self.user.username}"

class XPSystem(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="xp")
    total_xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = "XP System"
        verbose_name_plural = "XP Systems"

    def __str__(self):
        return f"{self.user.username} - Level {self.level} ({self.total_xp} XP)"

    def add_xp(self, amount):
        """
        Increase XP and level up if needed
        Args:
            amount (int): Amount of XP to add
        """
        if amount < 0:
            raise ValueError("XP amount cannot be negative")
            
        self.total_xp += amount
        self.level = self.calculate_level()
        self.save()

    def calculate_level(self):
        """Calculate level based on XP thresholds"""
        return max(1, (self.total_xp // 100) + 1)

class Badge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="badges")
    title = models.CharField(max_length=255)
    description = models.TextField()
    icon = CloudinaryField(null=True, blank=True)
    awarded_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Badges"

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class Leaderboard(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leaderboard")
    total_xp = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Leaderboards"
        ordering = ['-total_xp']

    def __str__(self):
        return f"{self.user.username} - {self.total_xp} XP"

    def update_xp(self):
        """Sync leaderboard XP with user's XP system"""
        self.total_xp = self.user.xp.total_xp
        self.save()
