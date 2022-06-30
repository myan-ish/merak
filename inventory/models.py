import uuid
from django.db import models
from user.models import Customer, User


class VariantFieldName(models.Model):
    name = models.CharField(max_length=255)  #

    def __str__(self):
        return self.name


class VarientField(models.Model):
    name = models.ForeignKey(
        VariantFieldName, null=True, blank=True, on_delete=models.CASCADE
    )
    value = models.CharField(max_length=100)

    organization = models.ForeignKey(
        "user.Organization", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.name.name + "-" + self.value


class Variant(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    field = models.ManyToManyField(VarientField)
    product = models.ForeignKey(
        "Product", on_delete=models.SET_NULL, blank=True, null=True
    )
    image = models.ImageField(upload_to="variant_images", blank=True)
    quantity = models.IntegerField(default=0)
    sku = models.CharField(max_length=100, blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    organization = models.ForeignKey(
        "user.Organization", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.sku if self.sku else str(self.id)

    def set_sku(self):
        self.sku = self.product.name + "-"
        fields = [field.value for field in self.field.all()]
        self.sku += "-".join(map(str, fields))
        while Variant.objects.filter(sku=self.sku).exists():
            self.sku += str(uuid.uuid4())[:5]
        self.save()


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    uuid = models.CharField(max_length=255, blank=True, null=True, unique=True)

    owned_by = models.ForeignKey(
        User, related_name="products", on_delete=models.SET_NULL, blank=True, null=True
    )
    organization = models.ForeignKey(
        "user.Organization", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.uuid

    @property
    def default_image(self):
        variants = self.variant_set.all()
        for variant in variants:
            if variant.is_default:
                try:
                    return variant.image.url
                except ValueError:
                    return None
        return None

    @property
    def default_price(self):
        variants = self.variant_set.all()
        for variant in variants:
            if variant.is_default:
                try:
                    return variant.price
                except ValueError:
                    return None

    def save(self, *args, **kwargs):
        # generate uuid
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    product = models.ForeignKey(
        Variant, on_delete=models.PROTECT, blank=True, null=True
    )
    quantity = models.IntegerField(default=0)

    organization = models.ForeignKey(
        "user.Organization", on_delete=models.CASCADE, null=True, blank=True
    )

    @property
    def price(self):
        return self.product.price

    def __str__(self):
        if self.product:
            return self.product.product.name if self.product.product else str(self.id)
        return str(self.id)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


# Status Enum
class Status(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class Order(models.Model):
    uuid = models.CharField(max_length=255, blank=True, unique=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )

    items = models.ManyToManyField(OrderItem)
    owned_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    ordered_by = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="orders",
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="assigned_orders",
    )
    organization = models.ForeignKey(
        "user.Organization", on_delete=models.CASCADE, null=True, blank=True
    )

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
        return self.assigned_to.email if self.assigned_to else ""

    def delete(self):
        self.status = Status.CANCELLED
        self.save()

    def save(self, *args, **kwargs):
        # generate uuid
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
