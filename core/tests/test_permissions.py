import pytest
from unittest.mock import Mock
from core.permissions import IsAdminOrReadOnly, IsOwnerOnly, IsOwnerOrReadOnly
from rest_framework import permissions

class MockUser:
    def __init__(self, is_staff=False):
        self.is_staff = is_staff

class MockObject:
    def __init__(self, user=None):
        self.user = user

class TestCorePermissions:

    # --- IsAdminOrReadOnly Tests ---
    def test_is_admin_or_read_only_safe_methods(self):
        perm = IsAdminOrReadOnly()
        for method in permissions.SAFE_METHODS: # GET, HEAD, OPTIONS
            request = Mock(method=method)
            assert perm.has_permission(request, None) is True

    def test_is_admin_or_read_only_post_admin(self):
        perm = IsAdminOrReadOnly()
        request = Mock(method='POST', user=MockUser(is_staff=True))
        assert perm.has_permission(request, None) is True

    def test_is_admin_or_read_only_post_regular_user(self):
        perm = IsAdminOrReadOnly()
        request = Mock(method='POST', user=MockUser(is_staff=False))
        assert perm.has_permission(request, None) is False

    # --- IsOwnerOnly Tests ---
    def test_is_owner_only_success(self):
        perm = IsOwnerOnly()
        user = MockUser()
        obj = MockObject(user=user)
        request = Mock(user=user)
        assert perm.has_object_permission(request, None, obj) is True

    def test_is_owner_only_failure(self):
        perm = IsOwnerOnly()
        user1 = MockUser()
        user2 = MockUser()
        obj = MockObject(user=user1)
        request = Mock(user=user2)
        assert perm.has_object_permission(request, None, obj) is False

    # --- IsOwnerOrReadOnly Tests ---
    def test_is_owner_or_read_only_safe_methods(self):
        perm = IsOwnerOrReadOnly()
        for method in permissions.SAFE_METHODS:
            request = Mock(method=method)
            assert perm.has_object_permission(request, None, Mock()) is True

    def test_is_owner_or_read_only_put_owner(self):
        perm = IsOwnerOrReadOnly()
        user = MockUser()
        obj = MockObject(user=user)
        request = Mock(method='PUT', user=user)
        assert perm.has_object_permission(request, None, obj) is True

    def test_is_owner_or_read_only_put_not_owner(self):
        perm = IsOwnerOrReadOnly()
        user1 = MockUser()
        user2 = MockUser()
        obj = MockObject(user=user1)
        request = Mock(method='PUT', user=user2)
        assert perm.has_object_permission(request, None, obj) is False
