from rest_framework import serializers
from .models import User, Profile, Achievement, UserAchievement

class AchievementSerializer(serializers.ModelSerializer):
    """For representing Achievement details"""

    class Meta:
        model = Achievement
        fields = ['id', 'name', 'description', 'badge_type', 'icon']


class UserAchievementSerializer(serializers.ModelSerializer):
    """For representing User's earned achievements"""
    
    # Nested Achievement details
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = ['achievement', 'earned_at']


class ProfileSerializer(serializers.ModelSerializer):
    """ Serializer for Profile model including game statistics """

    # Format time played for better readability (e.g., "2h 30m")
    time_played_display = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'level', 'quizzes_taken', 'total_score', 'win_rate', 
            'current_streak', 'highest_streak', 'completion_rate', 
            'time_played', 'time_played_display', 'best_category', 'weakest_category'
        ]

    def get_time_played_display(self, obj):
        """Format time played into hours and minutes."""

        if obj.time_played:
            hours, remainder = divmod(obj.time_played.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{int(hours)}h {int(minutes)}m"
        return "0h 0m"


class UserProfileSerializer(serializers.ModelSerializer):
    """ Serializer for User model including profile and achievements """
    
    profile = ProfileSerializer(read_only=True)
    # For listing user's earned achievements
    earned_achievements = UserAchievementSerializer(source='achievements', many=True, read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'avatar', 'is_verified', 
            'bio', 'date_joined', 'profile', 'earned_achievements'
        ]