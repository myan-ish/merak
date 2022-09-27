# Generated by Django 4.0.3 on 2022-09-26 06:50

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_customer'),
        ('audit', '0004_alter_expense_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateField(auto_now=True)),
                ('type', models.CharField(choices=[('SI', 'Sales Invoice'), ('SR', 'Sales Return'), ('PI', 'Purchase Invoice'), ('PR', 'Purchase Return'), ('RV', 'Receipt Voucher'), ('PV', 'Payment Voucher'), ('JV', 'Journal Voucher')], max_length=2)),
                ('organization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.organization')),
            ],
        ),
        migrations.CreateModel(
            name='Ledger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('CAPITAL', 'Capital'), ('FIXED_ASSET', 'Fixed Asset'), ('CURRENT_ASSSET', 'Current Asset'), ('LOAN_AND_ADVANCE', 'Loan and Advance'), ('CASH_AND_BANK', 'Cash and Bank'), ('INCOME', 'Income'), ('LIABILITY', 'Liability'), ('EXPENSE', 'Expense'), ('CUSTOMER', 'Customer'), ('VENDOR', 'Vendor'), ('CUSTOMER_AND_VENDOR', 'Customer and Vendor')], default='CUSTOMER', max_length=255)),
                ('credit', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('debit', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('entries', models.ManyToManyField(to='audit.entry')),
                ('organization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.organization')),
                ('related_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.customer')),
            ],
        ),
    ]
