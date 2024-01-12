import os
import telebot

from dotenv import load_dotenv
from leagues import (
    League
)
from football_stats.probability import MatchProbability


load_dotenv()


TG_TOKEN = str(os.getenv('TG_TOKEN'))
bot = telebot.TeleBot(TG_TOKEN)


leagues = {
    'PL': 'PremierLeague',
    'BL1': 'BundesLiga',
    'SA': 'SeriaA',
    'PD': 'LaLiga',
    'FL1': 'Ligue1',
}


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


@bot.message_handler(commands=['matchday', 'teams'])
def matchday_league(message):
    button = telebot.types.InlineKeyboardMarkup(row_width=1)

    command = message.text

    for league in leagues.keys():
        data = f'{league} & {command}'
        button.add(
            telebot.types.InlineKeyboardButton(leagues.get(league), callback_data=data)
        )

    bot.send_message(
        message.chat.id,
        'Выбери чемпионат:',
        reply_markup=button
    )


def matchday(callback):
    league_code = callback.data.split(' & ')[0]

    matches = list() # current_match_day from db <--------------------
    matches_list = []
    button = telebot.types.InlineKeyboardMarkup(row_width=1)

    for match in matches:
        home = match.get('homeTeam').get('shortName')
        away = match.get('awayTeam').get('shortName')
        text = f'{home} - {away}'

        data = f'{text} & {league_code}'

        button.add(
            telebot.types.InlineKeyboardButton(text, callback_data=data)
        )

        matches_list.append(button)

    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text='Матчи ближайшего тура:',
        reply_markup=button
    )


def teams(callback):
    leagues_code = callback.data.split(' & ')[0]
    teams = sorted([i for i in League(league_code=leagues_code).teams_league])
    text =''

    for team in teams:
        text += f'{team}\n'

    bot.send_message(
        callback.message.chat.id, text)


def get_result(text, league_code):
    team_name1, team_name2 = text.split(' - ')
    team1 = League(team_name=team_name1, league_code=league_code)
    team2 = League(team_name=team_name2, league_code=league_code)
    match = MatchProbability(team1.matches_results_count(), team2.matches_results_count())


    text_result = (
        'Статистика за последние 10 матчей:\n\n' +
        f'{team1.get_stats()}\n\n' +
        f'{team2.get_stats()}\n\n' +
        f'{match.print_result()}'
    )

    return text_result



def say_result(callback):
    data = callback.data.split(' & ')
    try:
        text = get_result(text=data[0], league_code=data[1])
    except:
         bot.send_message(
             callback.message.chat.id,
             'Что-то пошло не так, попробуйте позже.')
    else:
        bot.send_message(
            callback.message.chat.id, text)


@bot.callback_query_handler(func=lambda c:True)
def callback_inline(callback):
    data = callback.data.split(' & ')
    if data[1] == '/matchday':
        matchday(callback)
    elif data[1] == '/teams':
        teams(callback)
    else:
        say_result(callback)


def main():
    bot.polling()


if __name__ == '__main__':
    main()
