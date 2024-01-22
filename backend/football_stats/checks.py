import os

from telebot import TeleBot

from datetime import (
    datetime as dt, timedelta as td)
from time import sleep
from pytz import UTC

from .models import League, LeagueMatches, IsUpdating
from .updates import AfterMatchdayUpdate, AfterMatchUpdate


TG_TOKEN = str(os.getenv('TG_TOKEN'))
bot = TeleBot(TG_TOKEN)


class Checks:
    def __init__(
            self,
            league_name: str,
            chat_id: int = 0,
            message_id: int = 0
    ) -> None:
        self.league_name = league_name
        self.chat_id = chat_id
        self.message_id = message_id

    # Проверяет актуальность тура
    def is_current_tour(self) -> None:
        print(self.is_current_tour.__name__)
        try:
            last_match_date = League.objects.get(
                name=self.league_name).end_date
        except Exception:
            # список не создан
            update = AfterMatchdayUpdate(league_name=self.league_name)
            update.matchday_update_all()
            print('Тур был не создан')
        else:
            # обновить список
            if dt.utcnow().replace(tzinfo=UTC) > last_match_date + td(hours=3):
                update = AfterMatchdayUpdate(league_name=self.league_name)
                update.matchday_update_all()
                print('Тур обновлен')
            else:
                # не обновлять список
                print('Тур актуален')

    # Проверяет на завершенность матчей
    def is_matches_finished(self) -> None:
        print(self.is_matches_finished.__name__)
        now = dt.utcnow().replace(tzinfo=UTC)
        not_finished_matches = LeagueMatches.objects.filter(
            name=self.league_name
        )
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
                if now >= f_match.date + td(hours=1, minutes=45) and (
                    not f_match.finished
                ):
                    matches_list.append(f_match.current_match)

        if matches_list:
            AfterMatchUpdate(
                league_name=self.league_name,
                matches_list=matches_list
            ).matches_full_update()

    def check_is_updating(self) -> None:
        print(self.check_is_updating.__name__)
        if IsUpdating.objects.get(
            league_name=self.league_name
        ).is_updating is True:
            while True:
                if IsUpdating.objects.get(
                    league_name=self.league_name
                ).is_updating is False:
                    break
                sleep(5)



    # Проверка обновлений
    def check_updates(self) -> None:
        print(self.check_updates.__name__)
        is_updating = IsUpdating.objects.get(league_name=self.league_name)
        is_updating.is_updating = True
        is_updating.save()

        self.is_current_tour()
        self.is_matches_finished()

        is_updating.is_updating = False
        is_updating.save()
