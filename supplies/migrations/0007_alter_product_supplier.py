# Generated by Django 5.1.1 on 2024-10-15 13:04

import django.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplies', '0006_customer_created_at_customer_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.fields.BooleanField, to='supplies.supplier'),
        ),
    ]