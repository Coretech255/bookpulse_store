# Generated by Django 4.2.18 on 2025-01-17 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_remove_interaction_time_spent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='rating',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=4),
        ),
    ]
