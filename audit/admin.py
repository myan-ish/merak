from django.contrib import admin

from audit.models import Expense, ExpenseCategory

admin.site.register(ExpenseCategory)


class ExpenseAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "amount",
        "date",
        "category",
        "image",
        "organization",
        "requested_by",
    ]
    list_filter = ["date"]


admin.site.register(Expense, ExpenseAdmin)
