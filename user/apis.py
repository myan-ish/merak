from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

from user.models import Organization, Team

from user.serializer import (
    OrganizationRegistrationSerializer,
    RegistrationSerializer,
    AuthSerializer,
    TeamRegistrationSerializer,
)
from user import serializer
from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField

User = get_user_model()


class RegistrationView(generics.CreateAPIView):
    model = User
    serializer_class = RegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            return Response(
                {"access_token": str(RefreshToken.for_user(user).access_token)},
                status=201,
            )


class InviteFromUUID(APIView):
    def post(self, request, *args, **kwargs):
        uuid = request.data.get("uuid")
        user = request.user

        team = Team.objects.filter(uuid=uuid)
        if team.exists():
            team = team.first()
            user.team = team
            user.organization = team.organization
        else:
            organization = Organization.objects.filter(uuid=uuid)
            if organization.exists():
                print("here")
                user.organization = organization.first()
            else:
                return Response({"message": "UUID not valid"}, status=404)

        user.save()
        return Response({"message": "Success"}, status=201)
