
from rest_framework import serializers
from django.contrib.auth import get_user_model

from user.models import Customer

user_model = get_user_model()

class UserOutSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = user_model
        fields = ("pk", "email", "address", "phone", "full_name")

    def get_full_name(self, obj):
        return obj.get_full_name()


class CustomerOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"