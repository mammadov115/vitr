import pytest
from quizzes.models import Category, Quiz, Question, Choice, TakenQuiz
from accounts.models import User, Profile
from django.utils import timezone
from datetime import timedelta

@pytest.mark.django_db
class TestQuizzesSignals:

    def test_profile_updates_on_quiz_completion(self):
        """Test that profile stats increase when a quiz is completed."""
        user = User.objects.create_user(email="signal@test.com", username="signaluser", password="pass")
        # Profile is created via accounts.signals
        profile = user.profile
        
        category = Category.objects.create(name="Science", slug="science")
        quiz = Quiz.objects.create(title="Bio", category=category)
        
        # Initial stats
        assert profile.quizzes_taken == 0
        assert profile.total_score == 0.0
        
        # Create attempt (started)
        attempt = TakenQuiz.objects.create(
            user=user,
            quiz=quiz,
            started_at=timezone.now()
        )
        
        # Profile should NOT update yet (no score)
        profile.refresh_from_db()
        assert profile.quizzes_taken == 0
        
        # Complete the quiz (save with score)
        attempt.score = 80.0
        attempt.correct_answers = 4
        attempt.total_questions = 5
        attempt.duration = timedelta(minutes=2)
        attempt.save()
        
        # Refresh profile and check updates
        profile.refresh_from_db()
        assert profile.quizzes_taken == 1
        assert profile.total_score == 80.0
        assert profile.level == 1 # (80 // 500) + 1 = 1
        assert profile.best_category == "Science"

    def test_level_up_calculation(self):
        """Test that level increases based on total score milestones."""
        user = User.objects.create_user(email="level@test.com", username="leveluser", password="pass")
        profile = user.profile
        category = Category.objects.create(name="Math", slug="math")
        quiz = Quiz.objects.create(title="Calculus", category=category)
        
        # Large score to jump levels (e.g., 1200 points)
        # 1200 // 500 + 1 = level 3
        TakenQuiz.objects.create(
            user=user,
            quiz=quiz,
            score=1200.0,
            started_at=timezone.now(),
            duration=timedelta(minutes=5)
        )
        
        profile.refresh_from_db()
        assert profile.level == 3
