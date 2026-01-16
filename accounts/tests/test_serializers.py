import pytest
from accounts.serializers import UserProfileSerializer
from accounts.models import Profile, UserAchievement

@pytest.mark.django_db
class TestUserProfileSerializer:
    """For testing UserProfileSerializer functionality"""

    def test_serializer_output_structure(self, active_user, sample_achievement):
        # 1. This is the setup phase: Create necessary related objects
        profile, _ = Profile.objects.get_or_create(user=active_user, level=10)
        UserAchievement.objects.create(user=active_user, achievement=sample_achievement)

        # 2. Execution: Serialize the user instance
        serializer = UserProfileSerializer(instance=active_user)
        data = serializer.data

        # 3. Verification: Check the serialized data structure and content
        assert data['username'] == active_user.username
        assert data['email'] == active_user.email
        assert data['profile']['level'] == 10
        
        # Check earned achievements
        assert len(data['earned_achievements']) == 1
        assert data['earned_achievements'][0]['achievement']['name'] == sample_achievement.name

    def test_time_played_display_logic(self, active_user):
        """Test the time_played_display field formatting in ProfileSerializer. (e.g., "2h 30m")"""
        from datetime import timedelta
        profile, _ = Profile.objects.get_or_create(
            user=active_user, 
            time_played=timedelta(hours=2, minutes=30)
        )
        
        serializer = UserProfileSerializer(instance=active_user)
        # Verify the formatted time played display
        assert serializer.data['profile']['time_played_display'] == "2h 30m"