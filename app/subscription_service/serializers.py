from rest_framework import serializers

from .models import Plan, Subscription, TelegramUser


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = [
            "telegram_id",
            "chat_id",
            "telegram_username",
            "first_name",
            "last_name",
        ]


class PostSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["customer", "plan", "transaction_hash"]


class GetSubscriptionSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(source="customer.telegram_username")
    plan = serializers.CharField(source="plan.period")
    price = serializers.IntegerField(source="plan.price")
    start_date = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    end_date = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")

    class Meta:
        model = Subscription
        fields = [
            "customer",
            "plan",
            "price",
            "transaction_hash",
            "start_date",
            "end_date",
        ]
