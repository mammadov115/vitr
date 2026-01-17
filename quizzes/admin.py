from django.contrib import admin
from unfold.admin import ModelAdmin
from quizzes.models import Category, Quiz, Question, Choice, TakenQuiz
import nested_admin

class ChoiceInline(nested_admin.NestedTabularInline):
    """Nested inline for choices."""
    model = Choice
    extra = 1

class QuestionInline(nested_admin.NestedStackedInline):
    """Nested inline for questions, containing choice inlines."""
    model = Question
    extra = 1
    inlines = [ChoiceInline]

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    """Admin interface for quiz categories."""
    list_display = ("name", "slug", "description")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Quiz)
class QuizAdmin(nested_admin.NestedModelAdmin, ModelAdmin):
    """
    Admin interface for quizzes using nested_admin for hierarchy 
    and Unfold for the premium look.
    """
    list_display = ("title", "category", "difficulty", "time_limit_minutes", "is_active", "created_at")
    list_filter = ("category", "difficulty", "is_active")
    search_fields = ("title", "description")
    list_editable = ("is_active",)
    inlines = [QuestionInline]
    readonly_fields = ("created_at", "updated_at")

    class Media:
        css = {
            "all": ("css/admin_custom.css",)
        }

@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    """Standalone admin for questions if needed."""
    list_display = ("text", "quiz", "order")
    list_filter = ("quiz", "quiz__category")
    search_fields = ("text",)
    inlines = [ChoiceInline]
    ordering = ("quiz", "order")

@admin.register(Choice)
class ChoiceAdmin(ModelAdmin):
    """Standalone admin for choices."""
    list_display = ("text", "question", "is_correct")
    list_filter = ("is_correct", "question__quiz")
    search_fields = ("text",)

@admin.register(TakenQuiz)
class TakenQuizAdmin(ModelAdmin):
    """Admin for tracking user attempts."""
    list_display = ("user", "quiz", "score", "correct_answers", "total_questions", "completed_at", "duration")
    list_filter = ("quiz", "user", "completed_at")
    search_fields = ("user__username", "user__email", "quiz__title")
    readonly_fields = ("completed_at",)
    date_hierarchy = "completed_at"
