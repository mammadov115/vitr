from django.db import models
from accounts.models import User
from django.conf import settings

# Create your models here.

class Category(models.Model):
    """Model to represent quiz categories."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True) # For URL usage (e.g., /category/science/)
    icon = models.ImageField(upload_to='category_icons/', null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Quiz(models.Model):
    """Model to represent a quiz."""

    class Difficulty(models.TextChoices):
        EASY = "EASY", "Easy"
        MEDIUM = "MEDIUM", "Medium"
        HARD = "HARD", "Hard"

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='quizzes')
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.EASY)

    # Quiz settings
    time_limit_minutes = models.PositiveIntegerField(default=10) # For timed quizzes
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    """Model to represent a question in a quiz."""

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0) # Soruların sırası için

    def __str__(self):
        return self.text


class Choice(models.Model):
    """Model to represent a choice for a question."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class TakenQuiz(models.Model):
    """Model to represent a quiz taken by a user, storing their performance."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taken_quizzes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    
    score = models.FloatField() # 95.0
    total_questions = models.IntegerField() # 100
    correct_answers = models.IntegerField() # 95
    
    # UI-da gördüyün "12m 0s" üçün
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(null=True, blank=True) # Bitəndə hesablanır

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"