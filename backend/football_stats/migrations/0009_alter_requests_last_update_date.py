# Generated by Django 5.0.1 on 2024-01-20 05:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('football_stats', '0008_team_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requests',
            name='last_update_date',
            field=models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), verbose_name='Дата и время начала тура'),
        ),
    ]
