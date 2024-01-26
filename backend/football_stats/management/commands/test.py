import os
import requests

from django.core.management import BaseCommand
from football_stats.models import Team
from dotenv import load_dotenv
from time import sleep


load_dotenv()


HEADERS = {
    'X-Auth-Token': f'{os.getenv("API_TOKEN")}'
}


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "test bot"

    def handle(self, *args, **options):
        teams = Team.objects.filter(league='Premier League')

        for team in teams:
            print(team.name)
            url = f'{os.getenv('TEAMS_URL')}/{team.url_id}'
            response = requests.get(url=url, headers=HEADERS).json()

            fullname = response.get('name') if response.get('name') is not None else '-'
            founded = response.get('founded') if response.get('founded') is not None else -1
            stadium = response.get('venue') if response.get('venue') is not None else '-'
            address = response.get('address') if not response.get('address').startswith('null') else '-'
            website = response.get('website') if response.get('website') is not None else '-'
            coach = response.get('coach').get('name') if response.get('coach').get('name') is not None else '-'


            team.fullname = fullname
            team.founded = founded
            team.stadium = stadium
            team.adress = address
            team.website = website
            team.coach = coach

            team.save()

            sleep(7)
