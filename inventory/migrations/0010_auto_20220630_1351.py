# Generated by Django 3.2 on 2022-06-30 08:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_customer'),
        ('inventory', '0009_auto_20220614_2205'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.organization'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.organization'),
        ),
        migrations.AddField(
            model_name='product',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.organization'),
        ),
        migrations.AddField(
            model_name='variant',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.organization'),
        ),
        migrations.AddField(
            model_name='varientfield',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.organization'),
        ),
    ]
