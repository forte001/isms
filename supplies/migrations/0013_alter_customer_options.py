# Generated by Django 5.1.1 on 2024-10-22 00:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supplies', '0012_alter_customer_options_alter_customer_managers_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'permissions': [('can_view_profile', 'Can view profile'), ('can_edit_profile', 'Can edit profile'), ('can_delete_customer', 'Can delete customer')]},
        ),
    ]
