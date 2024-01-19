from django.core.management import BaseCommand

from .runbot import datetime_to_text
from football_stats.models import *
from football_stats.responses import *
from football_stats.updates import *
from football_stats.probability import *
import requests

import datetime as dt

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "test bot"

    def handle(self, *args, **options):
        matches = LeagueMatches.objects.all().order_by('name').order_by('date')
        print(dt.datetime.utcnow().date())
        for f_match in matches:
            if f_match.finished:
                continue
            if str(f_match.date).startswith(str(dt.datetime.utcnow().date())):
                print(f'{f_match.current_match} - {f_match.date}')
            else:
                break
