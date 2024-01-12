import os
import telebot

from django.core.management import BaseCommand
from django.forms.models import model_to_dict

from dotenv import load_dotenv

from football_stats.probability import MatchProbability
from football_stats.updates import LeagueUpdate, TeamUpdate
from football_stats.models import (
    League, LeagueMatches, Statistics, Team)

from datetime import date


load_dotenv()


TG_TOKEN = str(os.getenv('TG_TOKEN'))
bot = telebot.TeleBot(TG_TOKEN)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "Start football bot"

    def handle(self, *args, **options):
            print(
                'Бот начал свою работу.\n' +
                'id в Телеграме: @EPLStatsBot (https://t.me/EPLStatsBot)\n' +
                '_______________________________________________________'
            )
            bot.polling()


# Обработка команды /start
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    text = (
        f'Привет, {name}, я готов работать!\n\n' +
        '/teams - список команд\n' +
        '/matchday - предстоящий тур'
    )

    bot.send_message(
        message.chat.id, text)


# Обработка команд /matchday и /teams
@bot.message_handler(commands=['matchday', 'teams'])
def matchday_team_cmd(message):
    button = telebot.types.InlineKeyboardMarkup(row_width=1)
    command = message.text

    leagues = League.objects.all()

    for league in leagues:
        league_name = league.name
        data = f'{league_name} & {command}'
        button.add(
            telebot.types.InlineKeyboardButton(league_name, callback_data=data)
        )

    bot.send_message(
        message.chat.id,
        'Выбери чемпионат:',
        reply_markup=button
    )

# Выдает матчи актуального matchday
def matchday(callback):
    league_name = callback.data.split(' & ')[0]
    matches = LeagueMatches.objects.filter(name=league_name)

    button = telebot.types.InlineKeyboardMarkup(row_width=1)

    for f_match in matches:
        text = f_match.current_match
        data = f'{text} & {league_name}'

        button.add(
            telebot.types.InlineKeyboardButton(text, callback_data=data)
        )

    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text='Матчи ближайшего тура:',
        reply_markup=button
    )


# Выдает список команд лиги
def teams(callback):
    league_name = callback.data.split(' & ')[0]
    league = League.objects.get(name=league_name)
    teams = Team.objects.filter(league=league)

    button = telebot.types.InlineKeyboardMarkup(row_width=1)

    for team in teams:
        text = team.name

        button.add(
            telebot.types.InlineKeyboardButton(text, callback_data=text)
        )

    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=f'Команды {league.name}',
        reply_markup=button
    )

# Выдает текст результатов
def get_result_text(stats):
    return (
        f'{stats.get("name")}:\n' + f'побед: {stats.get("wins")}\n' + f'ничьих: {stats.get("draws")}\n' +
        f'поражений: {stats.get("loses")}\n' + f'побед дома: {stats.get("home_wins")}\n' +
        f'поражений дома: {stats.get("home_loses")}\n' + f'ничьих дома: {stats.get("home_draws")}\n' +
        f'побед вгостях: {stats.get("away_wins")}\n' + f'поражений вгостях: {stats.get("away_loses")}\n' +
        f'ничьих вгостях: {stats.get("away_draws")}\n' +
        f'всего голов: {stats.get("goals")}\n\n' + f'форма: {stats.get("form")}\n\n' +
        f'форма дома: {stats.get("home_form")}\n\n' + f'форма вгостях: {stats.get("away_form")}'
    )


# Выдает результаты одной команды
def get_team_result(team):
    team_stats_db = Statistics.objects.get(name=team)
    team_stats_dict = model_to_dict(team_stats_db)
    team_stats_text = get_result_text(team_stats_dict)

    return team_stats_text

# Выдает результат команд, запрашиваемого матча
def get_result(teams):
    home_team, away_team = teams.split(' - ')
    home_team_stats_db = Statistics.objects.get(name=home_team)
    away_team_stats_db = Statistics.objects.get(name=away_team)

    home_team_stats_dict = model_to_dict(home_team_stats_db)
    away_team_stats_dict = model_to_dict(away_team_stats_db)

    home_team_stats_text = get_result_text(home_team_stats_dict)
    away_teams_stats_text = get_result_text(away_team_stats_dict)

    probability = MatchProbability(
        home_team_stats_dict, away_team_stats_dict
    )

    return (
        'Статистика за последние 10 матчей:\n\n' +
        f'{home_team_stats_text}\n\n' +
        f'{away_teams_stats_text}\n\n' +
        f'{probability.print_result()}'
    )


# Печатает результат команды
def say_result(callback):
    data = callback.data.split(' & ')
    teams = data[0]

    if len(data) == 1:
        try:
            text = get_team_result(teams)
        except:
            bot.send_message(
                callback.message.chat.id,
                'Что-то пошло не так, попробуйте позже.')
            print('say_result(): get_result() не выдал результат КОМАНДЫ')
        else:
            bot.send_message(
                callback.message.chat.id, text)
            pass

    else:
        try:
            text = get_result(teams)
        except:
            bot.send_message(
                callback.message.chat.id,
                'Что-то пошло не так, попробуйте позже.')
            print('say_result(): get_result() не выдал результат 2-х КОМАНД')
        else:
            bot.send_message(
                callback.message.chat.id, text)
            pass


# Логика работы кнопок
@bot.callback_query_handler(func=lambda c:True)
def callback_inline(callback):
    data = callback.data.split(' & ')

    try:
        command = data[1]
    except:
        say_result(callback)
    else:
        if command == '/matchday':
            league = League.objects.get(name=data[0])
            matchday_end = str(league.matchday_end_date)
            if str(date.today()) > matchday_end:
                LeagueUpdate().matchday_update(league.league_code)
                TeamUpdate().team_results_update(league.name)
            matchday(callback)
        elif command == '/teams':
            teams(callback)

        else:
            say_result(callback)
