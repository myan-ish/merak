# Generated by Django 3.2 on 2022-07-07 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='image',
            field=models.ImageField(blank=True, upload_to='expense_images'),
        ),
    ]
