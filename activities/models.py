from django.db import models
from accounts.models import User

# Create your models here.

class Activity(models.Model):
    """Model to track user activities within the application."""
    
    class ActivityType(models.TextChoices):
        QUIZ_COMPLETED = "QUIZ_COMPLETED", "Quiz Completed"
        ACHIEVEMENT_EARNED = "ACHIEVEMENT_EARNED", "Achievement Earned"
        LEVEL_UP = "LEVEL_UP", "Level Up"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ActivityType.choices)
    
    # For storing additional details about the activity
    description = models.CharField(max_length=255) 
    
    # Timestamp of the activity
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # Latest activities first