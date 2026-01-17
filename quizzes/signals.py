from django.db.models.signals import post_save
from django.dispatch import receiver
from quizzes.models import TakenQuiz
from accounts.models import Profile
from django.db.models import Avg, Sum, Count

@receiver(post_save, sender=TakenQuiz)
def update_user_profile_stats(sender, instance, created, **kwargs):
    """
    Update Profile statistics whenever a TakenQuiz is completed/updated with a score.
    """
    # We only update stats if the quiz is completed (has a score)
    if instance.score is not None:
        user = instance.user
        profile, _ = Profile.objects.get_or_create(user=user)
        
        # Get all completed quizzes for this user
        results = TakenQuiz.objects.filter(user=user, score__isnull=False)
        stats = results.aggregate(
            total_s=Sum('score'),
            count=Count('id'),
            avg_s=Avg('score')
        )
        
        # Update basic stats
        profile.quizzes_taken = stats['count'] or 0
        profile.total_score = stats['total_s'] or 0.0
        
        # Win rate (let's define a win as score >= 50)
        wins = results.filter(score__gte=50.0).count()
        if profile.quizzes_taken > 0:
            profile.win_rate = (wins / profile.quizzes_taken) * 100
        
        # Level calculation (simple: 1 level per 500 total points)
        # You can make this more complex later
        profile.level = int(profile.total_score // 500) + 1
        
        # Duration / Time Played
        total_duration = results.aggregate(total_dur=Sum('duration'))['total_dur']
        profile.time_played = total_duration
        
        # Best Category calculation
        best_cat = results.values('quiz__category__name').annotate(
            avg_score=Avg('score')
        ).order_by('-avg_score').first()
        
        if best_cat:
            profile.best_category = best_cat['quiz__category__name']

        profile.save()
