# Generated by Django 5.0.3 on 2024-09-20 14:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0002_delete_rambutanpost'),
    ]

    operations = [
        migrations.CreateModel(
            name='RambutanPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('image_url', models.URLField()),
                ('description', models.TextField(blank=True, null=True)),
                ('farmer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
