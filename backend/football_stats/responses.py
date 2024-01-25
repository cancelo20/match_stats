import os
import requests
import logging

from logging.handlers import RotatingFileHandler
from datetime import date, datetime as dt, timedelta as td
from dotenv import load_dotenv
from time import sleep
from pytz import UTC
from .models import League, Team, Requests


load_dotenv()


from logging.handlers import RotatingFileHandler

# Здесь задана глобальная конфигурация для всех логгеров
logging.basicConfig(
    level=logging.DEBUG,
    filename='responses.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
handler = RotatingFileHandler('responses.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

HEADERS = {
    'X-Auth-Token': f'{os.getenv("API_TOKEN")}'
}


def count_requests_check() -> None:
    object = Requests.objects.get(id=1)
    if dt.utcnow().replace(tzinfo=UTC) >= (
        object.last_update_date + td(minutes=1, milliseconds=1)
    ):
        object.count = 1
        object.last_update_date = dt.utcnow().replace(tzinfo=UTC)
        object.save()
        return

    object = Requests.objects.get(id=1)
    object.count += 1
    object.save()

    if dt.utcnow().replace(tzinfo=UTC) < (
        object.last_update_date + td(minutes=1, milliseconds=1)) and (
            object.count >= 10
    ):
        sleeping_time = (
            object.last_update_date + td(
                minutes=1, milliseconds=1) - dt.utcnow().replace(tzinfo=UTC)
            ).seconds
        object.count = 0
        object.save()
        sleep(sleeping_time)


class LeagueResponse:
    def __init__(self, league: League = League()) -> None:
        self.league = league

        league_code = self.league.league_code
        self.league_url = f'{os.getenv("LEAGUES_URL")}/{league_code}/'

    def current_matchday_number(self) -> int:
        response = requests.get(
            url=self.league_url, headers=HEADERS).json()

        count_requests_check()

        try:
            current_matchday = int(
                response.get('currentSeason').get('currentMatchday')
            )
        except TypeError as error:
            logger.error(
                f'{error} in {self.current_matchday_number.__name__}',
                exc_info=True
            )
        else:
            return current_matchday

    def matchday_response(self) -> dict:
        matchday_number = League.objects.get(
            name=self.league.name).current_matchday
        url = self.league_url + f'matches?matchday={matchday_number}'
        response = requests.get(url=url, headers=HEADERS)

        count_requests_check()

        return response.json()

    def top_scorers_response(self) -> dict:
        url = self.league_url + 'scorers'
        response = requests.get(url=url, headers=HEADERS).json()

        count_requests_check()

        return response

    def standing_response(self) -> dict:
        url = self.league_url + 'standings'
        response = requests.get(url=url, headers=HEADERS).json()

        count_requests_check()

        try:
            standings = response.get('standings')[0]
        except TypeError as error:
            logger.error(
                f'{error} in {self.standing_response.__name__}',
                exc_info=True
            )
        else:
            return standings

    def league_teams_response(self) -> dict:
        url = self.league_url + '/teams'
        response = requests.get(url=url, headers=HEADERS).json()

        count_requests_check()

        try:
            teams = response.get('teams')
        except TypeError as error:
            logger.error(
                f'{error} in {self.league_teams_response.__name__}',
                exc_info=True
            )
        else:
            return teams


class TeamResponse(LeagueResponse):
    def __init__(self, team_name: str) -> None:

        self.team = Team.objects.get(name=team_name)
        self.team_matches_url = f'{os.getenv("TEAMS_URL")}'

    def last_10_team_matches(self) -> dict:
        current_date = date.today()
        url = self.team_matches_url + (
            f'/{self.team.url_id}' +
            f'/matches?dateFrom=2023-07-01&dateTo={current_date}&limit=20')
        response = requests.get(url=url, headers=HEADERS).json()

        count_requests_check()

        try:
            matches = response.get('matches')[::-1]
        except TypeError as error:
            logger.error(
                f'{error} in {self.last_10_team_matches.__name__}',
                exc_info=True
            )
        else:
            return matches
