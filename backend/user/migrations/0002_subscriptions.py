# Generated by Django 5.0.1 on 2024-01-22 13:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('football_stats', '0010_delete_user'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscriptions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_send_message', models.BooleanField(default=False)),
                ('f_match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='football_stats.leaguematches', verbose_name='Матч')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user', verbose_name='Пользователь')),
            ],
        ),
    ]
