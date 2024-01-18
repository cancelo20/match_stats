from datetime import timedelta as td

from .models import LeagueMatches, Statistics
from .management.commands.runbot import datetime_to_text


class MatchProbability:
    def __init__(self, home_team: str, away_team: str) -> None:
        self.home_team = Statistics.objects.get(name=home_team)
        self.away_team = Statistics.objects.get(name=away_team)

    # Возвращает процент исхода каждого события
    def win_probability(self) -> tuple:
        print(self.win_probability.__name__)
        NUMBER_OF_MATCHES = 20

        team1_win_probability = int((
            self.home_team.wins + self.away_team.wins) / NUMBER_OF_MATCHES * 100)
        team2_win_probability = int((
            self.away_team.wins + self.home_team.wins) / NUMBER_OF_MATCHES * 100)
        draw_probability = int((
            self.home_team.draws + self.away_team.draws) / NUMBER_OF_MATCHES * 100)

        return team1_win_probability, team2_win_probability, draw_probability

    #Возвращает среднее количество голов за 10 матчей
    def score_average(self) -> tuple:
        print(self.score_average.__name__)
        NUMBER_OF_MATCHES = 10

        team1_goals = self.home_team.goals_scored
        team2_goals = self.away_team.goals_scored

        team1_conceded = self.home_team.goals_conceded
        team2_conceded = self.away_team.goals_conceded

        team1_average_scored = team1_goals / NUMBER_OF_MATCHES
        team2_average_scored = team2_goals / NUMBER_OF_MATCHES

        team1_average_conceded = team1_conceded / NUMBER_OF_MATCHES
        team2_average_conceded = team2_conceded / NUMBER_OF_MATCHES

        return (
            [team1_average_scored, team1_average_conceded],
            [team2_average_scored, team2_average_conceded]
        )

    # Возвращает строку с текстом расчетов
    def print_result(self):
        print(self.print_result.__name__)
        win_probability = self.win_probability()
        score_average = self.score_average()
        date = datetime_to_text(LeagueMatches.objects.get(
            current_match=f'{self.home_team.name} - {self.away_team.name}'
        ).date + td(hours=3))

        return (
            f'{self.__str__()}\n\n' +
            f'{date} МСК\n\n'
            'Вероятность исхода:\n' +
            f'   Победа {self.home_team.name}: {win_probability[0]}%\n' +
            f'   Ничья: {win_probability[2]}%\n' +
            f'   Победа {self.away_team.name}: {win_probability[1]}%\n\n' +
            'Среднее количество забитых-пропущенных голов:\n' +
            f'   {self.home_team.name}: {score_average[0][0]}-{score_average[0][1]}\n' +
            f'   {self.away_team.name}: {score_average[1][0]}-{score_average[1][1]}\n'
        )

    def __str__(self):
        return f'{self.home_team.name} vs {self.away_team.name}'
