import pytest
from quizzes.models import Category, Quiz, Question, Choice, TakenQuiz
from quizzes.serializers import (
    CategorySerializer, QuizSerializer, QuestionSerializer, 
    ChoiceSerializer, QuizDetailSerializer, TakenQuizSerializer
)
from django.utils import timezone
from datetime import timedelta
from accounts.models import User

@pytest.mark.django_db
class TestQuizzesSerializers:

    def test_category_serializer(self):
        """Test CategorySerializer fields and quiz_count."""
        category = Category.objects.create(name="Science", slug="science")
        Quiz.objects.create(title="Biology", category=category)
        Quiz.objects.create(title="Physics", category=category)
        
        serializer = CategorySerializer(category)
        data = serializer.data
        
        assert data['name'] == "Science"
        assert data['quiz_count'] == 2
        assert 'slug' in data

    def test_quiz_serializer(self):
        """Test QuizSerializer fields and question_count."""
        category = Category.objects.create(name="Math", slug="math")
        quiz = Quiz.objects.create(title="Calculus", category=category)
        Question.objects.create(quiz=quiz, text="Q1")
        Question.objects.create(quiz=quiz, text="Q2")
        
        serializer = QuizSerializer(quiz)
        data = serializer.data
        
        assert data['title'] == "Calculus"
        assert data['category_name'] == "Math"
        assert data['question_count'] == 2

    def test_question_serializer(self):
        """Test QuestionSerializer with nested choices."""
        category = Category.objects.create(name="History", slug="history")
        quiz = Quiz.objects.create(title="WW2", category=category)
        question = Question.objects.create(quiz=quiz, text="When did WW2 start?")
        Choice.objects.create(question=question, text="1939", is_correct=True)
        Choice.objects.create(question=question, text="1945", is_correct=False)
        
        serializer = QuestionSerializer(question)
        data = serializer.data
        
        assert data['text'] == "When did WW2 start?"
        assert len(data['choices']) == 2
        assert data['choices'][0]['text'] == "1939"

    def test_quiz_detail_serializer(self):
        """Test QuizDetailSerializer with nested questions and categories."""
        category = Category.objects.create(name="Geography", slug="geo")
        quiz = Quiz.objects.create(title="Capitals", category=category)
        Question.objects.create(quiz=quiz, text="Capital of France?")
        
        serializer = QuizDetailSerializer(quiz)
        data = serializer.data
        
        assert data['title'] == "Capitals"
        assert data['category']['name'] == "Geography"
        assert len(data['questions']) == 1

    def test_taken_quiz_serializer(self):
        """Test TakenQuizSerializer fields."""
        user = User.objects.create_user(email="user@test.com", username="tester", password="pass")
        category = Category.objects.create(name="Music", slug="music")
        quiz = Quiz.objects.create(title="Rock Stars", category=category)
        
        taken_quiz = TakenQuiz.objects.create(
            user=user,
            quiz=quiz,
            score=100.0,
            total_questions=5,
            correct_answers=5,
            started_at=timezone.now()
        )
        
        serializer = TakenQuizSerializer(taken_quiz)
        data = serializer.data
        
        assert data['user_username'] == "tester"
        assert data['quiz_title'] == "Rock Stars"
        assert data['score'] == 100.0
