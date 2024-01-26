# Generated by Django 5.0.1 on 2024-01-26 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('football_stats', '0016_alter_team_founded'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='adress',
            field=models.CharField(blank=True, max_length=100, verbose_name='Адрес команды'),
        ),
        migrations.AlterField(
            model_name='team',
            name='coach',
            field=models.CharField(blank=True, max_length=50, verbose_name='Тренер'),
        ),
        migrations.AlterField(
            model_name='team',
            name='stadium',
            field=models.CharField(blank=True, max_length=100, verbose_name='Стадион команды'),
        ),
        migrations.AlterField(
            model_name='team',
            name='website',
            field=models.CharField(blank=True, max_length=100, verbose_name='Сайт команды'),
        ),
    ]