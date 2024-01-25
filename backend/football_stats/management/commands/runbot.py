import os
import telebot

from threading import Thread
from dotenv import load_dotenv
from datetime import timedelta as td
from django.core.management import BaseCommand
from user.models import User, Subscriptions
from football_stats.processes import runlive, runupdates
from football_stats.updates import (
    datetime_to_text,
    get_team_stats,
    get_teams_probability
)
from football_stats.models import (
    LeagueMatches,
    League,
    Player,
    Team
)


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
                        'id в Телеграме: @EPLStatsBot' +
                        '(https://t.me/EPLStatsBot)\n' +
                        '_' * 54
                    )
                    Thread(target=runlive, daemon=True).start()
                    Thread(target=runupdates, daemon=True).start()
                    bot.polling(non_stop=True)
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
        except Exception:
            continue


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
        User.objects.create(
            username=username,
            chat_id=message.chat.id)

    del_last_msg(message.chat.id, message.message_id)
    bot.send_message(
        message.chat.id, text
    )


# обработка команды /clear
@bot.message_handler(commands=['clear'])
def clear(message) -> None:
    chat_id = message.chat.id
    message_id = message.message_id

    try:
        number = int(message.text.split(' ')[1])
    except Exception:
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
    except Exception:
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
        except Exception:
            bot.send_message(
                chat_id=message.chat.id,
                text='Вы ввели слишком большое число, попробуйте заново')
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text='Часовой пояс обновлен')


# Выдает список из 5 матчей на странице
def matches_page(
        chat_id: int,
        user: str,
        message_id: int = int(),
        page: int = 1
):
    matches_count = len(matches_list)
    button = telebot.types.InlineKeyboardMarkup(row_width=1)
    second_page_range = page * 5
    first_page_range = second_page_range - 5

    for match in matches_list[first_page_range:second_page_range]:
        f_match = LeagueMatches.objects.get(current_match=match)
        league = League.objects.get(name=f_match.name)
        button_text = f'{f_match.current_match} {league.country} '
        data = f'{f_match.current_match}&{f_match.name}&matches&{page}'

        if f_match.fulltime:
            button_text += f'| {f_match.fulltime}'
        else:
            timezone = User.objects.get(username=user).time_zone + 3
            button_text += f'| {datetime_to_text(
                f_match.date + td(hours=timezone))}'

        button.add(
            telebot.types.InlineKeyboardButton(button_text, callback_data=data)
        )

    if (matches_count // 5 + (matches_count % 5 != 0)) > page:
        button.add(
                telebot.types.InlineKeyboardButton(
                    text='-------->',
                    callback_data=f'matches&{page}&next'))

    if page > 1:
        button.add(
                telebot.types.InlineKeyboardButton(
                    text='<--------',
                    callback_data=f'matches&{page}&previous'))

    if len(matches_list) != 0:
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f'Ближайшие матчи ({matches_count} матчей)',
                reply_markup=button
            )
        except Exception:
            bot.send_message(
                chat_id=chat_id,
                text=f'Ближайшие матчи ({matches_count} матчей)',
                reply_markup=button
            )
    else:
        bot.send_message(
            chat_id=chat_id,
            text='Сегодня нет матчей'
        )


matches_list = list()


# Обработка команды /matches
@bot.message_handler(commands=['matches'])
def matches(message) -> None:
    matches_list.clear()
    del_last_msg(message.chat.id, message.message_id)

    matches = LeagueMatches.objects.all().order_by('date')
    date = None

    for f_match in matches:
        if f_match.finished:
            continue

        date = f_match.date.date()
        break

    for f_match in matches:
        if str(f_match.date).startswith(str(date)):
            matches_list.append(f_match.current_match)

    matches_page(
        chat_id=message.chat.id,
        user=message.from_user.username,
        message_id=message.message_id+1
    )


# Обработка команды /competitions
@bot.message_handler(commands=['competitions'])
def league_choosing_cmd(message) -> None:
    del_last_msg(message.chat.id, message.message_id)
    button = telebot.types.InlineKeyboardMarkup(row_width=1)
    command = 'competitions'
    leagues = League.objects.all()

    for league in leagues:
        league_name = league.name
        country = league.country
        text = f'{league_name} {country}'
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
            text='Таблица', callback_data='teams'+data
        )
    )
    button.add(
        telebot.types.InlineKeyboardButton(
            text='Матчи', callback_data='matchday'+data
        )
    )
    button.add(
        telebot.types.InlineKeyboardButton(
            text='Бомбардиры', callback_data='scorers'+data
        )
    )
    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text='Выберите, что хотите посмотреть.',
        reply_markup=button
    )


# Выдает матчи актуального matchday
def matchday(callback) -> None:
    league_name = callback.data.split('&')[1]
    league = League.objects.get(name=league_name)
    text = f'Матчи {league_name} {league.country}\n\n'
    matches = LeagueMatches.objects.filter(name=league_name)
    button = telebot.types.InlineKeyboardMarkup(row_width=1)

    for f_match in matches:
        data = f'{f_match.current_match}&{league_name}&matchday'
        button_text = f'{f_match.current_match} '

        if f_match.fulltime:
            button_text += f'| {f_match.fulltime}'
        else:
            timezone = User.objects.get(
                username=callback.from_user.username).time_zone + 3
            button_text += f'| {datetime_to_text(
                f_match.date + td(hours=timezone))}'

        button.add(
            telebot.types.InlineKeyboardButton(
                button_text, callback_data=data
            )
        )
    button.add(
        telebot.types.InlineKeyboardButton(
            text='<--------',
            callback_data=f'competitions&{league_name}'
        )
    )

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
        f'Команды {league_name}\n' +
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

        button_text = (
            f'{count}. {name} - ' +
            f'{points} О | {wins} В | {draws} Н | {loses} П'
        )
        button.add(
            telebot.types.InlineKeyboardButton(button_text, callback_data=data)
        )
        count += 1

    button.add(
        telebot.types.InlineKeyboardButton(
            text='<--------',
            callback_data=f'competitions&{league_name}'
        )
    )

    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=text,
        reply_markup=button
    )


