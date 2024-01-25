from datetime import datetime as dt, timedelta as td
from pytz import UTC
from time import sleep
from django.core.management import BaseCommand
from threading import Thread
from football_stats.checks import Checks
from football_stats.models import League, LeagueMatches


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "UPDATES"

    def handle(self, *args, **options):
        def run():
            while True:
                try:
                    matches = LeagueMatches.objects.filter(
                        current_match__istartswith="IN LIVE"
                    )
                    leagues = League.objects.all()

                    for f_match in matches:
                        if dt.utcnow().replace(tzinfo=UTC) > (
                            f_match.date + td(hours=1, minutes=45)
                        ):
                            Checks(league_name=f_match.name).is_matches_finished()

                    for league in leagues:
                        if dt.utcnow().replace(tzinfo=UTC) > (
                            league.end_date + td(hours=3)
                        ):
                            Checks(league_name=league.name).is_current_tour()
                except Exception as error:
                        print(error)
                        continue
                finally:
                        print('checking...')
                        sleep(60)

        Thread(target=run, daemon=True).start()
        input('Press <Enter> to exit.\n')
