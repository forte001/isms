# Generated by Django 5.1.1 on 2024-10-11 15:42

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplies', '0005_stockadjustment'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='customer',
            name='password',
            field=models.CharField(default='password', max_length=128),
        ),
    ]
