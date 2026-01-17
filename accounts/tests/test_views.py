import pytest
from django.urls import reverse
from rest_framework import status
from accounts.models import Achievement
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestAuthenticationViews:

    def test_user_registration_success(self, api_client):
        """Test that a user can successfully register with valid data."""
        url = reverse('register', kwargs={'version': 'v1'})
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!"
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == "User registered successfully."
        assert User.objects.filter(email="newuser@example.com").exists()

    def test_user_registration_password_mismatch(self, api_client):
        """Test that registration fails if passwords do not match."""
        url = reverse('register', kwargs={'version': 'v1'})
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123!",
            "password_confirm": "DifferentPassword123!"
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # The key might be 'password' or 'non_field_errors' depending on your serializer
        assert "password" in response.data

    def test_user_login_success(self, api_client, active_user):
        """Test that a user can login and receive JWT tokens."""
        url = reverse('login', kwargs={'version': 'v1'})
        # Since we use email as USERNAME_FIELD
        data = {
            "email": active_user.email,
            "password": "strong_password_123"
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_user_login_invalid_credentials(self, api_client, active_user):
        """Test that login fails with an incorrect password."""
        url = reverse('login', kwargs={'version': 'v1'})
        data = {
            "email": active_user.email,
            "password": "wrongpassword"
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh(self, api_client, active_user):
        """Test obtaining a new access token using a refresh token."""
        # 1. Get initial tokens
        login_url = reverse('login', kwargs={'version': 'v1'})
        login_data = {"email": active_user.email, "password": "strong_password_123"}
        login_response = api_client.post(login_url, login_data)
        refresh_token = login_response.data['refresh']

        # 2. Use refresh token to get new access token
        refresh_url = reverse('token_refresh', kwargs={'version': 'v1'})
        response = api_client.post(refresh_url, {"refresh": refresh_token})

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

@pytest.mark.django_db
class TestAccountViews:

    def test_get_my_profile_authenticated(self, api_client, active_user):
        """Test that an authenticated user can retrieve their own profile."""
        url = reverse('my-profile', kwargs={'version': 'v1'})
        api_client.force_authenticate(user=active_user)
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == active_user.username
        assert response.data['email'] == active_user.email
        # Ensure nested profile data is present
        assert 'profile' in response.data

    def test_get_my_profile_unauthenticated(self, api_client):
        """Test that an unauthenticated user cannot access the /me/ endpoint."""
        url = reverse('my-profile', kwargs={'version': 'v1'})
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_my_profile_patch(self, api_client, active_user):
        """Test that a user can partially update their bio via PATCH."""
        url = reverse('my-profile', kwargs={'version': 'v1'})
        api_client.force_authenticate(user=active_user)
        
        payload = {"bio": "New bio description"}
        response = api_client.patch(url, payload)
        
        assert response.status_code == status.HTTP_200_OK
        active_user.refresh_from_db()
        assert active_user.bio == "New bio description"

    def test_update_my_profile_put_not_allowed(self, api_client, active_user):
        """Test that PUT method returns 405 Method Not Allowed as per our view logic."""
        url = reverse('my-profile', kwargs={'version': 'v1'})
        api_client.force_authenticate(user=active_user)
        
        payload = {"username": "newname", "email": "new@test.com"}
        response = api_client.put(url, payload)
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_view_public_profile(self, api_client, active_user):
        """Test retrieving a public profile by username."""
        # Create a second user to view their profile
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other_user = User.objects.create_user(username="otheruser", email="other@test.com", password="password123")
        
        url = reverse('public-profile', kwargs={'username': other_user.username, 'version': 'v1'})
        
        # Public profiles should be accessible even without login (IsAuthenticatedOrReadOnly)
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == "otheruser"

    def test_list_achievements(self, api_client):
        """Test that anyone can list all available achievements."""
        Achievement.objects.create(name="First Win", description="Win one quiz", badge_type="uncommon")
        
        url = reverse('achievement-list', kwargs={'version': 'v1'})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]['name'] == "First Win"

