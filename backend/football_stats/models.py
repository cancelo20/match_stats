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
    current_matchday = models.IntegerField(
        verbose_name='Предстоящий тур',
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(40)
        ]
    )
    matchday_end_date = models.CharField(
        max_length=15,
        verbose_name='Дата окончания тура',
        blank=True
    )


    class Meta:
        ordering = ['id']
        verbose_name = 'Лига'
        verbose_name_plural = 'Лиги'

    def __str__(self):
        return self.name


class LeagueMatches(models.Model):
    name = models.CharField(
        max_length = 100,
        verbose_name = 'Название Лиги'
    )
    current_match = models.CharField(
        max_length = 100,
        verbose_name = 'Актуальный матч'
    )
    date = models.CharField(
        max_length = 100,
        verbose_name = 'Дата матча (МСК)',
        blank=True
    )
    fulltime = models.CharField(
        max_length = 100,
        verbose_name = 'Счет матча',
        blank=True
    )
    finished = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Матч лиги'
        verbose_name_plural = 'Матчи лиги'

    def __str__(self):
        return self.current_match


class Team(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название команды'
    )
    url_id = models.IntegerField(
        verbose_name='url_id',
        unique=True
    )
    shortname = models.CharField(
        max_length=5,
        verbose_name='Аббревиатура команды'
    )
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        verbose_name='Лига',
    )
    stats_last_10 = models.ForeignKey(
        'Statistics',
        on_delete=models.CASCADE,
        verbose_name='Статистика команды',
        blank=True,
        null=True
    )
    total_wins = models.IntegerField(
        verbose_name='Общее кол-во побед',
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(50)
        ]
    )
    total_loses = models.IntegerField(
        verbose_name='Общее кол-во поражений',
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(50)
        ]
    )
    total_draws = models.IntegerField(
        verbose_name='Общее кол-во ничьих',
        default=0,
        validators=[
            MinValueValidator(1),
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
        ordering = ['league__name', '-points']
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'

    def __str__(self):
        return self.name


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
    home_wins = models.IntegerField(
        verbose_name='Домашние победы',
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(40)
        ]
    )
    home_draws = models.IntegerField(
        verbose_name='Домашние ничьи',
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(40)
        ]
    )
    home_loses = models.IntegerField(
        verbose_name='Домашние поражения',
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(40)
        ]
    )
    away_wins = models.IntegerField(
        verbose_name='Гостевые победы',
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(40)
        ]
    )
    away_draws = models.IntegerField(
        verbose_name='Гостевые ничьи',
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(40)
        ]
    )
    away_loses = models.IntegerField(
        verbose_name='Гостевые поражения',
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(40)
        ]
    )
    form = models.CharField(
        max_length=10,
        blank=True,
        verbose_name = 'Форма команды'
    )
    home_form = models.CharField(
        max_length=10,
        blank=True,
        verbose_name = 'Домашняя форма команды'
    )
    away_form = models.CharField(
        max_length=10,
        blank=True,
        verbose_name = 'Гостевая форма команды'
    )
    goals = models.PositiveSmallIntegerField(
        verbose_name='Голы',
        default=0
    )

    class Meta:
        verbose_name = 'Статистика'
        verbose_name_plural = 'Статистика'

    def __str__(self):
        return self.name
