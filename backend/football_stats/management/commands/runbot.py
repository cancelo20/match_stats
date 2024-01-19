import os
import telebot

from threading import Thread
from dotenv import load_dotenv
from datetime import datetime as dt, timedelta as td
from time import sleep
from pytz import UTC

from django.core.management import BaseCommand

from football_stats.checks import Checks
from football_stats.probability import MatchProbability
from football_stats.updates import datetime_to_text
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


def check_updating(
        chat_id: int,
        message_id: int,
        league_name: str) -> None:
    print(check_updating.__name__)
    if IsUpdating.objects.get(league_name=league_name).is_updating is True:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text='Загрузка обновлений, пожалуйста, подождите...'
        )
        while True:
            if IsUpdating.objects.get(id=1).is_updating is False:
                break
            sleep(5)


# Обработка команды /start
@bot.message_handler(commands=['start'])
def start(message) -> None:
    name = message.from_user.first_name
    text = (
        f'Привет, {name}, я готов работать!\n\n' +
        '/matches - список ближайших матчей\n' +
        '/competitions - выбор турнира\n' +
        '/timezone - изменение часового пояса\n' +
        'Пример ввода: /timezone 2, где \n' +
        'цифра - ваш часовой пояс, относительно МСК\n' +
        '/clear - очистка 2-х последних сообщений\n' +
        'чтобы очистить нужное вам количество сообщений\n' +
        'введите число, например: /clear 10'
    )

    username = message.from_user.username
    if not User.objects.filter(username=username).exists():
        User.objects.create(username=username)

    del_last_msg(message.chat.id, message.message_id)

    bot.send_message(
        message.chat.id, text)


# обработка команды /clear
@bot.message_handler(commands=['clear'])
def clear(message) -> None:
    chat_id = message.chat.id
    message_id = message.message_id
    try:
        number = int(message.text.split(' ')[1])
    except:
        number = 2
    finally:
        del_last_msg(chat_id, message_id, number)
        bot.delete_message(chat_id=chat_id, message_id=message_id)


# Обработка команд /timezone
@bot.message_handler(commands=['timezone'])
def timezone(message) -> None:
    del_last_msg(message.chat.id, message.message_id)
    try:
        timezone = int(message.text.split(' ')[1])
    except:
        bot.send_message(
            chat_id=message.chat.id,
            text=(
                'Введите команду корректо.\n' +
                'Пример: /timezone 2'))
    else:
        try:
            user = User.objects.get(username=message.from_user.username)
            user.time_zone = timezone
            user.save()
        except:
            bot.send_message(
                chat_id=message.chat.id,
                text='Вы ввели слишком большое число, попробуйте заново')
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text='Часовой пояс обновлен')


@bot.message_handler(commands=['matches'])
def matches(message) -> None:
    del_last_msg(message.chat.id, message.message_id)
    button = telebot.types.InlineKeyboardMarkup(row_width=1)

    matches = LeagueMatches.objects.all().order_by('date')
    for f_match in matches:
        if f_match.finished:
            continue
        button_text = f'{f_match.current_match} ({f_match.name}) '
        if str(f_match.date).startswith(str(dt.utcnow().date())):
            data = f'{f_match.current_match}&{f_match.name}&/matches'
            now = dt.utcnow().replace(tzinfo=UTC)
            if now >= f_match.date and now < f_match.date + td(hours=1, minutes=45):
                button_text += '| IN LIVE'
            else:
                user = message.from_user.username
                timezone = User.objects.get(username=user).time_zone + 3
                date = datetime_to_text(f_match.date + td(hours=timezone))
                button_text += f'| {date}'

            button.add(
                telebot.types.InlineKeyboardButton(button_text, callback_data=data)
            )
        else:
            break
    if len(button.keyboard) > 0:
        bot.send_message(
            chat_id=message.chat.id,
            text='Ближайшие матчи',
            reply_markup=button
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text='Сегодня нет матчей.'
        )

# Обработка команд /matchday и /teams
@bot.message_handler(commands=['competitions'])
def league_choosing_cmd(message) -> None:
    del_last_msg(message.chat.id, message.message_id)
    button = telebot.types.InlineKeyboardMarkup(row_width=1)
    command = message.text

    leagues = League.objects.all()

    for league in leagues:
        league_name = league.name
        country = league.country
        text = f'{league_name} ({country})'
        data = f'{command}&{league_name}'
        button.add(
            telebot.types.InlineKeyboardButton(text=text, callback_data=data)
        )

    bot.send_message(
        message.chat.id,
        'Выбери чемпионат:',
        reply_markup=button
    )

# Кнопки выбора запросов по чемпионату
def competitions_choices(callback):
    league_name = callback.data.split('&')[1]
    data = f'&{league_name}'
    button = telebot.types.InlineKeyboardMarkup(row_width=1)

    button.add(
        telebot.types.InlineKeyboardButton(
            text='Таблица', callback_data='teams'+data))
    button.add(
        telebot.types.InlineKeyboardButton(
            text='Матчи', callback_data='matchday'+data))
    button.add(
        telebot.types.InlineKeyboardButton(
            text='Бомбардиры', callback_data='scorers'+data))
    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text='Выберите, что хотите посмотреть.',
        reply_markup=button
    )

