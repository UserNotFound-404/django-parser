# Generated by Django 5.1.5 on 2025-01-24 12:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(unique=True)),
                ('address', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('price_guidance', models.CharField(max_length=255)),
                ('bedrooms', models.PositiveIntegerField(blank=True, null=True)),
                ('bathrooms', models.PositiveIntegerField(blank=True, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('contact_info', models.TextField(blank=True, null=True)),
                ('property_type', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.URLField()),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='properties.property')),
            ],
        ),
    ]
