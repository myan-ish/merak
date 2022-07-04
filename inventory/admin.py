from pyexpat import model
import uuid
from django.contrib import admin

from inventory.models import (
    Order,
    OrderItem,
    Product,
    Variant,
    VarientField,
    VariantFieldName,
)


class CustomProduct(admin.ModelAdmin):
    model = Product
    readonly_fields = ("uuid",)
    list_display = ("name", "uuid")
    list_filter = ("name", "uuid")


class CustomVariant(admin.ModelAdmin):
    model = Variant
    list_display = ("__str__", "price")

    def save_related(self, request, form,formsets, change) -> None:
        super().save_related(request, form, formsets, change)
        form.instance.set_sku()
        return super().save_related(request, form, formsets, change)
        
class CustomVarientField(admin.ModelAdmin):
    model = VarientField
    list_display = ("name", "value")
    list_filter = ("name",)


class CustomOrder(admin.ModelAdmin):
    model = Order
    readonly_fields = ("uuid",)
    list_display = ("uuid", "ordered_by", "ordered_date", "status")


admin.site.register(Product, CustomProduct)
admin.site.register(Variant, CustomVariant)
admin.site.register(VarientField, CustomVarientField)
admin.site.register(Order, CustomOrder)
admin.site.register(OrderItem)
admin.site.register(VariantFieldName)
