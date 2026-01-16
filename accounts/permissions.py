from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission: Only owners can edit their own profile; others have read-only access.
    """
    def has_object_permission(self, request, view, obj):
        # GET, HEAD or OPTIONS allow read-only access
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the profile
        # If obj is a Profile instance, check obj.user
        # If obj is a User instance, check obj == request.user
        return obj == request.user or (hasattr(obj, 'user') and obj.user == request.user)