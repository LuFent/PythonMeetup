from .views import *
from django.urls import path

app_name = "boxes"

urlpatterns = [
    path("send_message", send_message)
]