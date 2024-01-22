from pytz import UTC
from datetime import datetime as dt

from .models import (
    LeagueMatches,
    Statistics,
    League,
    Player,
    Team
)
from .responses import (
    LeagueResponse, TeamResponse)


def from_response_time_to_datetime(response_time) -> dt:
    date_time = response_time.split('T')
    date = date_time[0].split('-')
    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    time = date_time[1].split(':')
    hour = int(time[0])
    minute = int(time[1])

    return dt(year, month, day, hour, minute, tzinfo=UTC)


class AfterUpdate:
    def __init__(
            self,
            league_name: str) -> None:
        self.league = League.objects.get(name=league_name)
        self.league_response = LeagueResponse(
            league=self.league)


class AfterMatchdayUpdate(AfterUpdate):
    # выполняет все функции класса
    def matchday_update_all(self) -> None:
        print(self.matchday_update_all.__name__)
        self.matchday_number_update()
        self.matchday_matches_update()
        self.matchday_start_end_date_update()
        self.team_points_full_update()
        updated_matches = LeagueMatches.objects.filter(name=self.league.name)

        for f_match in updated_matches:
            teams = f_match.current_match.split(' - ')
            for team in teams:
                self.team_stats_update(team_name=team)

    # обновляет матчи предстоящего тура
    def matchday_matches_update(self) -> None:
        print(self.matchday_matches_update.__name__)
        LeagueMatches.objects.filter(name=self.league.name).delete()

        matches = self.league_response.matchday_response().get('matches')
        for match in matches:
            home_team = match.get('homeTeam').get('shortName')
            away_team = match.get('awayTeam').get('shortName')
            league_name = self.league.name
            date = from_response_time_to_datetime(match.get('utcDate'))

            LeagueMatches.objects.create(
                current_match=f'{home_team} - {away_team}',
                name=league_name,
                date=date
            )

    # обновляет номер matchday
    def matchday_number_update(self) -> None:
        print(self.matchday_number_update.__name__)
        matchday_number = int(
            self.league_response.current_matchday_number())

        if dt.utcnow().replace(tzinfo=UTC) > self.league.end_date:
            self.league.current_matchday = matchday_number + 1
            self.league.save()

    # обновляет дату начала и окончания тура
    def matchday_start_end_date_update(self) -> None:
        print(self.matchday_start_end_date_update.__name__)
        start_date = LeagueMatches.objects.filter(
            name=self.league.name)[0].date
        end_date = LeagueMatches.objects.filter(
             name=self.league.name).order_by('-date')[0].date

        self.league.start_date = start_date
        self.league.end_date = end_date
        self.league.save()

    # обновляет статистику 10 последних игр
    def team_stats_update(self, team_name) -> None:
        print(f'{self.team_stats_update.__name__} - {team_name}')

        GREEN_EMOJI = '\U0001F7E2'
        RED_EMOJI = '\U0001F534'
        ORANGE_EMOJI = '\U0001F7E0'

        Statistics.objects.filter(name=team_name).delete()
        matches = TeamResponse(team_name=team_name).last_10_team_matches()
        stats = Statistics.objects.create(name=team_name)

        count = 0
        for match in matches:
            if count == 10:
                break

            is_home = False

            if match.get('competition').get('name') != self.league.name:
                continue

            if match.get('homeTeam').get('shortName') == team_name:
                home_away_team = 'HOME'
                is_home = True
            else:
                home_away_team = 'AWAY'
            results = match.get('score')
            result = results.get('winner')

            if result is None:
                continue

            if is_home:
                stats.goals_scored += results.get('fullTime').get('home')
                stats.goals_conceded += results.get('fullTime').get('away')
            else:
                stats.goals_scored += results.get('fullTime').get('away')
                stats.goals_conceded += results.get('fullTime').get('home')

            if result.startswith(home_away_team):
                stats.wins += 1
                stats.form += GREEN_EMOJI
                if home_away_team == 'HOME':
                    stats.home_form += GREEN_EMOJI
                else:
                    stats.away_form += GREEN_EMOJI
            elif result == 'DRAW':
                stats.draws += 1
                stats.form += ORANGE_EMOJI
                if home_away_team == 'HOME':
                    stats.home_form += ORANGE_EMOJI
                else:
                    stats.away_form += ORANGE_EMOJI
            else:
                stats.loses += 1
                stats.form += RED_EMOJI
                if home_away_team == 'HOME':
                    stats.home_form += RED_EMOJI
                else:
                    stats.away_form += RED_EMOJI
            stats.save()
            count += 1


    # обновляет очки команды, победы, поражения, ничьи
    # обновляет api-запросом
    def team_points_full_update(self) -> None:
        print(self.team_points_full_update.__name__)
        teams = self.league_response.standing_response().get('table')

        for team in teams:

            name = team.get('team').get('shortName')
            position = team.get('position')
            points = team.get('points')
            wins = team.get('won')
            draws = team.get('draw')
            loses = team.get('lost')

            team_db = Team.objects.get(name=name)
            team_db.position = position
            team_db.points = points
            team_db.total_wins = wins
            team_db.total_draws = draws
            team_db.total_loses = loses
            team_db.save()


