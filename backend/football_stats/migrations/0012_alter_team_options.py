# Generated by Django 4.2.9 on 2024-01-12 06:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('football_stats', '0011_alter_team_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='team',
            options={'ordering': ['league__name', '-points'], 'verbose_name': 'Команда', 'verbose_name_plural': 'Команды'},
        ),
    ]