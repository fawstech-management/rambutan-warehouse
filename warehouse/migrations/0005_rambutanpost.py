# Generated by Django 5.0.3 on 2024-09-20 15:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0004_delete_rambutanpost'),
    ]

    operations = [
        migrations.CreateModel(
            name='RambutanPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('variety', models.CharField(max_length=100)),
                ('quantity', models.PositiveIntegerField()),
                ('price_per_kg', models.DecimalField(decimal_places=2, max_digits=10)),
                ('image_url', models.URLField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('farmer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rambutan_posts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
