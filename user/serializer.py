from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.hashers import check_password
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from user.models import Organization, Team

from .validators import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    @staticmethod
    def get_display_name(obj):
        return f"{obj.first_name} {obj.last_name}"

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "status",
            "avatar",
            "gender",
            "birth_date",
            "phone",
            "address",
            "is_staff",
            "display_name",
        )


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "old_password",
            "new_password",
        )

    def validate(self, data: dict) -> dict:
        old_password, new_password = data["old_password"], data["new_password"]

        if not check_password(old_password, self.instance.password):
            raise serializers.ValidationError(
                {"old_password": _("Password isn't correct")}
            )
        try:
            password_validation.validate_password(password=new_password)
        except password_validation.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return data

    def update(self, instance: User, validated_data: dict) -> User:
        instance.set_password(validated_data["new_password"])
        instance.save(update_fields=("password",))
        return instance


class AuthSerializer(serializers.Serializer):
    access_token = serializers.CharField(
        max_length=4096, required=True, trim_whitespace=True
    )


class RegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=64)
    last_name = serializers.CharField(max_length=64)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
        )

    def create(self, validated_data: dict) -> dict:
        user = User.objects.create_user(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
            password=validated_data["password"],
            status=User.UserStatusChoice.PENDING,
        )
        return user


class OrganizationRegistrationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=64)
    description = serializers.CharField(max_length=256)

    class Meta:
        model = Organization
        fields = (
            "name",
            "description",
        )

    def create(self, validated_data: dict) -> dict:
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        organization = Organization.objects.create(
            name=validated_data["name"],
            description=validated_data["description"],
            owner=user,
        )
        return organization


class TeamRegistrationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=64)
    description = serializers.CharField(max_length=256)
    team_leader = serializers.IntegerField(write_only=True)
    organization = serializers.IntegerField(write_only=True)
    members = serializers.ListField(write_only = True)

    class Meta:
        model = Team
        fields = (
            "name",
            "description",
            "team_leader",
            "organization",
            "members",
        )

    def create(self, validated_data: dict) -> dict:

        team = Team.objects.create(
            name=validated_data["name"],
            description=validated_data["description"],
            team_leader=User.objects.get(id=validated_data["team_leader"]),
            organization=Organization.objects.get(id=validated_data["organization"]),
        )

        for member in validated_data["members"]:
            member_obj = User.objects.get(id=member)
            if member_obj.organization != team.organization:
                raise serializers.ValidationError(
                    {"members": _("User is not in the same organization")}
                )
            member_obj.team = team
            member_obj.save()

        return team
