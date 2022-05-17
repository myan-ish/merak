from pyexpat import model
from django.contrib import admin

from inventory.models import Order, OrderItem, Product, Variant, VarientField

class CustomProduct(admin.ModelAdmin):
    model = Product
    readonly_fields = ('uuid',)
    list_display = ('name', 'quantity', 'uuid')
    list_filter = ('name', 'uuid')

class CustomVariant(admin.ModelAdmin):
    model = Variant
    list_display = ( 'image','price')

class CustomVarientField(admin.ModelAdmin):
    model = VarientField
    list_display = ('name', 'value')
    list_filter = ('name',)

class CustomOrder(admin.ModelAdmin):
    model = Order
    readonly_fields = ('uuid',)
    list_display = ('uuid', 'ordered_by', 'ordered_date', 'status')

admin.site.register(Product, CustomProduct)
admin.site.register(Variant, CustomVariant)
admin.site.register(VarientField, CustomVarientField)
admin.site.register(Order, CustomOrder)
admin.site.register(OrderItem)
