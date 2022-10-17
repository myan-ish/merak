from rest_framework import serializers
from django.contrib.auth import get_user_model

from inventory.models import Order, OrderItem, Variant
from inventory.serializers.product import ItemsRetriveSerializer, VariantSerializer
from inventory.serializers.user import CustomerOutSerializer, UserOutSerializer
from user.models import Customer

user_model = get_user_model()


class OrderOutSerializer(serializers.ModelSerializer):
    ordered_by = CustomerOutSerializer(read_only=True)
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
    ordered_by = CustomerOutSerializer(read_only=True)
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
