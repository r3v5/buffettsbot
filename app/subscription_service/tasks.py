import os
from datetime import timedelta

import requests
from celery import shared_task

from .models import Subscription


class TelegramConnector:
    TELEGRAM_API_ENDPOINT = os.environ.get("TELEGRAM_API_ENDPOINT")
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_PRIVATE_GROUP_ID = os.environ.get("TELEGRAM_PRIVATE_GROUP_ID")


@shared_task
def add_users_to_private_group():
    subscriptions = Subscription.objects.filter(
        customer__at_private_group=False
    ).select_related("customer")

    # Prepare url for Telegram API
    url = f"{TelegramConnector.TELEGRAM_API_ENDPOINT}/bot{TelegramConnector.TELEGRAM_BOT_TOKEN}/inviteChatMember"

    for subscription in subscriptions:
        user_id = subscription.customer.chat_id
        params = {
            "chat_id": str(TelegramConnector.TELEGRAM_PRIVATE_GROUP_ID),
            "user_id": user_id,
        }

        try:
            response = requests.post(url, params=params)

            if response.status_code == 200:
                subscription.customer.at_private_group = True
                subscription.customer.save(update_fields=["at_private_group"])
                print(f"User {user_id} added to the group.")
            else:
                print(
                    f"Failed to add user {user_id} to the group. Status code: {response.status_code}"
                )
        except Exception as e:
            print(f"Failed to add user {user_id} to the group: {str(e)}")
