import datetime as dt

from time import sleep

from .models import (
    League, LeagueMatches, Team, Statistics, Player)
from .responses import TeamResponse, TeamStats, PlayerResponse


class LeagueMatchesUpdate:
    def __init__(self):
        ...
    # Обновляет список игр актуального тура
    def matchday_update(self, league_name):
        matches = LeagueMatches.objects.filter(name=league_name)
        matches.delete()

        league_code = League.objects.get(name=league_name).league_code

        current_matches = TeamResponse(
            league_code=league_code).get_matchday_response()

        for match in current_matches.get('matches'):
            date_time = match.get('utcDate').split('T')
            time = date_time[1].split(':')
            date = date_time[0].split('-')

            hours = int(time[0])
            minutes = int(time[1])
            day = int(date[2])
            month = int(date[1])
            year = int(date[0])

            match_time = self.get_moscow_date(year, month, day, hours, minutes)

            home_team = match.get('homeTeam').get('shortName')
            away_team = match.get('awayTeam').get('shortName')

            LeagueMatches.objects.create(
                name=league_name,
                current_match=(
                    f'{home_team} - {away_team}'),
                date=match_time
            )

    # Переводит времся с UTC-0 к Московскому
    def get_moscow_date(self, year, month, day, hours, minutes):
        MOSCOW_PERIOD = dt.timedelta(hours=3)

        current_moscow_date = str(dt.datetime(
            year, month, day, hours, minutes
            ) + MOSCOW_PERIOD).split(' ')
        print(current_moscow_date)

        date = current_moscow_date[0].split('-')
        time = current_moscow_date[1].split(':')

        return f'{date[2]}.{date[1]} {time[0]}:{time[1]}'

    # Выдает счет сыгранного матча
    def fulltime_update(self, league_name, home_team):
        league = League.objects.get(name=league_name)

        matches = TeamResponse(
            league_code=league.league_code).get_matchday_response(
            ).get('matches')

        home_goals = 0
        away_goals = 0

        for match in matches:
            if match.get('homeTeam').get('shortName') != home_team:
                continue

            fulltime = match.get('score').get('fullTime')
            home_goals = fulltime.get('home')
            away_goals = fulltime.get('away')

            break

        league_match = LeagueMatches.objects.filter(
            current_match__istartswith=home_team)[0]
        league_match.fulltime = f'{home_goals}-{away_goals}'
        league_match.finished = True
        league_match.save()



class LeagueUpdate:
    # Обновляет номер актуального тура и дату его завершения
    def matchday_update(self, league_code):
        league = League.objects.get(league_code=league_code)
        matchday_response = TeamResponse(
            league_code=league_code).get_matchday_response()
        current_matchday = matchday_response.get('filters').get('matchday')

        league.current_matchday = int(current_matchday)
        league.save()

        matchday_end = matchday_response.get('resultSet').get('last')

        league.matchday_end_date = str(matchday_end)
        league.save()


class TeamUpdate:
    # Обновляет статистику команд
    def team_results_update(self, league_name):
            stat_list = list()

            league = League.objects.get(name=league_name)
            teams = Team.objects.filter(league=league)

            for team in teams:
                stats = TeamStats(team.url_id).matches_results()
                for stat in stats:
                    stat_list.append(stats[stat])

                (wins, draws, loses, home_wins,
                home_loses, home_draws, away_wins, away_loses,
                away_draws, form, home_form, away_form, goals) = stat_list

                print(team.name, wins+draws+loses, stat_list)

                statistic = Statistics.objects.get(name=team.name)
                statistic.wins = wins
                statistic.draws = draws
                statistic.loses = loses
                statistic.home_wins = home_wins
                statistic.home_draws = home_draws
                statistic.home_loses = home_loses
                statistic.away_draws = away_draws
                statistic.away_wins = away_wins
                statistic.away_loses = away_loses
                statistic.form = form
                statistic.home_form = home_form
                statistic.away_form = away_form
                statistic.goals = goals
                statistic.save()

                stat_list = list()
                sleep(6.1)

    # Обновляет общее кол-во очков, побед, поражений, ничьиъ команды
    def team_points_update(self, league_name):
        league = League.objects.get(name=league_name)
        teams_points = TeamResponse(
            league_code=league.league_code).team_points()

        for team_point in teams_points:
            print(team_point)
            team = Team.objects.get(name=team_point.get('name'))

            team.total_wins = team_point.get('wins')
            team.total_draws = team_point.get('draws')
            team.total_loses = team_point.get('loses')
            team.points = team_point.get('points')
            team.save()


class PlayerUpdate:
    def __init__(self, league_code):
        self.league_code = league_code

    # Обновляет список бомбордиров лиги
    def players_update(self):
        scorers = PlayerResponse(self.league_code).get_top_scorers_league()
        league = League.objects.get(league_code=self.league_code)

        Player.objects.filter(league=league.name).delete()

        for scorer in scorers:
            name = scorer.get('player').get('name')
            player_league = league.name
            team = scorer.get('team').get('shortName')
            goals = scorer.get('goals')
            penalty = scorer.get('penalties')
            assists = scorer.get('assists')

            if goals is None:
                goals = 0
            if penalty is None:
                penalty = 0
            if assists is None:
                assists = 0

            print(name, goals, penalty, assists)

            Player.objects.create(
                name=name, league=player_league, team=team,
                goals=goals, penalty=penalty, assists=assists
            )
