from django.db import models
from django.core.validators import (
    MinValueValidator, MaxValueValidator)
from football_stats.models import LeagueMatches


class User(models.Model):
    username = models.CharField(
        max_length=100,
        verbose_name='Имя пользователя',
        unique=True
    )
    chat_id = models.PositiveSmallIntegerField(
        default = 0
    )
    time_zone = models.IntegerField(
        verbose_name='Часовой пояс',
        default=0,
        validators=[
            MinValueValidator(-12),
            MaxValueValidator(12)
        ]
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    f_match = models.ForeignKey(
        LeagueMatches,
        on_delete=models.CASCADE,
        verbose_name='Матч'
    )
    is_send_message = models.BooleanField(
        default=False
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} : {self.f_match}'
