from time import sleep

from .models import League, LeagueMatches, Team, Statistics
from .responses import TeamResponse, TeamStats


class LeagueMatchesUpdate:
    def matchday_update(self, league_name):
        matches = LeagueMatches.objects.filter(name=league_name)
        matches.delete()

        league_code = League.objects.get(name=league_name).league_code

        current_matches = TeamResponse(
            league_code=league_code).get_matchday_response()

        for match in current_matches.get('matches'):
            home_team = match.get('homeTeam').get('shortName')
            away_team = match.get('awayTeam').get('shortName')

            LeagueMatches.objects.create(
                name=league_name,
                current_match=f'{home_team} - {away_team}'
            )


class LeagueUpdate:
    def matchday_update(self, league_code):

        league = League.objects.get(league_code=league_code)
        matchday_response = TeamResponse(
            league_code=league_code).get_matchday_response()
        current_matchday = matchday_response.get('filters').get('matchday')

        matches = matchday_response.get('matches')

        LeagueMatches.objects.filter(name=league.name).delete()

        for match in matches:
            home_team = match.get('homeTeam').get('shortName')
            away_team = match.get('awayTeam').get('shortName')

            LeagueMatches.objects.create(
                name=league.name,
                current_match=f'{home_team} - {away_team}'
            )

        league.current_matchday = int(current_matchday)
        league.save()

        matchday_end = matchday_response.get('resultSet').get('last')

        league.matchday_end_date = str(matchday_end)
        league.save()


class TeamUpdate:
    def team_results_update(self, league_name):
            stat_list = list()

            league = League.objects.get(name=league_name)
            teams = Team.objects.filter(league=league)

            POINTS_FOR_WIN = 3
            POINTS_FOR_DRAW = 1

            for team in teams:
                stats = TeamStats(team.url_id).matches_results()
                for stat in stats:
                    stat_list.append(stats[stat])

                (wins, draws, loses, home_wins,
                home_loses, home_draws, away_wins, away_loses,
                away_draws, form, home_form, away_form, goals) = stat_list
                points = wins * POINTS_FOR_WIN + draws * POINTS_FOR_DRAW

                print(stat_list, ' - ', points)

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
