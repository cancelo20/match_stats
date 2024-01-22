import os
import requests

from datetime import date, datetime as dt, timedelta as td
from dotenv import load_dotenv
from time import sleep
from pytz import UTC
from .models import League, Team, Requests


load_dotenv()


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
        print(f'REQUESTS - {object.count}')
        return

    object = Requests.objects.get(id=1)
    object.count += 1
    object.save()
    print(f'REQUESTS - {object.count}')

    if dt.utcnow().replace(tzinfo=UTC) < (
        object.last_update_date + td(minutes=1, milliseconds=1)) and (
            object.count >= 10
    ):
        sleeping_time = (
            object.last_update_date + td(
                minutes=1, milliseconds=1) - dt.utcnow().replace(tzinfo=UTC)
            ).seconds
        print(f'sleeped - {sleeping_time}')
        object.count = 0
        object.save()
        sleep(sleeping_time)


class LeagueResponse:
    def __init__(self, league: League = League()) -> None:
        self.league = league

        league_code = self.league.league_code
        self.league_url = f'{os.getenv("LEAGUES_URL")}/{league_code}/'

    def matchday_response(self) -> dict:
        print(self.matchday_response.__name__)
        league_response = requests.get(self.league_url, headers=HEADERS).json()

        count_requests_check()

        matchday_number = league_response.get('currentSeason').get(
            'currentMatchday'
        )
        url = self.league_url + f'matches?matchday={matchday_number}'
        response = requests.get(url=url, headers=HEADERS)

        count_requests_check()

        return response.json()

    def top_scorers_response(self) -> dict:
        print(self.top_scorers_response.__name__)
        url = self.league_url + 'scorers'
        response = requests.get(url=url, headers=HEADERS).json()

        count_requests_check()

        return response

    def standing_response(self) -> dict:
        print(self.standing_response.__name__)
        url = self.league_url + 'standings'
        response = requests.get(url=url, headers=HEADERS).json()

        count_requests_check()

        return response.get('standings')[0]

    def league_teams_response(self) -> dict:
        print(self.league_teams_response.__name__)
        url = self.league_url + '/teams'
        response = requests.get(url=url, headers=HEADERS).json()

        count_requests_check()

        return response.get('teams')


class TeamResponse(LeagueResponse):
    def __init__(self, team_name: str) -> None:

        self.team = Team.objects.get(name=team_name)
        self.team_matches_url = f'{os.getenv("TEAMS_URL")}'

    def last_10_team_matches(self) -> dict:
        print(self.last_10_team_matches.__name__)
        current_date = date.today()
        url = self.team_matches_url + (
            f'/{self.team.url_id}' +
            f'/matches?dateFrom=2023-07-01&dateTo={current_date}&limit=20')
        response = requests.get(url=url, headers=HEADERS).json()

        count_requests_check()

        return response.get('matches')[::-1]
