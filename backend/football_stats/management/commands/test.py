from django.core.management import BaseCommand

from football_stats.updates import TeamUpdate
from football_stats.models import League

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "test bot"

    def handle(self, *args, **options):

        TeamUpdate().team_results_update(league_name='Premier League')
