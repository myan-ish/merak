import uuid
from django.db import models
from user.models import User

class VarientField(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Variant(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    field = models.ForeignKey(VarientField, on_delete=models.CASCADE)

    def __str__(self):
        return self.field.name if self.field else ''


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    variant = models.ForeignKey(Variant, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    uuid = models.CharField(max_length=255, blank=True, null=True,unique=True)

    owned_by = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE)

    @property
    def price(self):
        return self.variant.price if self.variant else ''

    @property
    def is_active(self):
        return self.quantity > 0

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # generate uuid
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0)

    @property
    def price(self):
        return self.product.price

    def __str__(self):
        return self.product.name if self.product else self.id
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

# Status Enum
class Status(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    ACCEPTED = 'ACCEPTED', 'Accepted'
    PROCESSING = 'PROCESSING', 'Processing'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'

class Order(models.Model):
    uuid = models.CharField(max_length=255, blank=True,unique=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )

    items = models.ManyToManyField(OrderItem)
    owned_by = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='orders')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='assigned_orders')

    ordered_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(blank=True, null=True)

    @property
    def total(self):
        return sum([item.price for item in self.items.all()])
    
    def get_pending_orders(self):
        return Order.objects.filter(status=Status.PENDING)
    
    def get_estimated_earning(self):
        return sum([order.total for order in self.get_pending_orders()])
    
    def get_completed_orders(self):
        return Order.objects.filter(status=Status.COMPLETED)

    def get_total_earning(self):
        return sum([order.total for order in self.get_total_orders()])

    def __str__(self):
        return self.ordered_by.email if self.assigned_to else ''
    
    def save(self, *args, **kwargs):
        # generate uuid
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)