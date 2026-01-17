from rest_framework import serializers
from .models import Category, Quiz, Question, Choice, TakenQuiz

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for quiz categories."""
    quiz_count = serializers.IntegerField(source='quizzes.count', read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'icon', 'description', 'quiz_count')


class ChoiceSerializer(serializers.ModelSerializer):
    """Serializer for question choices - NO 'is_correct' for security."""
    class Meta:
        model = Choice
        fields = ('id', 'text')


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for questions, including their choices."""
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'order', 'choices')


class QuizSerializer(serializers.ModelSerializer):
    """Serializer for basic quiz information."""
    category_name = serializers.ReadOnlyField(source='category.name')
    question_count = serializers.IntegerField(source='questions.count', read_only=True)

    class Meta:
        model = Quiz
        fields = (
            'id', 'title', 'description', 'category', 'category_name', 
            'difficulty', 'time_limit_minutes', 'is_active', 
            'question_count', 'created_at'
        )


class QuizDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed quiz information including questions."""
    questions = QuestionSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Quiz
        fields = (
            'id', 'title', 'description', 'category', 'difficulty', 
            'time_limit_minutes', 'questions'
        )


class TakenQuizSerializer(serializers.ModelSerializer):
    """Serializer for tracking user quiz attempts and results."""
    user_username = serializers.ReadOnlyField(source='user.username')
    quiz_title = serializers.ReadOnlyField(source='quiz.title')

    class Meta:
        model = TakenQuiz
        fields = (
            'id', 'user', 'user_username', 'quiz', 'quiz_title', 
            'score', 'total_questions', 'correct_answers', 
            'started_at', 'completed_at', 'duration'
        )
        read_only_fields = ('completed_at', 'duration')
