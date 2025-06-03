from rest_framework import permissions

class IsContributorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow record contributors to edit them.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the record contributor
        # or admin users
        return obj.contributor == request.user or request.user.is_staff