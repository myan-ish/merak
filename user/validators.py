from django.contrib.auth import password_validation

from rest_framework import serializers


def validate_password(password: str) -> None:
    try:
        password_validation.validate_password(password=password)
    except password_validation.ValidationError as e:
        raise serializers.ValidationError(list(e.messages))
