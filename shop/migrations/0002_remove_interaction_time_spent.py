# Generated by Django 4.2.18 on 2025-01-17 02:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interaction',
            name='time_spent',
        ),
    ]
