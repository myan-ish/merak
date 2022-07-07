from django.db import models

from user.models import User


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        "user.Organization", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.name


class Expense(models.Model):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now=True)
    category = models.ForeignKey(
        "ExpenseCategory", on_delete=models.SET_NULL, null=True
    )
    image = models.ImageField(upload_to="expense_images", blank=True, null=True)
    organization = models.ForeignKey(
        "user.Organization", on_delete=models.CASCADE, null=True, blank=True
    )
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name
