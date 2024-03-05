import os

from celery import shared_task
from subscription_service.utils import TelegramMessageSender

from .models import Subscription, TelegramUser


@shared_task
def add_user_to_private_group():
    subscriptions = Subscription.objects.filter(
        customer__at_private_group=False
    ).select_related("customer")

    # Get the admins
    try:
        admins = TelegramUser.objects.filter(is_staff=True)
        print("Founded users:", admins)
    except TelegramUser.DoesNotExist:
        print("Users not found.")

    for subscription in subscriptions:
        telegram_username = subscription.customer.telegram_username
        plan = subscription.plan
        amount_usdt = subscription.plan.price
        tx_hash = subscription.transaction_hash

        for admin in admins:
            try:
                message = message = (
                    f"Hi, {admin.telegram_username}!\n"
                    f"Action 🟢: add to private group\n\n"
                    f"Transaction Details 🪪\n"
                    f"User: @{telegram_username}\n"
                    f"Transferred: {amount_usdt} USDT\n"
                    f"Subscription plan: {plan.period}\n"
                    f"Hash: https://tronscan.org/#/transaction/{tx_hash}\n\n"
                    "Click the link to copy the transaction hash."
                )

                response = TelegramMessageSender.send_message_to_admin_of_group(
                    message=message, chat_id=admin.chat_id
                )

                if response.status_code == 200:
                    subscription.customer.at_private_group = True
                    subscription.customer.save(update_fields=["at_private_group"])
                    print(f"User {telegram_username} must be added to the group.")
                else:
                    print(
                        f"Failed to add user {telegram_username} to the group. Status code: {response.status_code}"
                    )
            except Exception as e:
                print(f"Failed to add user {telegram_username} to the group: {str(e)}")
