import pytest
from activities.models import Activity
from accounts.models import User

@pytest.mark.django_db
class TestActivityModel:
    def test_activity_creation(self):
        """Test that an activity can be created with correct data."""
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        activity = Activity.objects.create(
            user=user,
            activity_type=Activity.ActivityType.QUIZ_COMPLETED,
            description="Completed a quiz about Python"
        )
        
        assert Activity.objects.count() == 1
        assert activity.user == user
        assert activity.activity_type == Activity.ActivityType.QUIZ_COMPLETED
        assert activity.get_activity_type_display() == "Quiz Completed"
        assert activity.description == "Completed a quiz about Python"
        assert activity.created_at is not None

    def test_activity_ordering(self):
        """Test that activities are ordered by created_at descending."""
        user = User.objects.create_user(
            email="test2@example.com",
            username="testuser2",
            password="testpassword123"
        )
        a1 = Activity.objects.create(
            user=user,
            activity_type=Activity.ActivityType.LEVEL_UP,
            description="First activity"
        )
        a2 = Activity.objects.create(
            user=user,
            activity_type=Activity.ActivityType.ACHIEVEMENT_EARNED,
            description="Second activity"
        )
        
        activities = Activity.objects.all()
        # Due to Meta: ordering = ['-created_at'], newest should be first
        assert activities.first() == a2
        assert activities.last() == a1

    def test_activity_type_choices(self):
        """Test that the activity type choices are correctly defined."""
        assert Activity.ActivityType.QUIZ_COMPLETED == "QUIZ_COMPLETED"
        assert Activity.ActivityType.ACHIEVEMENT_EARNED == "ACHIEVEMENT_EARNED"
        assert Activity.ActivityType.LEVEL_UP == "LEVEL_UP"
        
        # Verify human-readable labels
        choices = dict(Activity.ActivityType.choices)
        assert choices["QUIZ_COMPLETED"] == "Quiz Completed"
        assert choices["ACHIEVEMENT_EARNED"] == "Achievement Earned"
        assert choices["LEVEL_UP"] == "Level Up"

    def test_cascade_delete(self):
        """Test that activities are deleted when the user is deleted."""
        user = User.objects.create_user(
            email="test3@example.com",
            username="testuser3",
            password="testpassword123"
        )
        Activity.objects.create(
            user=user,
            activity_type=Activity.ActivityType.LEVEL_UP,
            description="Test activity"
        )
        
        assert Activity.objects.count() == 1
        user.delete()
        assert Activity.objects.count() == 0

