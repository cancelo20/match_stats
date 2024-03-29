from datetime import datetime as dt
from pytz import UTC

from django.core.validators import (
    MinValueValidator, MaxValueValidator)
from django.db import models


class League(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название лиги'
    )
    league_code = models.CharField(
        max_length=5,
        verbose_name='Код лиги',
        unique=True
    )
    country = models.CharField(
        max_length=20,
        verbose_name='Страна лиги',
        blank=True
    )
    current_matchday = models.IntegerField(
        verbose_name='Предстоящий тур',
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(40)
        ]
    )
    start_date = models.DateTimeField(
        default=dt(1, 1, 1, 0, 0, 0, tzinfo=UTC),
        verbose_name='Дата и время начала тура'
    )
    end_date = models.DateTimeField(
        default=dt(1, 1, 1, 0, 0, 0, tzinfo=UTC),
        verbose_name='Дата и время окончания тура'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Лига'
        verbose_name_plural = 'Лиги'

    def __str__(self):
        return self.name


class LeagueMatches(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название Лиги'
    )
    current_match = models.CharField(
        max_length=100,
        verbose_name='Актуальный матч'
    )
    fulltime = models.CharField(
        max_length=100,
        verbose_name='Счет матча',
        blank=True
    )
    date = models.DateTimeField(
        default=dt(1, 1, 1, 0, 0, 0, tzinfo=UTC),
        verbose_name='Дата и время матча'
    )
    finished = models.BooleanField(
        default=False,
        verbose_name='Проверка на завершенность матча'
    )

    class Meta:
        ordering = ['name', 'date']
        verbose_name = 'Матч лиги'
        verbose_name_plural = 'Матчи лиги'

    def __str__(self):
        return self.current_match


class Team(models.Model):
    fullname = models.CharField(
        max_length=50,
        verbose_name='Полное название команды',
        blank=True
    )
    name = models.CharField(
        max_length=50,
        verbose_name='Название команды'
    )
    shortname = models.CharField(
        max_length=5,
        verbose_name='Аббревиатура команды'
    )
    url_id = models.IntegerField(
        verbose_name='url_id',
        unique=True
    )
    league = models.CharField(
        max_length=100,
        verbose_name='Лига',
    )
    founded = models.IntegerField(
        verbose_name='Год создания',
        null=True
    )
    stadium = models.CharField(
        max_length=100,
        verbose_name='Стадион команды',
        blank=True,
    )
    adress = models.CharField(
        max_length=100,
        verbose_name='Адрес команды',
        blank=True,
    )
    website = models.CharField(
        max_length=100,
        verbose_name='Сайт команды',
        blank=True,
    )
    coach = models.CharField(
        max_length=50,
        verbose_name='Тренер',
        blank=True,
    )
    position = models.IntegerField(
        verbose_name='Позиция в таблице',
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(40)
        ]
    )
    total_wins = models.IntegerField(
        verbose_name='Общее кол-во побед',
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(50)
        ]
    )
    total_loses = models.IntegerField(
        verbose_name='Общее кол-во поражений',
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(50)
        ]
    )
    total_draws = models.IntegerField(
        verbose_name='Общее кол-во ничьих',
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(50)
        ]
    )
    points = models.IntegerField(
        verbose_name='Кол-во очков',
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(200)
        ]
    )

    class Meta:
        ordering = ['league', '-points']
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'

    def __str__(self):
        return f'{self.name} - {self.league}'


class Player(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Имя'
    )
    league = models.CharField(
        max_length=200,
        verbose_name='Лига'
    )
    team = models.CharField(
        max_length=200,
        verbose_name='Команда'
    )
    goals = models.IntegerField(
        verbose_name='Кол-во голов',
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(200)
        ]
    )
    penalty = models.IntegerField(
        verbose_name='Кол-во голов с пенальти',
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(200)
        ]
    )
    assists = models.IntegerField(
        verbose_name='Кол-во гол. передач',
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(200)
        ]
    )
    matches = models.IntegerField(
        verbose_name='Кол-во матчей',
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(50)
        ]
    )

    class Meta:
        ordering = ['league', '-goals']
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'

    def __str__(self):
        return self.name


class Statistics(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название команды'
    )
    wins = models.IntegerField(
        verbose_name='Победы',
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(50)
        ]
    )
    draws = models.IntegerField(
        verbose_name='Ничьи',
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(40)
        ]
    )
    loses = models.IntegerField(
        verbose_name='Поражения',
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(40)
        ]
    )
    form = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Форма команды'
    )
    home_form = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Домашняя форма команды'
    )
    away_form = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Гостевая форма команды'
    )
    goals_scored = models.PositiveSmallIntegerField(
        verbose_name='Забитые голы',
        default=0
    )
    goals_conceded = models.PositiveSmallIntegerField(
        verbose_name='Пропущенные голы',
        default=0
    )

    class Meta:
        verbose_name = 'Статистика'
        verbose_name_plural = 'Статистика'

    def __str__(self):
        return self.name


class Requests(models.Model):
    count = models.IntegerField(
        verbose_name='количество запросов',
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10)
        ]
    )
    last_update_date = models.DateTimeField(
        verbose_name='Дата и время начала тура',
        default=dt(1, 1, 1, 0, 0, 0, tzinfo=UTC)
    )


class IsUpdating(models.Model):
    league_name = models.CharField(
        max_length=50,
        blank=True
    )
    is_updating = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f'{self.league_name} - {self.is_updating}'
