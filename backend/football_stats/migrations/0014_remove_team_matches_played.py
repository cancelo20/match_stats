# Generated by Django 4.2.9 on 2024-01-12 15:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('football_stats', '0013_alter_team_options_remove_team_points'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='matches_played',
        ),
    ]