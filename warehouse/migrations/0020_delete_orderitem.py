# Generated by Django 5.0.3 on 2024-10-02 11:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0019_order_orderitem'),
    ]

    operations = [
        migrations.DeleteModel(
            name='OrderItem',
        ),
    ]
