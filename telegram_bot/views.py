from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
import json
import os
import telegram
from django.conf import settings

def send_message(request):
    token = os.getenv('TG_API_TOKEN')
    request_data = json.loads(request.read())
    event_id = request_data['event_id']
    message_text = request_data['message_text']
    bot = telegram.Bot(token=token)

    bot.sendMessage(chat_id=1720622916, text=message_text)

    return HttpResponse(status=200)


