from django.core.management import BaseCommand
from telegram_bot import bot

class Command(BaseCommand):
    def handle(self, *args, **options):
        bot.main()
    	
         