class AfterMatchUpdate(AfterUpdate):
    def __init__(
            self,
            league_name: str = str(),
            matches_list: list = list()) -> None:
        super().__init__(league_name)
        self.matches_list = matches_list

    def matches_full_update(self):
        self.matches_score_update()
        self.top_scorers_update()

    # обновляет счет матчей
    def matches_score_update(self) -> None:
        print(self.matches_score_update.__name__)
        matches = self.league_response.matchday_response().get('matches')
        home_teams = [match.split(' - ')[0] for match in self.matches_list]

        for f_match in matches:
            home_team = f_match.get('homeTeam').get('shortName')
            if home_team not in home_teams:
                continue

            status = f_match.get('status')

            if status == 'TIMED' or status == 'IN_PLAY':
                continue

            fulltime = f_match.get('score').get('fullTime')
            home_goals = fulltime.get('home')
            away_goals = fulltime.get('away')
            league_match = LeagueMatches.objects.get(
                current_match__istartswith=home_team)

            if status == 'POSTPONED':
                league_match.fulltime = 'Перенесен'
            elif status == 'FINISHED':
                league_match.fulltime = f'{home_goals} - {away_goals}'
            league_match.finished = True
            league_match.save()

    # обновляет список бомбардиров лиги
    def top_scorers_update(self) -> None:
        print(self.top_scorers_update.__name__)
        Player.objects.filter(league=self.league.name).delete()

        players = self.league_response.top_scorers_response().get('scorers')

        for player in players:
            name = player.get('player').get('name')
            league = self.league.name
            team = player.get('team').get('tla')
            goals = player.get('goals')
            penalty = player.get('penalties')
            assists = player.get('assists')
            matches = player.get('playedMatches')

            if penalty is None:
                penalty = 0
            if assists is None:
                assists = 0
            if goals is None:
                goals = 0
            if matches is None:
                matches = 0

            Player.objects.create(
                name=name,
                league=league,
                team=team,
                goals=goals,
                penalty=penalty,
                assists=assists,
                matches=matches
            )


class AfterSeasonUpdate(AfterUpdate):
    def league_teams_update(self):
        print(self.league_teams_update.__name__)
        teams = LeagueResponse(league=self.league).league_teams_response()
        Team.objects.filter(league=self.league.name).delete()

        for team in teams:
            name = team.get('shortName')
            shortname = team.get('tla')
            url_id = team.get('id')
            league = self.league.name

            Team.objects.create(
                name=name,
                shortname=shortname,
                url_id=url_id,
                league=league
            )


def datetime_to_text(datetime_type) -> str:
    date = str(datetime_type.date()).split('-')
    time = str(datetime_type.time()).split(':')
    month = date[1]
    day = date[2]
    hour = time[0]
    minutes = time[1]

    return f'{day}.{month} {hour}:{minutes}'
