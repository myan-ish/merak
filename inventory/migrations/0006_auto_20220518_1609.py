# Generated by Django 3.2 on 2022-05-18 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_auto_20220518_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='variant',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='variant',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
    ]