# Выдает список бомбардиров лиги
def scorers(callback) -> None:
    league_name = callback.data.split('&')[1]
    league = League.objects.get(name=league_name)
    players = Player.objects.filter(league=league_name)
    text = (
        f'Бомбардиры {league_name} {league.country}\n' +
        'Г - голы(с пенальти) П - гол. пасы\nИ - игры\n\n'
    )
    button = telebot.types.InlineKeyboardMarkup(row_width=1)

    for player in players:
        name = player.name
        goals = player.goals
        penalty = player.penalty
        assists = player.assists
        team = player.team
        matches = player.matches
        text += (
            f'{name} ({team})\n{goals}({penalty}) Г  ' +
            f'{assists} П  |  {matches} И\n\n'
        )

    button.add(
        telebot.types.InlineKeyboardButton(
            text='<--------',
            callback_data=f'competitions&{league_name}'
        )
    )

    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=text,
        reply_markup=button
    )


# Выдает статистику за последние 10 матчей
def stats(callback) -> None:
    teams_list = callback.data.split('&')[0].split(' - ')
    text = 'Статистика за 10 матчей:\n\n'
    button = telebot.types.InlineKeyboardMarkup(row_width=1)

    if len(teams_list) == 2:
        command = callback.data.split('&')[2]
        user = User.objects.get(
            username=callback.from_user.username)
        match = LeagueMatches.objects.get(
            current_match=f'{teams_list[0]} - {teams_list[1]}')

        if not Subscriptions.objects.filter(
            user=user, f_match=match
        ).exists():
            button_text = 'Подписаться ✅'
            button_command = 'subscribe'
        else:
            button_text = 'Отписаться ❌'
            button_command = 'unsubscribe'
        if not match.finished:
            button.add(telebot.types.InlineKeyboardButton(
                text=button_text,
                callback_data=(
                    f'{button_command}&{teams_list[0]} - {teams_list[1]}'
            )))

        if command == 'matchday':
            button.add(
                telebot.types.InlineKeyboardButton(
                    text='<--------',
                    callback_data=(
                        f'{command}&{callback.data.split('&')[1]}')))
        elif command == 'matches':
            page = callback.data.split('&')[3]
            button.add(
                telebot.types.InlineKeyboardButton(
                    text='<--------',
                    callback_data=(
                        f'{command}&{page}&same_page')))

        for team_name in teams_list:
            text += get_team_stats(team_name=team_name)
        f_match = LeagueMatches.objects.get(
            current_match=f'{teams_list[0]} - {teams_list[1]}')
        timezone = user.time_zone + 3
        date = datetime_to_text(f_match.date + td(hours=timezone))
        text += get_teams_probability(teams=teams_list, date=date)
    elif len(teams_list) == 1:
        text += get_team_stats(team_name=teams_list[0])
        button.add(
            telebot.types.InlineKeyboardButton(
                text='<--------',
                callback_data=f'teams&{callback.data.split('&')[1]}'
            )
        )

    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=text,
        reply_markup=button
    )


# Оформление подписки на матч
def subscribe(callback):
    user = User.objects.get(
        username=callback.from_user.username)
    match = LeagueMatches.objects.get(
        current_match=callback.data.split('&')[1]
    )
    Subscriptions.objects.get_or_create(
        user=user, f_match=match
    )
    button = telebot.types.InlineKeyboardMarkup(row_width=1)
    button.add(
        telebot.types.InlineKeyboardButton(
            text='Готово! 👍',
            callback_data='None&None')
    )
    button.add(callback.message.reply_markup.keyboard[1][0])
    bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        reply_markup=button
    )


# Оформление отписки от матча
def unsubscribe(callback):
    user = User.objects.get(
        username=callback.from_user.username)
    match = LeagueMatches.objects.get(
        current_match=callback.data.split('&')[1]
    )
    Subscriptions.objects.get(
        user=user, f_match=match
    ).delete()
    button = telebot.types.InlineKeyboardMarkup(row_width=1)
    button.add(
        telebot.types.InlineKeyboardButton(
            text='Готово! 👍',
            callback_data='None&None')
    )
    button.add(callback.message.reply_markup.keyboard[1][0])
    bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        reply_markup=button
    )


# Логика работы кнопок
@bot.callback_query_handler(func=lambda c: True)
def callback_inline(callback):
    command = callback.data.split('&')[0]
    data = callback.data.split('&')[1]

    if command == 'competitions':
        competitions_choices(callback)
    elif command == 'matches':
        if callback.data.split('&')[2] == 'next':
            page = int(data) + 1
        elif callback.data.split('&')[2] == 'previous':
            page = int(data) - 1
        else:
            page = int(data)

        matches_page(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            user=callback.from_user.username,
            page=page)
    elif command == 'matchday':
        matchday(callback)
    elif command == 'teams':
        teams(callback)
    elif command == 'scorers':
        scorers(callback)
    elif command == 'subscribe':
        subscribe(callback)
    elif command == 'unsubscribe':
        unsubscribe(callback)
    else:
        if command != 'None':
            stats(callback)
