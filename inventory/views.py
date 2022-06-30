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

from user.models import Customer

user_model = get_user_model()


class FieldSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(write_only=True)
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VarientField
        fields = "__all__"

    def create(self, validated_data):
        variant_field_name = VariantFieldName.objects.get_or_create(
            name=validated_data.pop("field_name")
        )[0]
        validated_data["name"] = variant_field_name

        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        validated_data["organization"] = user.organization if user else None

        return super().create(validated_data)

    def get_name(self, obj):
        return obj.name.name


class VariantFieldView(ModelViewSet):
    serializer_class = FieldSerializer
    queryset = VarientField.objects.all()

    def get_queryset(self):
        return (
            super().get_queryset().filter(organization=self.request.user.organization)
        )


class VariantView(ModelViewSet):
    class VariantInSerializer(WritableNestedModelSerializer):
        field = serializers.ListField()
        price = serializers.IntegerField()
        image = serializers.ImageField(required=False)
        # image = serializers.CharField(required=False)
        product = serializers.PrimaryKeyRelatedField(
            queryset=Product.objects.all(),
        )
        is_default = serializers.BooleanField(required=False)

        class Meta:
            model = Variant
            fields = "__all__"

        def create(self, validated_data):
            field = validated_data.pop("field")
            user = None
            request = self.context.get("request")
            if request and hasattr(request, "user"):
                user = request.user
            variant = Variant.objects.create(
                **validated_data, organization=user.organization
            )
            variant.set_sku()
            field_obj = [VarientField.objects.get(id=field_id) for field_id in field]
            variant.field.set(field_obj)
            variant.save()
            return variant

    class VairantOutSerializer(serializers.ModelSerializer):
        field = FieldSerializer(many=True)

        class Meta:
            model = Variant
            fields = "__all__"

    queryset = Variant.objects.all()
    serializer_class = VairantOutSerializer
    performer_serializer_class = VariantInSerializer
    filterset_class = VariantFilter
    lookup_field = "sku"

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
    class ProductInSerializer(serializers.ModelSerializer):
        name = serializers.CharField(max_length=255)
        description = serializers.CharField(max_length=255, required=False)
        owned_by = serializers.PrimaryKeyRelatedField(
            queryset=user_model.objects.all(), required=False
        )

        class Meta:
            model = Product
            fields = "__all__"

        def create(self, validated_data):
            user = None
            request = self.context.get("request")
            if request and hasattr(request, "user"):
                user = request.user
            product = Product.objects.create(
                owned_by=user, organization=user.organization, **validated_data
            )
            product.save()
            return product

    class ProductOutSerializer(serializers.ModelSerializer):
        class Meta:
            model = Product
            fields = (
                "uuid",
                "name",
                "description",
                "default_image",
                "default_price",
                "id",
            )

    queryset = Product.objects.all()
    serializer_class = ProductOutSerializer
    performer_serializer_class = ProductInSerializer
    lookup_field = "uuid"

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


class VariantSerializer(serializers.Serializer):
    product = serializers.CharField()
    quantity = serializers.IntegerField()


class ItemsRetriveSerializer(serializers.Serializer):
    product = VariantView.VairantOutSerializer()
    quantity = serializers.IntegerField()
    line_total = serializers.SerializerMethodField()

    def get_line_total(self, obj):
        return obj.product.price * obj.quantity


class UserOutSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = user_model
        fields = ("pk", "email", "address", "phone", "full_name")

    def get_full_name(self, obj):
        return obj.get_full_name()


class CustomerOutSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = "__all__"

    def get_full_name(self, obj):
        return obj.get_full_name()


