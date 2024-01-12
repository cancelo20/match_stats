from django.core.management import BaseCommand

from football_stats.updates import TeamUpdate, LeagueMatchesUpdate
from football_stats.models import League

import datetime as dt

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "test bot"

    def handle(self, *args, **options):
        pass
        leagues = League.objects.all()

        for league in leagues:
            LeagueMatchesUpdate().matchday_update(league_name=league.name)
