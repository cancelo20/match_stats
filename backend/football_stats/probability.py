class MatchProbability:
    def __init__(self, home_team, away_team):
        self.home_team = home_team
        self.away_team = away_team
        self.team1_name = self.home_team.get('name')
        self.team2_name = self.away_team.get('name')

    # Возвращает процент исхода каждого события
    def win_probability(self):
        NUMBER_OF_MATCHES = 20

        team1_win_probability = int((
            self.home_team['wins'] + self.away_team['loses']) / NUMBER_OF_MATCHES * 100)
        team2_win_probability = int((
            self.away_team['wins'] + self.home_team['loses']) / NUMBER_OF_MATCHES * 100)
        draw_probability = int((
            self.home_team['draws'] + self.away_team['draws']) / NUMBER_OF_MATCHES * 100)

        return team1_win_probability, team2_win_probability, draw_probability

    #Возвращает среднее количество голов за 10 матчей
    def score_average(self):
        NUMBER_OF_MATCHES = 10

        team1_goals = self.home_team.get('goals')
        team2_goals = self.away_team.get('goals')

        team1_average = team1_goals / NUMBER_OF_MATCHES
        team2_average = team2_goals / NUMBER_OF_MATCHES

        return team1_average, team2_average

    # Возвращает строку с текстом расчетов
    def print_result(self):
        win_probability = self.win_probability()
        score_average = self.score_average()

        return (
            f'{self.__str__()}\n\n' +
            'Вероятность исхода:\n' +
            f'   Победа {self.team1_name}: {win_probability[0]}%\n' +
            f'   Ничья: {win_probability[2]}%\n' +
            f'   Победа {self.team2_name}: {win_probability[1]}%\n\n' +
            'Средннее количество голов:\n' +
            f'   {self.team1_name}: {score_average[0]}\n' +
            f'   {self.team2_name}: {score_average[1]}\n'
        )

    def __str__(self):
        return f'{self.team1_name} vs {self.team2_name}'
