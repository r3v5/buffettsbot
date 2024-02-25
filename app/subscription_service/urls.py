from django.urls import path
from .views import TelegramUserAPIView


urlpatterns = [
    path('v1/users/', TelegramUserAPIView.as_view(), name='create-telegram-user'),
]