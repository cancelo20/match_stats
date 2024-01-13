from django.core.management import BaseCommand

from football_stats.responses import PlayerResponse
from football_stats.updates import TeamUpdate, LeagueMatchesUpdate
from football_stats.models import League
from football_stats.updates import PlayerUpdate

import datetime as dt

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "test bot"

    def handle(self, *args, **options):
        pass
        LeagueMatchesUpdate().fulltime_update(league_name='Premier League', home_team='Burnley')
