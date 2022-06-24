from datetime import date, time, datetime
from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from rest_framework.views import APIView

from user.models import Attendance, Organization, Team
from user.permissions import UserIsOwner

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


class PunchInView(APIView):
    def get(self, request):
        user = request.user
        attendance_object = Attendance.objects.create(user=user, date=date.today())
        attendance_object.punch_in_time = datetime.now().strftime("%H:%M:%S")
        attendance_object.save()

        return Response({"message": "Success"}, status=201)


class PunchOutView(APIView):
    def get(self, request):
        user = request.user
        attendance_object = Attendance.objects.filter(
            user=user, date=date.today()
        ).last()
        attendance_object.punch_in_time = datetime.now().strftime("%H:%M:%S")
        attendance_object.save()
        return Response({"message": "Success"}, status=201)


class AttendanceViewSet(viewsets.ModelViewSet):
    model = Attendance
    serializer_class = serializer.AttendanceSerializer
    permission_classes = (UserIsOwner,)
    queryset = Attendance.objects.all()

    def get_queryset(self):
        tema_members = Organization.objects.get(owner=self.request.user).user_set.all()
        return Attendance.objects.filter(user__in=tema_members)

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user")
        if not user_id:
            return Response({"message": "User id is required"}, status=400)

        queryset = self.filter_queryset(self.get_queryset().filter(user__id=user_id))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
