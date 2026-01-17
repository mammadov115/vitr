from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    """
    Form for creating a new user with email instead of username 
    and password confirmation.
    """
    password_confirm = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        help_text="Enter the same password as above, for verification.",
    )

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_password_confirm(self):
        """Check that the two password fields match."""
        p1 = self.cleaned_data.get("password")
        p2 = self.cleaned_data.get("password_confirm")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match")
        return p2

    def save(self, commit=True):
        """Save the user with the correctly hashed password."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    """
    Form for updating existing users.
    """
    class Meta:
        model = User
        fields = ("username", "email", "avatar", "bio", "is_verified")
