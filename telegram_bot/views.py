from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
import json
import os
import telegram
from django.conf import settings
from .models import *
from .bot_tools import get_users_ids, get_visitors_ids, get_speakers_ids, get_moderators_ids
from time import sleep
def send_message(request):
    token = os.getenv('TG_API_TOKEN')
    request_data = json.loads(request.read())
    event_name = request_data['event_name']
    event = Event.objects.get(name=event_name)

    message_text = request_data['message_text']
    receivers = request_data['to_whom']

    funcs_by_codes = {1: get_users_ids, 2: get_visitors_ids, 3: get_moderators_ids, 4: get_speakers_ids}

    receivers_ids = funcs_by_codes[receivers](event)


    bot = telegram.Bot(token=token)

    for id_ in receivers_ids:
        try:
            bot.sendMessage(chat_id=id_, text=message_text)
            sleep(0.05)
        except Exception:
            pass


    return HttpResponse(status=200)


