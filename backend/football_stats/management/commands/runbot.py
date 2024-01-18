import os
import telebot

from threading import Thread
from dotenv import load_dotenv
from datetime import datetime as dt, timedelta as td
from pytz import UTC

from django.core.management import BaseCommand

from football_stats.checks import Checks
from football_stats.models import *

load_dotenv()


TG_TOKEN = str(os.getenv('TG_TOKEN'))
bot = telebot.TeleBot(TG_TOKEN)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "Start football bot"

    def handle(self, *args, **options):
        def run():
            while True:
                try:
                    print(
                        'Бот начал свою работу.\n' +
                        'id в Телеграме: @EPLStatsBot (https://t.me/EPLStatsBot)\n' +
                        '_______________________________________________________'
                    )
                    bot.infinity_polling()
                except Exception as error:
                    print(error)
                    continue

        Thread(target=run, daemon=True).start()
        input('Press <Enter> to exit.\n')


# удаляет выбранное количество сообщений (по дефолту - 2)
def del_last_msg(chat_id, message_id, number=2, timeout=0):
    for i in range(number, 0, -1):
        try:
            bot.delete_message(
                chat_id=chat_id,
                message_id=message_id-i,
                timeout=timeout)
        except:
            continue


def datetime_to_text(datetime_type):
    date = str(datetime_type.date()).split('-')
    time = str(datetime_type.time()).split(':')
    month = date[1]
    day = date[2]
    hour = time[0]
    minutes = time[1]

    return f'{day}.{month} {hour}:{minutes}'


# Обработка команды /start
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    text = (
        f'Привет, {name}, я готов работать!\n\n' +
        '/teams - таблица лиги\n' +
        '/matchday - предстоящий тур\n' +
        '/scorers - список бомбардиров лиги'
    )

    del_last_msg(message.chat.id, message.message_id)

    bot.send_message(
        message.chat.id, text)


# обработка команды /clear
@bot.message_handler(commands=['clear'])
def clear(message):
    chat_id = message.chat.id
    message_id = message.message_id
    try:
        number = int(message.text.split(' ')[1])
    except:
        number = 2
    finally:
        del_last_msg(chat_id, message_id, number)
        bot.delete_message(chat_id=chat_id, message_id=message_id)


# Обработка команд /matchday и /teams
@bot.message_handler(commands=['matchday', 'teams', 'scorers'])
def league_choosing_cmd(message):
    del_last_msg(message.chat.id, message.message_id)
    button = telebot.types.InlineKeyboardMarkup(row_width=1)
    command = message.text

    leagues = League.objects.all()

    for league in leagues:
        league_name = league.name
        data = f'{command}&{league_name}'
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
    league_name = callback.data.split('&')[1]
    text = f'Матчи {league_name}\n\n'

    matches = LeagueMatches.objects.filter(name=league_name)
    button = telebot.types.InlineKeyboardMarkup(row_width=1)

    for f_match in matches:
        data = f'{...}&{f_match.current_match}'
        button_text = f'{f_match.current_match} '
        now = dt.now().replace(tzinfo=UTC)
        if f_match.finished:
            button_text += f_match.fulltime
        else:
            if now >= f_match.date and now < f_match.date + td(hours=1, minutes=45):
                button_text += 'IN LIVE'
            else:
                date = datetime_to_text(f_match.date + td(hours=3))
                button_text += f'{date} МСК'

        button.add(
            telebot.types.InlineKeyboardButton(button_text, callback_data=data)
        )

    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=text,
        reply_markup=button
    )


# Выдает список команд лиги
def teams(callback):
    pass


# Выдает список бомбардиров лиги
def scorers(callback):
    league_name = callback.data.split('&')[1]
    players = Player.objects.filter(league=league_name)
    text = f'Бомбардиры {league_name}\nГ - голы(с пенальти) П - гол. пасы\n\n'

    for player in players:
        name = player.name
        goals = player.goals
        penalty = player.penalty
        assists = player.assists
        team = player.team

        text += f'{name}({team}) {goals}({penalty})Г {assists}П\n\n'

    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=text,
    )

def stats(callback):
    teams_list = callback.data.split('&')[1].split(' - ')
    text = 'Статистика за 10 матчей:\n\n'
    if len(teams_list) == 2:
        for team_name in teams_list:
            print(team_name)
            text += get_team_stats(team_name=team_name)
        text += get_teams_probability(teams_list)
    elif len(teams_list) == 1:
        text += get_team_stats(team_name=teams_list[0])

    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=text
    )

def get_team_stats(team_name: str) -> str:
    print(get_team_stats.__name__)
    stats = Statistics.objects.get(name=team_name)
    text = f'{team_name}\n'
    text += f'Победы: {stats.wins}\n'
    text += f'Ничьи: {stats.draws}\n'
    text += f'Поражения: {stats.loses}\n'
    text += f'Форма: {stats.form}\n'
    text += f'Форма дома: {stats.home_form}\n'
    text += f'Форма в гостях: {stats.away_form}\n\n'

    return text


def get_teams_probability(teams: list) -> str:
    return str()


# Логика работы кнопок
@bot.callback_query_handler(func=lambda c:True)
def callback_inline(callback):
    current_commands = ['/matchday', '/teams', '/scorers']
    command = callback.data.split('&')[0]
    data = callback.data.split('&')[1]

    if command in current_commands:
        check = Checks(
            league_name=data,
            chat_id=callback.message.chat.id,
            message_id=callback.message.id
        )

        check.is_current_tour()
        check.is_matches_finished()

    if command == '/matchday':
        matchday(callback)
    elif command == '/teams':
        teams(callback)
    elif command == '/scorers':
        scorers(callback)
    else:
        stats(callback)
