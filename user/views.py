import json
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import exceptions

from user.utils import decrypt_string, send_password_reset_email
from user.models import User
from .serializers import UserSerializer, ChangePasswordSerializer
from .filters import UserFilter
from user import serializers
from cryptography.fernet import InvalidToken


User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    http_method_names = ("get", "put", "patch", "head", "options", "trace")
    filterset_class = UserFilter

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

class GetUserProfile(APIView):
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

class ActivateEmail(APIView):
    permission_classes = (AllowAny,)
    def get(self, request,token, *args, **kwargs):
        user_id = decrypt_string(token,settings.INVITES_KEY)['id']
        user = User.objects.get(id=user_id)
        user.status = User.UserStatusChoice.ACTIVE
        user.save()
        return Response({"data": "Success"})

class SendPasswordResetEmail(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "Email not valid."}, status=404)
        send_password_reset_email(user)
        return Response({"message": "Reset Password Email Sent"})

class VerifyResetPasswordEmail(APIView):
    permission_classes = (AllowAny,)
    def post(self, request,token, *args, **kwargs):
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")
        try:
            user_email = decrypt_string(token,settings.INVITES_KEY)['email']
        except InvalidToken:
            return Response({"message": "Invalid Token"}, status=404)
        if new_password ==None or confirm_password == None:
            return Response({"message": "Invalid Password"}, status=404)
        if new_password != confirm_password:
            raise exceptions.AuthenticationFailed("Password not matched")

        user = User.objects.get(email=user_email)
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password reset successful."})

class ChangePassword(APIView):
    
    def post(self, request, *args, **kwargs):
        password = request.data.get("password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")
        if new_password != confirm_password:
            raise exceptions.AuthenticationFailed("Password not matched")
        user = request.user
        if not user.check_password(password):
            raise exceptions.AuthenticationFailed("Wrong Password")
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully"})
