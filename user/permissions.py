from rest_framework.permissions import BasePermission

class UserEmailVerified(BasePermission):
    message = "You need to verify your email address before you can access this resource."
    def has_permission(self, request, view):
        return request.user.status == 'Active'