# Выдает матчи актуального matchday
def matchday(callback) -> None:
    league_name = callback.data.split('&')[1]
    text = f'Матчи {league_name}\n\n'

    matches = LeagueMatches.objects.filter(name=league_name)
    button = telebot.types.InlineKeyboardMarkup(row_width=1)

    for f_match in matches:
        data = f'{f_match.current_match}&{league_name}&matchday'
        button_text = f'{f_match.current_match} '
        now = dt.utcnow().replace(tzinfo=UTC)
        if f_match.finished:
            if f_match.fulltime == 'None-None':
                button_text += '| Перенесен'
            else:
                button_text += f'| {f_match.fulltime}'
        else:
            if now >= f_match.date and now < f_match.date + td(hours=1, minutes=45):
                button_text += '| IN LIVE'
            else:
                user = callback.from_user.username
                timezone = User.objects.get(username=user).time_zone + 3
                date = datetime_to_text(f_match.date + td(hours=timezone))
                button_text += f'| {date}'

        button.add(
            telebot.types.InlineKeyboardButton(button_text, callback_data=data)
        )
    button.add(
            telebot.types.InlineKeyboardButton(
                text='<--------',
                callback_data=f'/competitions&{league_name}'))

    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=text,
        reply_markup=button
    )


# Выдает список команд лиги
def teams(callback) -> None:
    league_name = callback.data.split('&')[1]
    teams = Team.objects.filter(league=league_name)
    button = telebot.types.InlineKeyboardMarkup(row_width=1)
    text = (
        f'Команды {league_name}\n'+
        'О - очки, В - победы, Н - ничьи,\nП - поражения\n\n'
    )
    count = 1
    for team in teams:
        name = team.name
        points = team.points
        wins = team.total_wins
        draws = team.total_draws
        loses = team.total_loses

        data = f'{name}&{league_name}'

        button_text = f'{count}. {name} - {points} О | {wins} В | {draws} Н | {loses} П'
        button.add(
            telebot.types.InlineKeyboardButton(button_text, callback_data=data)
        )
        count += 1
    button.add(
            telebot.types.InlineKeyboardButton(
                text='<--------',
                callback_data=f'/competitions&{league_name}'))

    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=text,
        reply_markup=button
    )

# Выдает список бомбардиров лиги
def scorers(callback) -> None:
    league_name = callback.data.split('&')[1]
    players = Player.objects.filter(league=league_name)
    text = f'Бомбардиры {league_name}\nГ - голы(с пенальти) П - гол. пасы\nИ - игры\n\n'
    button = telebot.types.InlineKeyboardMarkup(row_width=1)
    for player in players:
        name = player.name
        goals = player.goals
        penalty = player.penalty
        assists = player.assists
        team = player.team
        matches = player.matches

        text += f'{name}({team})\n{goals}({penalty}) Г  {assists} П  |  {matches} И\n\n'
    button.add(
            telebot.types.InlineKeyboardButton(
                text='<--------',
                callback_data=f'/competitions&{league_name}'))

    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=text,
        reply_markup=button
    )

def stats(callback) -> None:
    print(callback.data)
    teams_list = callback.data.split('&')[0].split(' - ')
    text = 'Статистика за 10 матчей:\n\n'
    button = telebot.types.InlineKeyboardMarkup(row_width=1)
    print(callback.data)
    if len(teams_list) == 2:
        if callback.data.split('&')[2] == 'matchday':
            button.add(
                telebot.types.InlineKeyboardButton(
                    text='<--------',
                    callback_data=(
                        f'matchday&{callback.data.split('&')[1]}')))
        for team_name in teams_list:
            print(team_name)
            text += get_team_stats(team_name=team_name)
        f_match = LeagueMatches.objects.get(
            current_match=f'{teams_list[0]} - {teams_list[1]}')
        user = callback.from_user.username
        timezone = User.objects.get(username=user).time_zone + 3
        date = datetime_to_text(f_match.date + td(hours=timezone))
        text += get_teams_probability(teams=teams_list, date=date)
    elif len(teams_list) == 1:
        text += get_team_stats(team_name=teams_list[0])
        button.add(
            telebot.types.InlineKeyboardButton(
                text='<--------',
                callback_data=f'teams&{callback.data.split('&')[1]}'))

    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=text,
        reply_markup=button
    )

def get_team_stats(team_name: str) -> str:
    print(get_team_stats.__name__)
    position = Team.objects.get(name=team_name).position
    stats = Statistics.objects.get(name=team_name)
    text = f'{team_name} ({position} место)\n'
    text += f'Победы: {stats.wins}\n'
    text += f'Ничьи: {stats.draws}\n'
    text += f'Поражения: {stats.loses}\n'
    text += f'Форма: {stats.form[::-1]}\n'
    text += f'Форма дома: {stats.home_form[::-1]}\n'
    text += f'Форма в гостях: {stats.away_form[::-1]}\n'
    text += f'Голов забито: {stats.goals_scored}\n'
    text += f'Голов пропущено: {stats.goals_conceded}\n\n'

    return text


def get_teams_probability(teams: list, date: str) -> str:
    home_team = teams[0]
    away_team = teams[1]
    return MatchProbability(
        home_team=home_team, away_team=away_team
    ).print_result(date=date)



# Логика работы кнопок
@bot.callback_query_handler(func=lambda c:True)
def callback_inline(callback):
    command = callback.data.split('&')[0]
    league_name = callback.data.split('&')[1]

    check_updating(
        league_name=league_name,
        chat_id=callback.message.chat.id,
        message_id=callback.message.id
    )

    if command == '/competitions':
        is_updating = IsUpdating.objects.get(league_name=league_name)
        is_updating.is_updating = True
        is_updating.save()
        try:
            check = Checks(
                league_name=league_name,
                chat_id=callback.message.chat.id,
                message_id=callback.message.id
            )

            check.is_current_tour()
            check.is_matches_finished()
        except:
            pass
        is_updating.is_updating = False
        is_updating.save()


    if command == '/competitions':
        competitions_choices(callback)
    elif command == '/matches':
        matches(callback)
    elif command == 'matchday':
        matchday(callback)
    elif command == 'teams':
        teams(callback)
    elif command == 'scorers':
        scorers(callback)
    else:
        stats(callback)
