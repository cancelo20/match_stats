from .models import Team, League, Statistics


class TeamOperations:
    # Добавляет команду в базу даных
    def add_team(
            self,
            name,
            team_id,
            shortname,
            league_name,
            matches_played
        ):
        try:
            league_to_add = League.objects.get(name=league_name)
            stats = Statistics.objects.create(name=name)
            Team.objects.create(
                name=name, url_id=team_id, shortname=shortname,
                league=league_to_add, matches_played=matches_played,
                stats_last_10=stats
            )
        except:
            print('add_team(): неудалось добавить объекту в базу')

    # Удаляет команду из базы данных
    def del_team(self, team_id):
        try:
            Team.objects.filter(url_id=team_id).delete()
        except:
            print('del_team(): неудалось удать объект из базы')

    # Проверяет команду в базе данных
    def check_team(self, team_id):
        try:
            return Team.objects.filter(url_id=team_id).exists()
        except:
            print('check_team(): не удалось выполнить проверку')
