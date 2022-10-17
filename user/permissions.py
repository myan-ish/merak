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
        return request.user.id in list_of_owners

    def has_object_permission(self, request, view, obj):
        try:
            return request.user.id == obj.user.organization.owner.id
        except AttributeError:
            return request.user.organization == obj.organization

class UserIsEditor(BasePermission):
    message = "You need to be the editor of the organization to access this resource."

    def has_permission(self, request, view):
        return request.user.groups.filter(name='Editor').exists()

    def has_object_permission(self, request, view, obj):
        return request.user.organization == obj.organization

class UserIsStaff(BasePermission):
    message = "You need to be a staff member to access this resource."

    def has_permission(self, request, view):
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff and request.user.organization == obj.organization