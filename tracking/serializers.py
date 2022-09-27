from rest_framework import serializers

from .models import TravelHistory, Coordinate

class CoordinateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinate
        fields = '__all__'

class TravelHistorySerializer(serializers.ModelSerializer):
    logged_coordinates = CoordinateSerializer(many=True, read_only=True)
    class Meta:
        model = TravelHistory
        fields = "__all__"
    