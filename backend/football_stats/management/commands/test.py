from django.core.management import BaseCommand
import telebot
import os
from time import sleep
from dotenv import load_dotenv
from user.models import User
from threading import Thread

load_dotenv()


TG_TOKEN = str(os.getenv('TG_TOKEN'))
bot = telebot.TeleBot(TG_TOKEN)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "test bot"

    def handle(self, *args, **options):
        #def run():
        while True:
            user = User.objects.get(username='stepankrylovv')
            bot.send_message(
                chat_id=user.chat_id,
                text='Hello!',
            )
            sleep(60)

        #Thread(target=run, daemon=True).start()
        #input('Press <Enter> to exit.\n')
