import os
import requests
import telebot

from pytz import UTC
from time import sleep
from threading import Thread
from dotenv import load_dotenv
from datetime import datetime as dt
from django.core.management import BaseCommand
from football_stats.responses import count_requests_check
from football_stats.responses import HEADERS
from football_stats.models import (
    LeagueMatches,
    Team
)
from user.models import User, Subscriptions


load_dotenv()


TG_TOKEN = str(os.getenv('TG_TOKEN'))
bot = telebot.TeleBot(TG_TOKEN)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "IN LIVE"

    def handle(self, *args, **options):
        def run():
            matches = LeagueMatches.objects.all()
            while True:
                try:
                    for f_match in matches:
                        if f_match.finished:
                            continue

                        if dt.utcnow().replace(tzinfo=UTC) >= (
                            f_match.date
                        ):
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
                            print(f_match.current_match)
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
                except Exception as error:
                    print(error)
                    continue
                finally:
                    print('LIVE')
                    sleep(10)
        Thread(target=run, daemon=True).start()
        input('Press <Enter> to exit.\n')
