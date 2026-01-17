import pytest
from django.utils import timezone
from datetime import timedelta
from quizzes.models import Category, Quiz, Question, Choice, TakenQuiz
from accounts.models import User

@pytest.mark.django_db
class TestQuizzesModels:
    """For testing quizzes models"""

    def test_category_creation(self):
        """For testing category creation"""
        category = Category.objects.create(
            name="Science",
            slug="science",
            description="Science related quizzes"
        )
        assert category.name == "Science"
        assert str(category) == "Science"
        assert category.slug == "science"
        assert category._meta.verbose_name_plural == "Categories"

    def test_quiz_creation(self):
        """For testing quiz creation"""
        category = Category.objects.create(name="History", slug="history")
        quiz = Quiz.objects.create(
            title="World War II",
            description="A quiz about WWII",
            category=category,
            difficulty=Quiz.Difficulty.MEDIUM,
            time_limit_minutes=15
        )
        assert quiz.title == "World War II"
        assert str(quiz) == "World War II"
        assert quiz.category == category
        assert quiz.difficulty == Quiz.Difficulty.MEDIUM
        assert quiz.is_active is True

    def test_question_creation(self):
        """For testing question creation"""
        category = Category.objects.create(name="Math", slug="math")
        quiz = Quiz.objects.create(title="Algebra", description="Math quiz", category=category)
        question = Question.objects.create(
            quiz=quiz,
            text="What is 2+2?",
            order=1
        )
        assert question.text == "What is 2+2?"
        assert str(question) == "What is 2+2?"
        assert question.quiz == quiz
        assert question.order == 1

    def test_choice_creation(self):
        """For testing choice creation"""
        category = Category.objects.create(name="General", slug="general")
        quiz = Quiz.objects.create(title="General Knowledge", description="General quiz", category=category)
        question = Question.objects.create(quiz=quiz, text="Question 1")
        choice = Choice.objects.create(
            question=question,
            text="Correct Answer",
            is_correct=True
        )
        assert choice.text == "Correct Answer"
        assert str(choice) == "Correct Answer"
        assert choice.is_correct is True
        assert choice.question == question

    def test_taken_quiz_creation(self):
        """For testing taken quiz creation"""
        user = User.objects.create_user(email="test@example.com", username="testuser", password="password")
        category = Category.objects.create(name="Sports", slug="sports")
        quiz = Quiz.objects.create(title="Football", description="Football quiz", category=category)
        
        started_at = timezone.now() - timedelta(minutes=5)
        taken_quiz = TakenQuiz.objects.create(
            user=user,
            quiz=quiz,
            score=80.0,
            total_questions=10,
            correct_answers=8,
            started_at=started_at,
            duration=timedelta(minutes=5)
        )
        
        assert taken_quiz.user == user
        assert taken_quiz.quiz == quiz
        assert taken_quiz.score == 80.0
        assert str(taken_quiz) == "testuser - Football"
        assert taken_quiz.duration == timedelta(minutes=5)
        assert taken_quiz.completed_at is not None
