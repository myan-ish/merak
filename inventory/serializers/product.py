from django.contrib.auth import get_user_model

from rest_framework import serializers
from inventory.models import (
    Product,
    Variant,
    VariantFieldName,
    VarientField,
)

from drf_writable_nested.serializers import WritableNestedModelSerializer

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

class VariantSerializer(serializers.Serializer):
    product = serializers.CharField()
    quantity = serializers.IntegerField()


class ItemsRetriveSerializer(serializers.Serializer):
    product = VairantOutSerializer()
    quantity = serializers.IntegerField()
    line_total = serializers.SerializerMethodField()

    def get_line_total(self, obj):
        return obj.product.price * obj.quantity

class VariantSerializer(serializers.Serializer):
    product = serializers.CharField()
    quantity = serializers.IntegerField()


class ItemsRetriveSerializer(serializers.Serializer):
    product = VairantOutSerializer()
    quantity = serializers.IntegerField()
    line_total = serializers.SerializerMethodField()

    def get_line_total(self, obj):
        return obj.product.price * obj.quantity
