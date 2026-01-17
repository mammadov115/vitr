from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from quizzes.models import Category, Quiz, TakenQuiz, Choice
from quizzes.serializers import (
    CategorySerializer, QuizSerializer, QuizDetailSerializer, 
    TakenQuizSerializer
)
from core.permissions import IsAdminOrReadOnly, IsOwnerOnly

from django.utils import timezone
from django.db import models


# --- Category Views ---

class CategoryListView(generics.ListAPIView):
    """List all quiz categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema(operation_summary="List all quiz categories")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CategoryDetailView(generics.RetrieveAPIView):
    """Get category details by slug."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    @swagger_auto_schema(operation_summary="Get category details by slug")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# --- Quiz Views ---

class QuizListView(generics.ListAPIView):
    """List all active quizzes. Supports filtering by category and search by title."""
    serializer_class = QuizSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Quiz.objects.filter(is_active=True).select_related('category')
        
        # Category Filter
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
            
        # Search functionality
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
            
        return queryset

    @swagger_auto_schema(
        operation_summary="List all active quizzes",
        manual_parameters=[
            openapi.Parameter(
                'category', 
                openapi.IN_QUERY, 
                description="Filter quizzes by category slug", 
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'search', 
                openapi.IN_QUERY, 
                description="Search quizzes by title", 
                type=openapi.TYPE_STRING
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class QuizDetailView(generics.RetrieveAPIView):
    """Get full quiz details. Optimized with prefetch_related."""
    queryset = Quiz.objects.filter(is_active=True).prefetch_related('questions__choices', 'category')
    serializer_class = QuizDetailSerializer
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema(operation_summary="Get full quiz details")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)




class QuizStartView(APIView):
    """
    Initialize a quiz attempt. Records the start time in the DB.
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Start a quiz session",
        responses={201: openapi.Response(description="Quiz session created")}
    )
    def post(self, request, pk, *args, **kwargs):
        quiz = generics.get_object_or_404(Quiz, pk=pk, is_active=True)
        
        # Create an 'ongoing' attempt
        attempt = TakenQuiz.objects.create(
            user=request.user,
            quiz=quiz,
            started_at=timezone.now()
        )
        
        return Response({
            "message": f"Quiz '{quiz.title}' started.",
            "attempt_id": attempt.id,
            "quiz_id": quiz.id,
            "time_limit": quiz.time_limit_minutes
        }, status=status.HTTP_201_CREATED)


class TakenQuizListView(generics.ListAPIView):
    """List current user's quiz history."""
    serializer_class = TakenQuizSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOnly]

    def get_queryset(self):
        return TakenQuiz.objects.filter(user=self.request.user).select_related('quiz')

    @swagger_auto_schema(operation_summary="List current user's quiz history")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TakenQuizCreateView(generics.CreateAPIView):
    """
    Submit quiz results. Validates time limit and calculates the final score.
    """
    serializer_class = TakenQuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Submit quiz results",
        manual_parameters=[
            openapi.Parameter(
                'attempt_id', 
                openapi.IN_QUERY, 
                description="ID of the attempt created at start (can be passed in URL query or request body)", 
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        # We try to get attempt_id from query params or the request body
        attempt_id = request.query_params.get('attempt_id') or request.data.get('attempt_id')
        if not attempt_id:
            return Response({"error": "attempt_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        attempt = generics.get_object_or_404(TakenQuiz, id=attempt_id, user=request.user)
        
        if attempt.score is not None:
            return Response({"error": "This attempt has already been submitted."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Time Validation
        now = timezone.now()
        elapsed_time = now - attempt.started_at
        time_limit_delta = timezone.timedelta(minutes=attempt.quiz.time_limit_minutes)
        
        # Allow 30 seconds grace period for network latency
        if elapsed_time > (time_limit_delta + timezone.timedelta(seconds=30)):
            return Response({
                "error": "Time limit exceeded.",
                "elapsed_seconds": elapsed_time.total_seconds(),
                "limit_seconds": time_limit_delta.total_seconds()
            }, status=status.HTTP_403_FORBIDDEN)

        # 2. Results Calculation
        user_answers_ids = request.data.get('answers', []) # List of Choice IDs
        if not isinstance(user_answers_ids, list):
            return Response({"error": "answers must be a list"}, status=status.HTTP_400_BAD_REQUEST)

        # Get all correct choices for this quiz
        correct_choices_ids = Choice.objects.filter(
            question__quiz=attempt.quiz, 
            is_correct=True
        ).values_list('id', flat=True)

        correct_count = 0
        for choice_id in user_answers_ids:
            if choice_id in correct_choices_ids:
                correct_count += 1

        total_questions = attempt.quiz.questions.count()
        if total_questions > 0:
            score_percentage = (correct_count / total_questions) * 100
        else:
            score_percentage = 0

        attempt.score = round(score_percentage, 2)
        attempt.correct_answers = correct_count
        attempt.total_questions = total_questions
        attempt.completed_at = now
        attempt.duration = elapsed_time
        attempt.save()

        return Response({
            "id": attempt.id,
            "score": attempt.score,
            "correct_answers": attempt.correct_answers,
            "total_questions": attempt.total_questions,
            "message": "Results calculated and saved successfully."
        }, status=status.HTTP_200_OK)
