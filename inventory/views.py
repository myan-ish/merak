import base64
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Q
from inventory.filters import OrderFilter, VariantFilter
from inventory.models import (
    Order,
    OrderItem,
    Product,
    Variant,
    VariantFieldName,
    VarientField,
)

from drf_yasg.utils import swagger_auto_schema
from inventory.serializers.order import OrderInSerializer, OrderOutSerializer

from user.models import Customer

user_model = get_user_model()

class OrderView(ModelViewSet):
    
    queryset = Order.objects.all()
    serializer_class = OrderOutSerializer
    perfomer_serializer_class = OrderInSerializer
    lookup_field = "uuid"
    permission_classes = (IsAuthenticated,)
    filterset_class = OrderFilter

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(organization=self.request.user.organization)
            .order_by("-ordered_date")
        )

    @swagger_auto_schema(
        request_body=perfomer_serializer_class,
        responses={201: serializer_class},
    )
    def create(self, request, *args, **kwargs):
        field = request.data.get("field")
        serializer = self.perfomer_serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(self.serializer_class(order).data, status=201)

    @swagger_auto_schema(
        request_body=perfomer_serializer_class,
        responses={201: serializer_class},
    )
    def update(self, request, *args, **kwargs):
        serializer = self.perfomer_serializer_class(
            self.get_object(), data=request.data
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(self.serializer_class(order).data, status=201)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(serializer.data)



# TODO: Change the following apis to change it to same funciton
#       Each api will check which funciton to call based on the request method



class AcceptOrderView(APIView):

    lookup_url = "uuid"
    permission_classes = (IsAuthenticated,)

    def get(self, request, uuid):
        order = Order.objects.filter(
            Q(assigned_to=None) | Q(assigned_to=request.user),
            uuid=uuid,
            status="PENDING",
            owned_by__in=[request.user.admin, request.user],
        )

        if not order:
            return Response(data={"detail": "Order doesn't exists."}, status=404)
        order = order.first()
        order.status = "ACCEPTED"
        if order.assigned_to is None:
            order.assigned_to = request.user
        order.save()
        return Response(OrderOutSerializer(order).data)


class DeclineAssignedOrderView(APIView):
    lookup_url = "uuid"
    permission_classes = (IsAuthenticated,)

    def get(self, request, uuid):
        try:
            order = Order.objects.get(
                uuid=uuid,
                assigned_to__in=[request.user, None],
                status="PENDING",
                owned_by__in=[request.user.admin, request.user],
            )
        except Order.DoesNotExist:
            return Response(data={"detail": "Order doesn't exists."}, status=404)

        order.assigned_to = None
        order.save()
        return Response(OrderOutSerializer(order).data)


class GetUserPendingOrderView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            orders = Order.objects.filter(
                assigned_to=request.user,
                status="PENDING",
                owned_by__in=[request.user.admin, request.user],
            )
        except Order.DoesNotExist:
            return Response(data={"detail": "Order doesn't exists."}, status=404)

        return Response(OrderOutSerializer(orders, many=True).data)


class GetUserAcceptedOrderView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            orders = Order.objects.filter(
                assigned_to=request.user,
                status="ACCEPTED",
                owned_by__in=[request.user.admin, request.user],
            )
        except Order.DoesNotExist:
            return Response(data={"detail": "Order doesn't exists."}, status=404)

        return Response(OrderOutSerializer(orders, many=True).data)


class DeclineAcceptedOrderView(APIView):
    lookup_url = "uuid"
    permission_classes = (IsAuthenticated,)

    def get(self, request, uuid):
        try:
            order = Order.objects.get(
                uuid=uuid,
                assigned_to=request.user,
                status="ACCEPTED",
                owned_by=request.user.admin or request.user,
            )
        except Order.DoesNotExist:
            return Response(data={"detail": "Order doesn't exists."}, status=404)

        order.assigned_to = None
        order.status = "PENDING"
        order.save()
        return Response(OrderOutSerializer(order).data)
