import json
from django.contrib.auth import get_user_model

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from .serializers import UserSerializer, ChangePasswordSerializer
from .filters import UserFilter


User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    http_method_names = ("get", "put", "patch", "head", "options", "trace")
    filterset_class = UserFilter

    def get_queryset(self):
        user = self.request.user
        filter_params = {}

        if not user.is_superuser:
            filter_params["is_superuser"] = False
        if not user.is_admin:
            filter_params["is_admin"] = False
        if not user.is_merchant:
            filter_params["is_merchant"] = False

        return User.objects.filter(**filter_params).distinct()

    def get_serializer_class(self):
        if self.action == "change_password":
            return ChangePasswordSerializer
        return self.serializer_class

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        data = json.loads(request.data.get("data", b"{}"))

        if request.FILES.get("avatar") is not None:
            data["avatar"] = request.FILES["avatar"]
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if "avatar" in request.data:
            instance.avatar.delete(save=False)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(methods=["PUT"], detail=True)
    def change_password(self, request, pk):
        user = self.get_object()
        serializer = self.get_serializer_class()(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()
