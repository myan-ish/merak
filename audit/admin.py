from django.contrib import admin

from audit.models import Expense, ExpenseCategory,Entry, Ledger

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

class EntryAdmin(admin.ModelAdmin):
    list_display = ["amount", "type", "date","credit"]
    list_filter = ["date"]

    def credit(self, obj):
        return obj.is_credit

    credit.boolean = True

class LedgerAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "opening_balance", "closing_balance", "related_user"]
    list_filter = ["type"]

admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Ledger, LedgerAdmin)