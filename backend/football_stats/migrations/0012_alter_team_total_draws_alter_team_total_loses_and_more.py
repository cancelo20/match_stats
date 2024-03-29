# Generated by Django 5.0.1 on 2024-01-25 15:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('football_stats', '0011_team_logo_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='total_draws',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(50)], verbose_name='Общее кол-во ничьих'),
        ),
        migrations.AlterField(
            model_name='team',
            name='total_loses',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(50)], verbose_name='Общее кол-во поражений'),
        ),
        migrations.AlterField(
            model_name='team',
            name='total_wins',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(50)], verbose_name='Общее кол-во побед'),
        ),
    ]
