from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin, TabularInline
from .models import User, Profile, Achievement, UserAchievement

class ProfileInline(TabularInline):
    model = Profile
    can_delete = False

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """
    Simplified UserAdmin using Unfold.
    """
    inlines = (ProfileInline,)
    list_display = ("username", "email", "is_staff", "is_verified")
    
    # Keeping minimal fieldsets to avoid potential crashes with custom fields
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Extra Info", {"fields": ("avatar", "is_verified", "bio")}),
    )

    # Adding email to the "Add User" form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {"fields": ("email",)}),
    )

    readonly_fields = ("date_joined", "last_login")

@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = ("user", "level", "quizzes_taken", "total_score")

@admin.register(Achievement)
class AchievementAdmin(ModelAdmin):
    list_display = ("name", "badge_type")

@admin.register(UserAchievement)
class UserAchievementAdmin(ModelAdmin):
    list_display = ("user", "achievement", "earned_at")