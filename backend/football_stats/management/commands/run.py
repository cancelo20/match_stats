from django.core.management import BaseCommand

from .runbot import datetime_to_text
from football_stats.models import *
from football_stats.responses import *
from football_stats.updates import *

import datetime as dt

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "test bot"

    def handle(self, *args, **options):
        LeagueMatches.objects.all().delete()
        Statistics.objects.all().delete()
