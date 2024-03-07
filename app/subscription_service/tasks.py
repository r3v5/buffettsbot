import pytz
from celery import shared_task
from django.utils import timezone
from subscription_service.utils import TelegramMessageSender

from .models import Subscription, TelegramUser


@shared_task
def find_new_subscriptions():
    try:
        subscriptions = Subscription.objects.filter(
            customer__at_private_group=False
        ).select_related("customer", "plan")
        print(f"Founded new subscriptions: {subscriptions}")
    except Subscription.DoesNotExist:
        print("New subscriptions not found.")

    # Get the admins
    try:
        admins_of_group = TelegramUser.objects.filter(is_staff=True)
        print("Found users:", admins_of_group)
    except TelegramUser.DoesNotExist:
        print("Users not found.")

    # Convert time in Moscow time zone
    moscow_tz = pytz.timezone("Europe/Moscow")

    for subscription in subscriptions:
        telegram_username = subscription.customer.telegram_username
        subscription_plan = subscription.plan.period
        subscription_price = subscription.plan.price
        tx_hash = subscription.transaction_hash
        subscription_start_date = subscription.start_date.astimezone(
            moscow_tz
        ).strftime("%d/%m/%Y %H:%M:%S")
        subscription_end_date = subscription.end_date.astimezone(moscow_tz).strftime(
            "%d/%m/%Y %H:%M:%S"
        )

        for admin in admins_of_group:
            try:
                """message = (
                    f"Hi, {admin.telegram_username}!\n\n"
                    f"Action: 🟢 add to private group\n\n"
                    f"Transaction Details 🪪\n"
                    f"--------------------------------------\n"
                    f"User: @{telegram_username}\n"
                    f"--------------------------------------\n"
                    f"Transferred: {amount_usdt} USDT\n"
                    f"--------------------------------------\n"
                    f"Subscription plan: {plan.period}\n"
                    f"--------------------------------------\n"
                    f"Hash: https://tronscan.org/#/transaction/{tx_hash}\n\n"
                    "Click the link to copy the transaction hash."
                )"""

                message = TelegramMessageSender.create_message_about_add_user(
                    admin_of_group=admin.telegram_username,
                    telegram_username=telegram_username,
                    subscription_start_date=subscription_start_date,
                    subscription_end_date=subscription_end_date,
                    subscription_plan=subscription_plan,
                    subscription_price=subscription_price,
                    tx_hash=tx_hash,
                )

                response = TelegramMessageSender.send_message_to_admin_of_group(
                    message=message, chat_id=admin.chat_id
                )

                if response.status_code == 200:
                    subscription.customer.add_to_private_group()
                    print(f"User {telegram_username} must be added to the group.")
                else:
                    print(
                        f"Failed to add user {telegram_username} to the group. Status code: {response.status_code}"
                    )
            except Exception as e:
                print(f"Failed to add user {telegram_username} to the group: {str(e)}")


@shared_task
def delete_expired_subscriptions():
    # Get the admins
    try:
        admins_of_group = TelegramUser.objects.filter(is_staff=True)
        print("Found users:", admins_of_group)
    except TelegramUser.DoesNotExist:
        print("Users not found.")

    today = timezone.now().date()
    moscow_tz = pytz.timezone("Europe/Moscow")

    try:
        # Print today's date for debugging
        print("Today's date:", today)
        print(f"Today'time: {timezone.now()}")

        expired_subscriptions = Subscription.objects.select_related(
            "customer", "plan"
        ).filter(end_date__date=today)

        # Print the SQL query being executed
        print("SQL Query:", expired_subscriptions.query)

        print("Found subscriptions:", expired_subscriptions)
    except Subscription.DoesNotExist:
        print("Subscriptions not found.")

    for subscription in expired_subscriptions:
        if subscription.is_expired():
            telegram_username = subscription.customer.telegram_username
            subscription_start_date = subscription.start_date.astimezone(
                moscow_tz
            ).strftime("%d/%m/%Y %H:%M:%S")
            subscription_end_date = subscription.end_date.astimezone(
                moscow_tz
            ).strftime("%d/%m/%Y %H:%M:%S")
            subscription_plan = subscription.plan.period
            subscription_price = subscription.plan.price
            tx_hash = subscription.transaction_hash

            for admin in admins_of_group:
                try:
                    """message = (
                        f"Hi, {admin.telegram_username}!\n\n"
                        f"Action: 🔴 delete from private group\n\n"
                        f"Subscription Details 📁\n"
                        f"--------------------------------------\n"
                        f"User: @{telegram_username}\n"
                        f"--------------------------------------\n"
                        f"Purchased on: {subscription_start_date}\n"
                        f"--------------------------------------\n"
                        f"Expired on: {subscription_end_date}\n"
                        f"--------------------------------------\n"
                        f"Subscription plan: {subscription_plan}\n"
                        f"--------------------------------------\n"
                        f"Subscription price: {subscription_price} USDT\n"
                        f"--------------------------------------\n"
                        f"Hash: https://tronscan.org/#/transaction/{tx_hash}\n\n"
                        "Click the link to copy the transaction hash."
                    )"""

                    message = TelegramMessageSender.create_message_about_delete_user(
                        admin_of_group=admin.telegram_username,
                        telegram_username=telegram_username,
                        subscription_start_date=subscription_start_date,
                        subscription_end_date=subscription_end_date,
                        subscription_plan=subscription_plan,
                        subscription_price=subscription_price,
                        tx_hash=tx_hash,
                    )

                    response = TelegramMessageSender.send_message_to_admin_of_group(
                        message=message, chat_id=admin.chat_id
                    )

                    if response.status_code == 200:
                        subscription.delete()
                        print(f"{subscription} was successfully deleted.")

                        subscription.customer.delete_from_private_group()
                        """subscription.customer.at_private_group = False
                        subscription.customer.save(update_fields=["at_private_group"])"""
                        print(
                            f"User {subscription.customer.telegram_username} must be deleted from the group."
                        )
                    else:
                        print(f"{subscription} was not deleted.")
                        print(
                            f"Failed to delete user {subscription.customer.telegram_username} from the group. Status code: {response.status_code}"
                        )
                except Exception as e:
                    print(
                        f"Failed to delete user {subscription.customer.telegram_username} from the group: {str(e)}"
                    )
        else:
            print("Expired subscriptions not found.")
