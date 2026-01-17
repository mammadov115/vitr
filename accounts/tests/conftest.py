import pytest
from django.contrib.auth import get_user_model
from accounts.models import Achievement
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def api_client():
    """Fixture to provide a DRF API client instance."""
    return APIClient()

@pytest.fixture
def user_data():
    """Fixture to provide sample user data."""

    return {
        "email": "alex@example.com",
        "username": "alexjohnson",
        "password": "strong_password_123",
        "bio": "Quiz enthusiast"
    }

@pytest.fixture
def active_user(db, user_data):
    """Fixture to create and return an active user."""

    return User.objects.create_user(**user_data)

@pytest.fixture
def sample_achievement(db):
    """Fixture to create and return a sample achievement."""

    return Achievement.objects.create(
        name="Quiz Master",
        description="Complete 100 quizzes",
        badge_type="rare"
    )