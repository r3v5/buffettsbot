from rest_framework import serializers
from .models import TelegramUser, Subscription, Plan


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ['telegram_id', 'chat_id', 'telegram_username', 'first_name', 'last_name']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['customer', 'plan', 'transaction_hash']