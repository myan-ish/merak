from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Q
from inventory.filters import VariantFilter
from inventory.models import Order, OrderItem, Product, Variant, VarientField

from drf_yasg.utils import swagger_auto_schema

user_model = get_user_model()


user_model = get_user_model()

class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = VarientField
        fields = '__all__'

class VariantView(ModelViewSet):
    class VariantInSerializer(WritableNestedModelSerializer):
        field = FieldSerializer(many=True)
        price = serializers.IntegerField()
        image = serializers.ImageField(required=False)
        product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
        is_default = serializers.BooleanField(required=False)

        class Meta:
            model = Variant
            fields = '__all__'

    class VairantOutSerializer(serializers.ModelSerializer):
        field = FieldSerializer(many=True)
        class Meta:
            model = Variant
            fields = "__all__"

    queryset = Variant.objects.all()
    serializer_class = VairantOutSerializer
    performer_serializer_class = VariantInSerializer
    filterset_class = VariantFilter
    lookup_field = 'sku'

    @swagger_auto_schema(
        request_body=performer_serializer_class,
        responses={201: serializer_class},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.performer_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        variant = serializer.save()
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

        class Meta:
            model = Product
            fields = '__all__'
    class ProductOutSerializer(serializers.ModelSerializer):
        variant = VariantView.VairantOutSerializer(many=True)

        class Meta:
            model = Product
            fields = ("uuid","name", "description", "variant", "quantity")

    queryset = Product.objects.all()
    serializer_class = ProductOutSerializer
    performer_serializer_class = ProductInSerializer
    lookup_field = "uuid"

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
    product = serializers.IntegerField()
    quantity = serializers.IntegerField()


class ItemsRetriveSerializer(serializers.Serializer):
    product = ProductView.ProductOutSerializer()
    quantity = serializers.IntegerField()


class OrderView(ModelViewSet):
    class OrderInSerializer(serializers.Serializer):
        items = serializers.ListField(child=VariantSerializer())

        ordered_by = serializers.IntegerField()
        assigned_to = serializers.IntegerField(required=False)

        def create(self, validated_data):
            order_item_list = []
            for item in validated_data.pop("items"):
                product = Variant.objects.get(sku=item["product"])
                if product.quantity < item["quantity"]:
                    raise serializers.ValidationError(
                        "Not enough quantity for product {}".format(product.name)
                    )
                product.quantity -= item["quantity"]
                product.save()

                order_item = OrderItem.objects.create(
                    product=product, quantity=item["quantity"]
                )

                order_item_list.append(order_item)
            try:
                ordered_by = user_model.objects.get(id=validated_data.pop("ordered_by"))
            except user_model.DoesNotExist:
                raise serializers.ValidationError("User does not exist")
            try:
                assigned_to = user_model.objects.get(
                    id=validated_data.pop("assigned_to")
                )
            except KeyError:
                assigned_to = None
            except user_model.DoesNotExist:
                raise serializers.ValidationError("User does not exist")
            order = Order.objects.create(
                ordered_by=ordered_by, assigned_to=assigned_to, **validated_data
            )
            order.items.set(order_item_list)
            return order

        def update(self, instance, validated_data):
            order_item_list = []
            try:
                for item in validated_data.pop("items"):
                    product = Product.objects.get(id=item["product"])
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
        ordered_by = serializers.CharField(source="ordered_by.email", read_only=True)
        assigned_to = serializers.CharField(source="assigned_to.email", read_only=True)
        # status = serializers.CharField(source="status")
        items = ItemsRetriveSerializer(many=True)
        # uuid = serializers.CharField(source="uuid")
        # ordered_date = serializers.DateTimeField(source="ordered_date")
        # completed_date = serializers.DateTimeField(source="completed_date")

        class Meta:
            model = Order
            fields = (
                "ordered_by",
                "assigned_to",
                "status",
                "items",
                "uuid",
                "ordered_date",
                "completed_date",
            )

    queryset = Order.objects.all()
    serializer_class = OrderOutSerializer
    perfomer_serializer_class = OrderInSerializer
    lookup_field = "uuid"
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=perfomer_serializer_class,
        responses={201: serializer_class},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.perfomer_serializer_class(data=request.data)
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
