# signals.py
from django.dispatch import receiver
from activities.models import Activity
from quizzes.models import TakenQuiz
from django.db.models.signals import post_save

@receiver(post_save, sender=TakenQuiz)
def track_quiz_activity(sender, instance, created, **kwargs):
    """Signal to track quiz completion activity."""
    
    if created:
        Activity.objects.create(
            user=instance.student,
            activity_type=Activity.ActivityType.QUIZ_COMPLETED,
            description=f"Completed '{instance.quiz.title}' with a score of {instance.score}%"
        )