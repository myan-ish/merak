from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated

from inventory.filters import VariantFilter
from inventory.models import (
    Product,
    Variant,
    VarientField,
)
from inventory.serializers.product import FieldSerializer, ProductInSerializer, ProductOutSerializer, VairantOutSerializer, VariantInSerializer
from user.permissions import UserIsOwner, UserIsEditor

from drf_yasg.utils import swagger_auto_schema


user_model = get_user_model()


class VariantFieldView(ModelViewSet):
    serializer_class = FieldSerializer
    queryset = VarientField.objects.all()
    permission_classes = [IsAuthenticated, UserIsOwner, UserIsEditor]

    def get_queryset(self):
        return (
            super().get_queryset().filter(organization=self.request.user.organization)
        )


class VariantView(ModelViewSet):
    queryset = Variant.objects.all()
    serializer_class = VairantOutSerializer
    performer_serializer_class = VariantInSerializer
    filterset_class = VariantFilter
    lookup_field = "sku"
    permission_classes = [UserIsOwner|UserIsEditor]


    def get_queryset(self):
        return (
            super().get_queryset().filter(organization=self.request.user.organization)
        )

    @swagger_auto_schema(
        request_body=performer_serializer_class,
        responses={201: serializer_class},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.performer_serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        variant = serializer.save()
        variant.set_sku()
        return Response(self.serializer_class(variant).data)

    @swagger_auto_schema(
        request_body=performer_serializer_class,
        responses={201: serializer_class},
    )
    def update(self, request, *args, **kwargs):
        variant = self.get_object()
        serializer = self.performer_serializer_class(variant, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.serializer_class(variant).data)


class ProductView(ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductOutSerializer
    performer_serializer_class = ProductInSerializer
    lookup_field = "uuid"
    permission_classes = [UserIsOwner| UserIsEditor]


    def get_queryset(self):
        return (
            super().get_queryset().filter(organization=self.request.user.organization)
        )

    @swagger_auto_schema(
        request_body=performer_serializer_class,
        responses={201: serializer_class},
    )
    def create(self, request, *args, **kwargs):
        """Create a new product,
        The list in the variant field is list of variant pks."""
        serializer = self.performer_serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(self.serializer_class(product).data, status=201)

    @swagger_auto_schema(
        request_body=performer_serializer_class,
        responses={201: serializer_class},
    )
    def update(self, request, *args, **kwargs):
        serializer = self.performer_serializer_class(
            self.get_object(), data=request.data
        )
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(self.serializer_class(product).data, status=201)


