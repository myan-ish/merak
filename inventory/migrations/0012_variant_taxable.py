# Generated by Django 4.0.3 on 2022-10-17 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_alter_order_ordered_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='variant',
            name='taxable',
            field=models.BooleanField(default=True),
        ),
    ]
