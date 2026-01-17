from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from .models import User, Profile, Achievement, UserAchievement

# For Unfold admin customization
from unfold.admin import TabularInline

class ProfileInline(TabularInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile Statistics'

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """
    Custom User admin using Unfold's design.
    """
    inlines = (ProfileInline,)
    list_display = ("username", "email", "is_staff", "is_verified")
    list_filter = ("is_staff", "is_superuser", "is_active", "is_verified")
    
    # Customize the fieldsets to include additional fields
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("email", "avatar", "bio")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "is_verified", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

@admin.register(Achievement)
class AchievementAdmin(ModelAdmin):
    """
    Admin for achievements with Unfold features.
    """
    list_display = ("name", "badge_type", "description")
    search_fields = ("name",)
    list_filter = ("badge_type",)

@admin.register(UserAchievement)
class UserAchievementAdmin(ModelAdmin):
    """
    Tracks which user earned which achievement.
    """
    list_display = ("user", "achievement", "earned_at")
    list_filter = ("achievement", "earned_at")
    date_hierarchy = 'earned_at'