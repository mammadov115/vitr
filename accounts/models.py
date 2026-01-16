from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier for authentication instead of usernames."""
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "ADMIN")
        return self.create_user(email, password, **extra_fields)
    

class User(AbstractUser):
    """Custom User model extending AbstractUser with additional fields."""
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    bio = models.TextField(max_length=500, blank=True)
    
    
    date_joined = models.DateTimeField(auto_now_add=True) 

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username
    

class Profile(models.Model):
    """Profile model to store additional user information and game statistics."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    level = models.PositiveIntegerField(default=1)
    
    # Game Statistics
    quizzes_taken = models.PositiveIntegerField(default=0)
    total_score = models.FloatField(default=0.0)
    win_rate = models.FloatField(default=0.0)
    current_streak = models.PositiveIntegerField(default=0)
    highest_streak = models.PositiveIntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)
    time_played = models.DurationField(null=True, blank=True)

    # Category Analytics
    best_category = models.CharField(max_length=100, blank=True)
    weakest_category = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Stats for {self.user.username}"
    

class Achievement(models.Model):
    """Model to represent achievements in the game."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    badge_type = models.CharField(max_length=20) # rare, epic, uncommon
    icon = models.ImageField(upload_to='badges/')

class UserAchievement(models.Model):
    """Model to link users with their earned achievements."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)