class OrderView(ModelViewSet):
    class OrderInSerializer(serializers.Serializer):
        items = serializers.ListField(child=VariantSerializer())

        ordered_by = serializers.IntegerField()
        assigned_to = serializers.IntegerField(required=False)

        def create(self, validated_data):
            order_item_list = []
            for item in validated_data.pop("items"):
                try:
                    product = Variant.objects.get(
                        sku=item["product"],
                        organization=self.context["request"].user.organization,
                    )
                except Variant.DoesNotExist:
                    raise serializers.ValidationError(
                        "Product with sku {} does not exist".format(item["product"])
                    )

                if product.quantity < item["quantity"]:
                    raise serializers.ValidationError(
                        "Not enough quantity for product {}".format(
                            product.product.name
                        )
                    )
                product.quantity -= item["quantity"]
                product.save()

                order_item = OrderItem.objects.create(
                    product=product,
                    quantity=item["quantity"],
                    organization=product.organization,
                )

                order_item_list.append(order_item)
            try:
                ordered_by = Customer.objects.get(
                    id=validated_data.pop("ordered_by"),
                    organization=self.context["request"].user.organization,
                )
            except user_model.DoesNotExist:
                raise serializers.ValidationError("User does not exist")
            try:
                assigned_to = user_model.objects.get(
                    id=validated_data.pop("assigned_to"),
                    organization=ordered_by.organization,
                )
            except KeyError:
                assigned_to = None
            except user_model.DoesNotExist:
                raise serializers.ValidationError("User does not exist")
            order = Order.objects.create(
                owned_by=self.context["request"].user,
                organization=self.context["request"].user.organization,
                ordered_by=ordered_by,
                assigned_to=assigned_to,
                **validated_data
            )
            order.items.set(order_item_list)
            return order

        def update(self, instance, validated_data):
            order_item_list = []
            try:
                for item in validated_data.pop("items"):
                    product = Variant.objects.get(id=item["product"])
                    product.quantity -= item["quantity"]
                    product.save()
                    order_item = OrderItem.objects.create(
                        product=product, quantity=item["quantity"]
                    )

                    order_item_list.append(order_item)

                for previous_item in instance.items.all():
                    previous_item.product.quantity += previous_item.quantity
                    previous_item.product.save()

                instance.items.all().delete()
                instance.items.set(order_item_list)
            except KeyError:
                pass

            instance.__dict__.update(validated_data)
            instance.save()
            return instance

    class OrderOutSerializer(serializers.ModelSerializer):
        ordered_by = UserOutSerializer(read_only=True)
        assigned_to = UserOutSerializer(read_only=True)
        items = ItemsRetriveSerializer(many=True)
        invoice = serializers.CharField(source="uuid")
        sub_total = serializers.SerializerMethodField()
        total = serializers.SerializerMethodField()

        # Need refactoring--------------------------------------------------
        def get_sub_total(self, obj):
            sub_total = 0
            for item in obj.items.all():
                sub_total += item.product.price * item.quantity
            return float(sub_total)

        # Need refactoring--------------------------------------------------
        def get_total(self, obj):
            tax = 1.13
            return self.get_sub_total(obj) * tax

        class Meta:
            model = Order
            fields = (
                "ordered_by",
                "assigned_to",
                "status",
                "items",
                "invoice",
                "ordered_date",
                "completed_date",
                "sub_total",
                "total",
            )

    queryset = Order.objects.all()
    serializer_class = OrderOutSerializer
    perfomer_serializer_class = OrderInSerializer
    lookup_field = "uuid"
    permission_classes = (IsAuthenticated,)
    filterset_class = OrderFilter

    def get_queryset(self):
        return (
            super().get_queryset().filter(organization=self.request.user.organization)
        )

    @swagger_auto_schema(
        request_body=perfomer_serializer_class,
        responses={201: serializer_class},
    )
    def create(self, request, *args, **kwargs):
        field = request.data.get("field")
        print(field)
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
        return Response(OrderView.OrderOutSerializer(order).data)


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
        return Response(OrderView.OrderOutSerializer(order).data)


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

        return Response(OrderView.OrderOutSerializer(orders, many=True).data)


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

        return Response(OrderView.OrderOutSerializer(orders, many=True).data)


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
        return Response(OrderView.OrderOutSerializer(order).data)
