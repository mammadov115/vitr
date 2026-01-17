from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView,
    QuizListView, QuizDetailView, QuizStartView,
    TakenQuizListView, TakenQuizCreateView
)

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    
    # Quizzes
    path('list/', QuizListView.as_view(), name='quiz-list'),
    path('list/<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('list/<int:pk>/start/', QuizStartView.as_view(), name='quiz-start'),
    
    # History & Attempts
    path('history/', TakenQuizListView.as_view(), name='quiz-history'),
    path('submit/', TakenQuizCreateView.as_view(), name='quiz-submit'),
]
