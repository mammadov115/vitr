import pytest
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from quizzes.models import Category, Quiz, Question, Choice, TakenQuiz
from accounts.models import User

@pytest.mark.django_db
class TestQuizzesViews:

    @pytest.fixture
    def api_client(self):
        from rest_framework.test import APIClient
        return APIClient()

    @pytest.fixture
    def test_user(self):
        return User.objects.create_user(email="test@example.com", username="testuser", password="password123")

    @pytest.fixture
    def setup_quiz(self):
        category = Category.objects.create(name="Science", slug="science")
        quiz = Quiz.objects.create(title="Biology Quiz", category=category, time_limit_minutes=10)
        q1 = Question.objects.create(quiz=quiz, text="What is a cell?")
        c1 = Choice.objects.create(question=q1, text="Basic unit of life", is_correct=True)
        c2 = Choice.objects.create(question=q1, text="A car part", is_correct=False)
        
        q2 = Question.objects.create(quiz=quiz, text="What is DNA?")
        c3 = Choice.objects.create(question=q2, text="Genetic material", is_correct=True)
        c4 = Choice.objects.create(question=q2, text="A type of food", is_correct=False)
        
        return quiz, [c1.id, c3.id], [c2.id, c4.id]

    def test_start_quiz_creates_attempt(self, api_client, test_user, setup_quiz):
        """Test that starting a quiz creates a TakenQuiz record in the DB."""
        quiz, correct_ids, wrong_ids = setup_quiz
        api_client.force_authenticate(user=test_user)
        
        url = reverse('quiz-start', kwargs={'pk': quiz.id, 'version': 'v1'})
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert "attempt_id" in response.data
        assert TakenQuiz.objects.filter(user=test_user, quiz=quiz).count() == 1

    def test_submit_quiz_calculates_score_correctly(self, api_client, test_user, setup_quiz):
        """Test submitting correct answers gives 100%."""
        quiz, correct_ids, wrong_ids = setup_quiz
        api_client.force_authenticate(user=test_user)
        
        # Start
        start_url = reverse('quiz-start', kwargs={'pk': quiz.id, 'version': 'v1'})
        start_res = api_client.post(start_url)
        attempt_id = start_res.data['attempt_id']
        
        # Submit correct answers
        submit_url = reverse('quiz-submit', kwargs={'version': 'v1'})
        payload = {
            "attempt_id": attempt_id,
            "answers": correct_ids
        }
        response = api_client.post(submit_url, payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['score'] == 100.0
        assert response.data['correct_answers'] == 2

    def test_submit_quiz_time_limit_exceeded(self, api_client, test_user, setup_quiz):
        """Test that submitting after the time limit (plus grace) results in a 403."""
        quiz, correct_ids, wrong_ids = setup_quiz
        api_client.force_authenticate(user=test_user)
        
        # Create an attempt that started 15 minutes ago (limit is 10 mins)
        old_start = timezone.now() - timedelta(minutes=15)
        attempt = TakenQuiz.objects.create(
            user=test_user,
            quiz=quiz,
            started_at=old_start
        )
        
        submit_url = reverse('quiz-submit', kwargs={'version': 'v1'})
        payload = {
            "attempt_id": attempt.id,
            "answers": correct_ids
        }
        response = api_client.post(submit_url, payload, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Time limit exceeded" in response.data['error']

    def test_submit_quiz_wrong_answers(self, api_client, test_user, setup_quiz):
        """Test that submitting wrong answers results in 0 score."""
        quiz, correct_ids, wrong_ids = setup_quiz
        api_client.force_authenticate(user=test_user)
        
        attempt = TakenQuiz.objects.create(user=test_user, quiz=quiz, started_at=timezone.now())
        
        submit_url = reverse('quiz-submit', kwargs={'version': 'v1'})
        payload = {
            "attempt_id": attempt.id,
            "answers": wrong_ids # 0 correct
        }
        response = api_client.post(submit_url, payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['score'] == 0.0
        assert response.data['correct_answers'] == 0

    def test_cannot_submit_same_attempt_twice(self, api_client, test_user, setup_quiz):
        """Test that an attempt cannot be submitted more than once."""
        quiz, correct_ids, wrong_ids = setup_quiz
        api_client.force_authenticate(user=test_user)
        
        attempt = TakenQuiz.objects.create(user=test_user, quiz=quiz, started_at=timezone.now())
        
        submit_url = reverse('quiz-submit', kwargs={'version': 'v1'})
        payload = {"attempt_id": attempt.id, "answers": correct_ids}
        
        # First submission
        api_client.post(submit_url, payload, format='json')
        
        # Second submission
        response = api_client.post(submit_url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already been submitted" in response.data['error']

    def test_filter_quizzes_by_category(self, api_client, test_user):
        """Test filtering quiz list by category slug."""
        cat1 = Category.objects.create(name="History", slug="history")
        cat2 = Category.objects.create(name="Math", slug="math")
        Quiz.objects.create(title="WW2", category=cat1, is_active=True)
        Quiz.objects.create(title="Algebra", category=cat2, is_active=True)
        
        url = reverse('quiz-list', kwargs={'version': 'v1'})
        
        # Filter by history
        response = api_client.get(f"{url}?category=history")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == "WW2"
        
        # Filter by math
        response = api_client.get(f"{url}?category=math")
        assert len(response.data) == 1
        assert response.data[0]['title'] == "Algebra"
