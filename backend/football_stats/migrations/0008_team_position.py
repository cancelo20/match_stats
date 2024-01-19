# Generated by Django 5.0.1 on 2024-01-19 12:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('football_stats', '0007_league_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='position',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(40)], verbose_name='Позиция в таблице'),
        ),
    ]