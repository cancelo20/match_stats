import os

from telebot import TeleBot

from datetime import (
    datetime as dt, timedelta as td)
from time import sleep
from pytz import UTC

from .models import LeagueMatches
from .updates import AfterMatchdayUpdate, AfterMatchUpdate


TG_TOKEN = str(os.getenv('TG_TOKEN'))
bot = TeleBot(TG_TOKEN)


class Checks:
    def __init__(self,
                 league_name: str,
                 chat_id: int = 0,
                 message_id: int = 0
                ) -> None:
        self.league_name = league_name
        self.chat_id = chat_id
        self.message_id = message_id

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text='Проверка обновлений, пожалуйста, подождите...',
        )

    def is_current_tour(self) -> None:
        print(self.is_current_tour.__name__)
        try:
            last_match_date = LeagueMatches.objects.filter(
                name=self.league_name).order_by('-date')[0].date
        except:
            # список не создан
            update = AfterMatchdayUpdate(league_name=self.league_name)
            update.matchday_update_all()
            print('Тур был не создан')
        else:
            # обновить список
            if dt.utcnow().replace(tzinfo=UTC) > last_match_date + td(days=1):
                update = AfterMatchdayUpdate(league_name=self.league_name)
                update.matchday_update_all()
                print('Тур обновлен')
            else:
                # не обновлять список
                print('Тур актуален')


    def is_matches_finished(self) -> None:
        print(self.is_matches_finished.__name__)
        now = dt.utcnow().replace(tzinfo=UTC)

        not_finished_matches = LeagueMatches.objects.filter(name=self.league_name)
        matches_list = list()

        try:
            for f_match in not_finished_matches:
                break
        except Exception:
            print('Нет списка матчей')
            bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self.message_id,
                text='Матчи отсутсвуют.'
            )
        else:
            for f_match in not_finished_matches:
                if f_match.finished:
                    continue
                if now >= f_match.date + td(hours=1, minutes=45) and not f_match.finished:
                    matches_list.append(f_match.current_match)

        if matches_list:
            AfterMatchUpdate(
                league_name=self.league_name,
                matches_list=matches_list
            ).matches_full_update()
            for match in matches_list:
                if LeagueMatches.objects.get(current_match=match).fulltime:
                    league_match = LeagueMatches.objects.get(current_match=match)
                    league_match.finished = True
                    league_match.save()
