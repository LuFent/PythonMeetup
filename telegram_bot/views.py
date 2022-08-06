from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
import json
import os
import telegram
from django.conf import settings
from .models import *
from .bot_tools import get_users_ids
def send_message(request):
    token = os.getenv('TG_API_TOKEN')
    request_data = json.loads(request.read())
    event_name = request_data['event_name']
    event = Event.objects.get(name=event_name)

    message_text = request_data['message_text']
    receivers = request_data['to_whom']
    if receivers == 1:
        receivers_ids = get_users_ids(event)


    bot = telegram.Bot(token=token)

    bot.sendMessage(chat_id=1720622916, text=message_text)

    return HttpResponse(status=200)


