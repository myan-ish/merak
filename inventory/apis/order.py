from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from inventory.models import (
    Order,
)

from drf_yasg.utils import swagger_auto_schema

from inventory.serializers.order import OrderOutSerializer


user_model = get_user_model()


class OrderByActionView(APIView):
    lookup_field = "uuid"
    permission_classes = [IsAuthenticated]

    def get(self, request, uuid, action):
        try:
            order = Order.objects.get(
                uuid=uuid,
                assigned_to__in=[request.user, None],
                status="PENDING",
                owned_by__in=[request.user.admin, request.user],
            )
        except Order.DoesNotExist:
            return Response(data={"detail": "Order doesn't exists."}, status=404)

        if action == "accept":
            order = order.first()
            order.status = "ACCEPTED"
            if order.assigned_to is None:
                order.assigned_to = request.user
            order.save()
            return Response(OrderOutSerializer(order).data)
        elif action == "reject":
            order.assigned_to = None
            order.save()
            return Response(OrderOutSerializer(order).data)
        elif action == "reject_accepted":
            order.assigned_to = None
            order.status = "PENDING"
            order.save()
            return Response(OrderOutSerializer(order).data)
        else:
            return Response(data={"detail": "Invalid action."}, status=400)

class GetOrderByActionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, action):
        if action == "pending":
            order = Order.objects.filter(
                assigned_to__in=[request.user, None],
                status="PENDING",
                owned_by__in=[request.user.admin, request.user],
            )
            return Response(OrderOutSerializer(order, many=True).data)
        elif action == "accepted":
            order = Order.objects.filter(
                assigned_to=request.user,
                status="ACCEPTED",
                owned_by__in=[request.user.admin, request.user],
            )
            return Response(OrderOutSerializer(order, many=True).data)
        else:
            return Response(data={"detail": "Invalid action."}, status=400)
