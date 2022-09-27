from http.client import HTTPResponse
import re
from urllib import request
from django.shortcuts import render
from rest_framework.response import Response

from tracking.models import Coordinate, TravelHistory
from tracking.serializers import TravelHistorySerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

# def log_coordinates(request):
#     if request.method == "POST":
#         latitude = request.POST.get("latitude")
#         longitude = request.POST.get("longitude")
#         coordinate = Coordinate.objects.create(latitude=latitude, longitude=longitude)
#         temporary_user = TravelHistory.objects.get(id=1)
#         travel_history = TravelHistory.objects.get_or_create(user=temporary_user)[0]
#         travel_history.logged_coordinates.add(coordinate)
#         travel_history.save()
#         return Response({"message": "Coordinates logged successfully"})
#     if request.method == "GET":
#         travel_history = TravelHistorySerializer(TravelHistory.objects.filter(user__id=1), many=True)
#         return Response({"travel_history": travel_history})

class log_coordinates(APIView):
    serializer_class = TravelHistorySerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        travel_history = TravelHistory.objects.filter(user__id=1)
        serializer = TravelHistorySerializer(travel_history, many=True)
        return Response({"travel_history": serializer.data})