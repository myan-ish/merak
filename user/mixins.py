

class RetrievePermissionMixin:
    """Uses to allow retrieve object even
    in case when view_ permission did not get.
     Work only in case, if model has retrieve_ rule,
     and user has retrieve_ permission"""

    def check_permissions(self, request):
        super().check_permissions(request)
        if self.kwargs.get(self.lookup_field):
            return super().check_object_permissions(request, None)