from contextlib import closing
import uuid
from django.db import models

from user.models import Customer, User


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

class EntryTypeEnum(models.TextChoices):
    SALES_INVOICE = "SI", "Sales Invoice" # Debit
    SALES_RETURN = "SR", "Sales Return" # Credit
    PURCHASE_INVOICE = "PI", "Purchase Invoice" # Credit
    PURCHASE_RETURN = "PR", "Purchase Return" # Debit
    RECEIPT_VOUCHER = "RV", "Receipt Voucher" # Credit
    PAYMENT_VOUCHER = "PV", "Payment Voucher" # Debit
    JOURNAL_VOUCHER = "JV", "Journal Voucher" # Debit/Credit

class Entry(models.Model):
    # TODO: Add products and list of products
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now=True)
    is_credit = models.BooleanField(default=False)
    closing_balance = models.DecimalField(max_digits=15, decimal_places=2) 
    type = models.CharField(max_length=2, choices=EntryTypeEnum.choices)
    organization = models.ForeignKey(
        "user.Organization", on_delete=models.CASCADE, null=True, blank=True
    )
    
    class Meta:
        ordering = ["-date"]

class LedgerTypeEnum(models.TextChoices):
    CAPITAL = "CAPITAL", "Capital" #Credit
    FIXED_ASSET = "FIXED_ASSET", "Fixed Asset" #Debit
    CURRENT_ASSSET = "CURRENT_ASSSET", "Current Asset" #Debit
    LOAN_AND_ADVANCE = "LOAN_AND_ADVANCE", "Loan and Advance" #Credit
    CASH_AND_BANK = "CASH_AND_BANK", "Cash and Bank" #Credit
    INCOME = "INCOME", "Income" #Debit
    LIABILITY = "LIABILITY", "Liability" #Credit
    EXPENSE = "EXPENSE", "Expense" #Debit
    CUSTOMER = "CUSTOMER", "Customer" #Debit
    VENDOR = "VENDOR", "Vendor" #Credit
    CUSTOMER_AND_VENDOR = "CUSTOMER_AND_VENDOR", "Customer and Vendor" # Debit/Credit


class Ledger(models.Model):
    # TODO: Separate ledger by date so separate fiscal years can have different ledgers
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    type = models.CharField(
        max_length=255, choices=LedgerTypeEnum.choices, default=LedgerTypeEnum.CUSTOMER
    )

    opening_balance = models.DecimalField(max_digits=15, decimal_places=2)
    closing_balance = models.DecimalField(max_digits=15, decimal_places=2)

    related_user = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True
    )

    organization = models.ForeignKey(
        "user.Organization", on_delete=models.CASCADE, null=True, blank=True
    )

    entries = models.ManyToManyField(
        Entry, blank=True)
    
    credit = models.DecimalField(decimal_places=2, default=0, max_digits=15)
    debit = models.DecimalField(decimal_places=2, default=0,max_digits=15)


    def __str__(self):
        return self.name

    def is_credit(self, type):
        if type in [EntryTypeEnum.SALES_INVOICE, EntryTypeEnum.PURCHASE_RETURN, EntryTypeEnum.RECEIPT_VOUCHER, EntryTypeEnum.JOURNAL_VOUCHER]:
            return False
        return True
    
    def make_transaction(self, amount, is_credit, type):
        self.closing_balance = self.closing_balance + amount if not is_credit else self.closing_balance - amount
        self.save()
        entry = Entry.objects.create(
            amount=amount,
            is_credit=is_credit,
            closing_balance=self.closing_balance,
            type=type,
            organization=self.organization
        )
        self.entries.add(entry)
        self.save()
    
    
    def save(self, *args, **kwargs):
        self.name = self.related_user.name

        return super().save(*args, **kwargs)
    

