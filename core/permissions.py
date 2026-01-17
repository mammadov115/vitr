from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to anyone, but restrict write access to admins only.
    Useful for Categories, Quizzes, etc.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsOwnerOnly(permissions.BasePermission):
    """
    Private permission: Only the owner of the object can access it.
    Useful for TakenQuizzes, User Profiles, etc.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the object itself is the user OR if it has a 'user' attribute
        return obj == request.user or (hasattr(obj, 'user') and obj.user == request.user)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to anyone, but restrict write access to the owner.
    Useful for User Profiles, Comments, etc.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user or (hasattr(obj, 'user') and obj.user == request.user)
