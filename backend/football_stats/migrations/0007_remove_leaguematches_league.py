# Generated by Django 4.2.9 on 2024-01-11 14:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('football_stats', '0006_remove_league_current_matches_leaguematches_league'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leaguematches',
            name='league',
        ),
    ]