from rest_framework.permissions import BasePermission

from user.models import Organization


class UserEmailVerified(BasePermission):
    message = (
        "You need to verify your email address before you can access this resource."
    )

    def has_permission(self, request, view):
        return request.user.status == "Active"


class UserIsOwner(BasePermission):
    message = "You need to be the owner of an organization to access this resource."

    def has_permission(self, request, view):
        list_of_owners = Organization.objects.values_list("owner__id", flat=True)
        if request.user.id in list_of_owners:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.user.organization.owner.id
