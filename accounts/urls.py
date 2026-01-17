from django.urls import path
from rest_framework_simplejwt.views import  TokenRefreshView
from accounts.views import (CustomTokenObtainPairView,
                             RegisterView,
                               MyProfileView,
                                 PublicProfileView,
                                   AchievementListView)

urlpatterns = [
    # Auth
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # My profile
    path('me/', MyProfileView.as_view(), name='my-profile'),
    
    # Public profile
    path('profile/<str:username>/', PublicProfileView.as_view(), name='public-profile'),
    
    # Achievements
    path('achievements/', AchievementListView.as_view(), name='achievement-list'),
]