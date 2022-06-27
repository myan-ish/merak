import json
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField
from rest_framework import exceptions
from user.permissions import UserIsOwner

from user.utils import decrypt_string, send_password_reset_email
from user.models import Customer, Organization, Team, User
from user.serializer import (
    CustomerSerializer,
    OrganizationRegistrationSerializer,
    TeamRegistrationSerializer,
    UserSerializer,
    ChangePasswordSerializer,
)
from .filters import UserFilter
from cryptography.fernet import InvalidToken

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    http_method_names = ("get", "put", "patch", "head", "options", "trace")
    filterset_class = UserFilter

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization)

    def get_serializer_class(self):
        if self.action == "change_password":
            return ChangePasswordSerializer
        return self.serializer_class

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        data = json.loads(request.data.get("data", b"{}"))

        if request.FILES.get("avatar") is not None:
            data["avatar"] = request.FILES["avatar"]
        instance = request.user
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

    def get(self, request, token, *args, **kwargs):
        user_id = decrypt_string(token, settings.INVITES_KEY)["id"]
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

    def post(self, request, token, *args, **kwargs):
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")
        try:
            user_email = decrypt_string(token, settings.INVITES_KEY)["email"]
        except InvalidToken:
            return Response({"message": "Invalid Token"}, status=404)
        if new_password == None or confirm_password == None:
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


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationRegistrationSerializer
    queryset = Organization.objects.all()

    def get_queryset(self):
        try:
            organization = Organization.objects.filter(owner=self.request.user)
            return organization
        except Organization.DoesNotExist:
            return Response({"message": "Organization not found"}, status=404)

    def create(self, request, *args, **kwargs):
        if Organization.objects.filter(owner=request.user).exists():
            return Response(
                {"message": "You cannot create two organizations"}, status=400
            )
        return super().create(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        with transaction.atomic():

            print("here")
            serializer = self.get_serializer(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                serializer.data,
                status=201,
            )


class TeamRegistrationViewSet(viewsets.ModelViewSet):
    class TeamSerializer(ModelSerializer):
        team_leader = SerializerMethodField()
        organization = CharField(source="organization.name")

        class Meta:
            model = Team
            fields = ("id", "name", "organization", "team_leader", "uuid")

        def get_team_leader(self, obj):
            return obj.team_leader.get_full_name()

    serializer_class = TeamSerializer
    performer_class = TeamRegistrationSerializer
    queryset = Team.objects.all()

    def get_queryset(self):
        try:
            organization = Organization.objects.get(owner=self.request.user)
        except Organization.DoesNotExist:
            return Response({"message": "Organization not found"}, status=404)
        teams = Team.objects.filter(organization=organization)
        return teams

    def create(self, request, *args, **kwargs):
        self.serializer_class = self.performer_class
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.serializer_class = self.performer_class
        return super().update(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.get_serializer(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            team = serializer.save()

            return Response(
                self.TeamSerializer(team).data,
                status=201,
            )
