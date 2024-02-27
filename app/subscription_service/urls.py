from django.urls import path
from .views import TelegramUserAPIView, SubscriptionAPIView


urlpatterns = [
    path('v1/users/', TelegramUserAPIView.as_view(), name='create-telegram-user'),
    path('v1/subscriptions/', SubscriptionAPIView.as_view(), name='create-subscription'),
]