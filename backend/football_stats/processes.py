import os
import telebot
import requests

from pytz import UTC
from time import sleep
from dotenv import load_dotenv
from datetime import datetime as dt, timedelta as td

from user.models import Subscriptions
from football_stats.responses import count_requests_check
from football_stats.responses import HEADERS
from football_stats.checks import Checks
from football_stats.models import(
    LeagueMatches,
    League,
    Team
)


load_dotenv()


TG_TOKEN = str(os.getenv('TG_TOKEN'))
bot = telebot.TeleBot(TG_TOKEN)


def runlive():
    while True:
        try:
            matches = LeagueMatches.objects.all()
            for f_match in matches:
                if f_match.finished:
                    continue

                if dt.utcnow().replace(tzinfo=UTC) >= (
                    f_match.date
                ):
                    print(f'{f_match.current_match}: {f_match.fulltime}')
                    home_team = f_match.current_match.split(' - ')[0]
                    team_id = Team.objects.get(name=home_team).url_id
                    date = dt.utcnow().date()
                    url = (
                        f'{os.getenv("TEAMS_URL")}' +
                        f'/{team_id}/matches?' +
                        f'dateFrom={date}&dateTo={date}'
                    )
                    response = requests.get(
                        url=url, headers=HEADERS
                    ).json()
                    count_requests_check()
                    match = LeagueMatches.objects.get(
                        current_match__istartswith=home_team
                    )
                    status = response.get('matches')[0].get('status')

                    if status == 'IN_PLAY':
                        home_goals = response.get('matches')[0].get(
                            'score').get('fullTime').get('home')
                        away_goals = response.get('matches')[0].get(
                            'score').get('fullTime').get('away')
                        if home_goals is None and away_goals is None:
                            home_goals = 0
                            away_goals = 0
                        match.fulltime = (
                            f'IN LIVE {home_goals} - {away_goals}'
                        )
                        match.save()

                        subscriptions = Subscriptions.filter(
                            f_match=match
                        )
                        for subscription in subscriptions:
                            if subscriptions.is_send_message:
                                updated_match = LeagueMatches.objects.get(
                                    current_match__istartswith=home_team
                                )
                                if match.fulltime != updated_match.fulltime:
                                    bot.send_message(
                                        chat_id=subscription.user.chat_id,
                                        text=(
                                            'Гол!!! Счет в матче ' +
                                            f'{updated_match.current_match}: ' +
                                            f'{updated_match.fulltime}')
                                    )
                            else:
                                bot.send_message(
                                    chat_id=subscription.user.chat_id,
                                    text=f'Матч {match.current_match} начался!'
                                )
                                subscription.is_send_message = True
                                subscription.save()
                    else:
                        continue

                    sleep(10)
        except Exception:
            continue
        finally:
            print('CHECKING IN LIVE---------')
            sleep(10)


def runupdates():
    while True:
        try:
            matches = LeagueMatches.objects.all()
            leagues = League.objects.all()

            for f_match in matches:
                if dt.utcnow().replace(tzinfo=UTC) > (
                    f_match.date + td(hours=1, minutes=45)
                ) and not f_match.finished:
                    print('Обновление матчей')
                    Checks(league_name=f_match.name).is_matches_finished()

            for league in leagues:
                if dt.utcnow().replace(tzinfo=UTC) > (
                    league.end_date + td(hours=3)
                ):
                    print('Обновление тура')
                    Checks(league_name=league.name).is_current_tour()
        except Exception:
                continue
        finally:
            print('CHECKING UPDATES---------')
            sleep(60)
