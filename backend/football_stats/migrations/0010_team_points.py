# Generated by Django 4.2.9 on 2024-01-12 06:07

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('football_stats', '0009_league_matchday_end_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='points',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(200)], verbose_name='Очки'),
        ),
    ]