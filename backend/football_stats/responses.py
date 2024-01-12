import os
import requests

from time import sleep
from dotenv import load_dotenv
from datetime import date

from .models import Team


load_dotenv()


class TeamResponse:
    def __init__(self, team_id=None, league_code=None):
        self.team_id = team_id
        self.league_code = league_code

        self.HEADERS = {
            'X-Auth-Token': str(os.getenv('API_TOKEN'))
        }

    # Выдает список команд в заданной лиге
    def get_teams_response(self):
        url = f'{os.getenv("LEAGUES_URL")}/{self.league_code}/teams/'
        teams_list = list()
        try:
            response = requests.get(url=url, headers=self.HEADERS).json()
            teams = response.get('teams')
        except:
            assert False, 'get_team(): ошибка в response.'
        else:
            for team in teams:
                name = team.get('shortName')
                team_id = int(team.get('id'))
                short_name = team.get('tla')
                league_name = response.get('competition').get('name')
                matches_response = self.get_team_matches_response(team_id)
                matches_played = int(matches_response.get('resultSet').get('played'))
                teams_list.append([
                    name, team_id, short_name,
                    league_name, matches_played,
                ])
                print(name)
                sleep(6.1)

        return teams_list

    # Выдает response 10 матчей заданной команды
    def get_team_matches_response(self, team_id=None):
        if team_id == None:
            team_id = self.team_id

        current_data = date.today()
        url = f'{os.getenv("TEAMS_URL")}/{team_id}/matches?dateFrom=2023-07-01&dateTo={current_data}&limit=20'
        response = requests.get(url=url, headers=self.HEADERS).json()

        print(
            response.get('message')
        ) if 'message' in response.keys() else ...

        return response

    # Выдает response матчей актуального игрового дня
    def get_matchday_response(self):
        league_url = f'{os.getenv("LEAGUES_URL")}/{self.league_code}/'
        league_response = requests.get(league_url, headers=self.HEADERS).json()
        current_matchday = league_response.get('currentSeason').get('currentMatchday')

        matchday_url = league_url + f'matches?matchday={current_matchday}'
        matchday_response = requests.get(url=matchday_url, headers=self.HEADERS).json()

        print(
            league_response.get('message')
        ) if 'message' in league_response.keys() else ...

        return matchday_response


class TeamStats:
    def __init__(self, team_id, league_code=None):
        self.team_id = team_id
        self.league_code = league_code

        self.team_data = {
            'wins': 0,
            'draws': 0,
            'loses': 0,
            'home_wins': 0,
            'home_loses': 0,
            'home_draws': 0,
            'away_wins': 0,
            'away_loses': 0,
            'away_draws': 0,
            'form': '',
            'home_form': '',
            'away_form': '',
            'goals': 0,
        }

    # Выдает response результат 10 матчей заданной команды
    def matches_results(self):
        GREEN_EMOJI = '\U0001F7E2'
        RED_EMOJI = '\U0001F534'
        ORANGE_EMOJI = '\U0001F7E0'

        response = TeamResponse(self.team_id).get_team_matches_response()
        shortname = Team.objects.get(url_id=self.team_id).shortname
        matches = response.get('matches')[::-1]
        home_away_team = None
        team = self.team_data

        matches_count = 0
        for match in matches:
            if matches_count == 10:
                break

            home_away_team = 'home' if match.get('homeTeam').get('tla') == shortname else 'away'
            results = match.get('score')

            try:
                result = results.get('winner').startswith(home_away_team.upper())
            except:
                continue

            if result == 'null':
                continue

            if results.get('winner').startswith(home_away_team.upper()):
                team['wins'] += 1
                team['form'] += GREEN_EMOJI
                team[f'{home_away_team}_form'] += GREEN_EMOJI
                team[f'{home_away_team}_wins'] += 1
            elif results.get('winner') == 'DRAW':
                team['draws'] += 1
                team['form'] += ORANGE_EMOJI
                team[f'{home_away_team}_form'] += ORANGE_EMOJI
                team[f'{home_away_team}_draws'] += 1
            else:
                team['loses'] += 1
                team['form'] += RED_EMOJI
                team[f'{home_away_team}_form'] += RED_EMOJI
                team[f'{home_away_team}_loses'] += 1

            matches_count +=1
            team['goals'] += results.get('fullTime').get(home_away_team)

        return team
