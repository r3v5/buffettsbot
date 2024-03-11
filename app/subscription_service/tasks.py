import os
from datetime import timedelta

import pytz
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from subscription_service.utils import TelegramMessageSender

from .models import Subscription, TelegramUser


@shared_task
def find_new_subscriptions() -> None:
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
                message = TelegramMessageSender.create_message_about_add_user(
                    admin_of_group=admin.telegram_username,
                    telegram_username=telegram_username,
                    subscription_start_date=subscription_start_date,
                    subscription_end_date=subscription_end_date,
                    subscription_plan=subscription_plan,
                    subscription_price=subscription_price,
                    tx_hash=tx_hash,
                )

                response = TelegramMessageSender.send_message_to_chat(
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
def delete_expired_subscriptions() -> None:
    # Get the admins
    try:
        admins_of_group = TelegramUser.objects.filter(is_staff=True)
        print("Found users:", admins_of_group)
    except TelegramUser.DoesNotExist:
        print("Users not found.")

    today = timezone.now()
    moscow_tz = pytz.timezone("Europe/Moscow")

    try:
        # Print today's date for debugging
        print(f"Today'time: {timezone.now()}")

        expired_subscriptions = Subscription.objects.select_related(
            "customer", "plan"
        ).filter(end_date__lt=today)

        print("Found subscriptions:", expired_subscriptions)
    except Subscription.DoesNotExist:
        print("Subscriptions not found.")

    for subscription in expired_subscriptions:

        telegram_username = subscription.customer.telegram_username
        subscription_start_date = subscription.start_date.astimezone(
            moscow_tz
        ).strftime("%d/%m/%Y %H:%M:%S")
        subscription_end_date = subscription.end_date.astimezone(moscow_tz).strftime(
            "%d/%m/%Y %H:%M:%S"
        )
        subscription_plan = subscription.plan.period
        subscription_price = subscription.plan.price
        tx_hash = subscription.transaction_hash

        for admin in admins_of_group:
            try:
                message = TelegramMessageSender.create_message_about_delete_user(
                    admin_of_group=admin.telegram_username,
                    telegram_username=telegram_username,
                    subscription_start_date=subscription_start_date,
                    subscription_end_date=subscription_end_date,
                    subscription_plan=subscription_plan,
                    subscription_price=subscription_price,
                    tx_hash=tx_hash,
                )

                response = TelegramMessageSender.send_message_to_chat(
                    message=message, chat_id=admin.chat_id
                )

                if response.status_code == 200:
                    subscription.delete()
                    print(f"{subscription} was successfully deleted.")
                    subscription.customer.delete_from_private_group()
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


@shared_task
def notify_about_expiring_subscriptions_1_day() -> None:
    # Get the admins
    try:
        admins_of_group = TelegramUser.objects.filter(is_staff=True)
        print("Found users:", admins_of_group)
    except TelegramUser.DoesNotExist:
        print("Users not found.")

    try:
        subscriptions = Subscription.objects.filter(
            end_date__gte=timezone.now() + timedelta(days=1)
        ).select_related("customer", "plan")
        print(f"Found subscriptions ending after 1 day: {subscriptions}")
    except Subscription.DoesNotExist:
        print("Subscriptions ending after 1 day not found.")

    moscow_tz = pytz.timezone("Europe/Moscow")

    for subscription in subscriptions:
        telegram_username = subscription.customer.telegram_username
        chat_id = subscription.customer.chat_id
        subscription_start_date = subscription.start_date.astimezone(
            moscow_tz
        ).strftime("%d/%m/%Y %H:%M:%S")
        subscription_end_date = subscription.end_date.astimezone(moscow_tz).strftime(
            "%d/%m/%Y %H:%M:%S"
        )
        subscription_plan = subscription.plan.period
        subscription_price = subscription.plan.price

        for admin in admins_of_group:
            try:
                # Firstly, send a reminder to user
                message = TelegramMessageSender.create_message_about_reminder(
                    telegram_username=telegram_username,
                    subscription_plan=subscription_plan,
                    subscription_start_date=subscription_start_date,
                    subscription_end_date=subscription_end_date,
                    subscription_price=subscription_price,
                    day=1,
                    syntax_word="день",
                )

                response = TelegramMessageSender.send_message_with_photo_to_chat(
                    message=message,
                    photo_path=os.path.join(
                        settings.MEDIA_ROOT,
                        "buffets-on-crows.jpg",
                    ),
                    chat_id=chat_id,
                )

                if response.status_code == 200:
                    print(f"Reminder sent to user {telegram_username}.")

                    # Secondly, notify about it admins of group
                    message = (
                        f"Hi, {admin.telegram_username}!\n\n"
                        f"A reminder about extending the subscription was successfully sent to @{telegram_username}\n\n"
                    )

                    response = TelegramMessageSender.send_message_to_chat(
                        message=message, chat_id=admin.chat_id
                    )

                    if response.status_code == 200:
                        print("Log message was successfully sent to admin")
                    else:
                        print(
                            f"Failed to sent log message to admin. Status code: {response.status_code}"
                        )
                else:
                    print(
                        f"Failed to send reminder to user {telegram_username}. Status code: {response.status_code}"
                    )
            except Exception as e:
                print(f"Failed to send reminder to user {telegram_username}: {str(e)}")


@shared_task
def notify_about_expiring_subscriptions_3_days() -> None:
    # Get the admins
    try:
        admins_of_group = TelegramUser.objects.filter(is_staff=True)
        print("Found users:", admins_of_group)
    except TelegramUser.DoesNotExist:
        print("Users not found.")

    try:
        subscriptions = Subscription.objects.filter(
            end_date__gte=timezone.now() + timedelta(days=3)
        ).select_related("customer", "plan")
        print(f"Found subscriptions ending after 3 days: {subscriptions}")
    except Subscription.DoesNotExist:
        print("Subscriptions ending after 3 days not found.")

    moscow_tz = pytz.timezone("Europe/Moscow")

    for subscription in subscriptions:
        telegram_username = subscription.customer.telegram_username
        chat_id = subscription.customer.chat_id
        subscription_start_date = subscription.start_date.astimezone(
            moscow_tz
        ).strftime("%d/%m/%Y %H:%M:%S")
        subscription_end_date = subscription.end_date.astimezone(moscow_tz).strftime(
            "%d/%m/%Y %H:%M:%S"
        )
        subscription_plan = subscription.plan.period
        subscription_price = subscription.plan.price

        for admin in admins_of_group:
            try:
                # Firstly, send a reminder to user
                message = TelegramMessageSender.create_message_about_reminder(
                    telegram_username=telegram_username,
                    subscription_plan=subscription_plan,
                    subscription_start_date=subscription_start_date,
                    subscription_end_date=subscription_end_date,
                    subscription_price=subscription_price,
                    day=3,
                    syntax_word="дня",
                )

                response = TelegramMessageSender.send_message_to_chat(
                    message=message, chat_id=chat_id
                )

                if response.status_code == 200:
                    print(f"Reminder sent to user {telegram_username}.")

                    # Secondly, notify about it admins of group
                    message = (
                        f"Hi, {admin.telegram_username}!\n\n"
                        f"A reminder about extending the subscription was successfully sent to @{telegram_username}\n\n"
                    )

                    response = TelegramMessageSender.send_message_to_chat(
                        message=message, chat_id=admin.chat_id
                    )

                    if response.status_code == 200:
                        print("Log message was successfully sent to admin")
                    else:
                        print(
                            f"Failed to sent log message to admin. Status code: {response.status_code}"
                        )
                else:
                    print(
                        f"Failed to send reminder to user {telegram_username}. Status code: {response.status_code}"
                    )
            except Exception as e:
                print(f"Failed to send reminder to user {telegram_username}: {str(e)}")


@shared_task
def notify_about_expiring_subscriptions_7_days() -> None:
    # Get the admins
    try:
        admins_of_group = TelegramUser.objects.filter(is_staff=True)
        print("Found users:", admins_of_group)
    except TelegramUser.DoesNotExist:
        print("Users not found.")

    try:
        subscriptions = Subscription.objects.filter(
            end_date__gte=timezone.now() + timedelta(days=7)
        ).select_related("customer", "plan")
        print(f"Found subscriptions ending after 7 days: {subscriptions}")
    except Subscription.DoesNotExist:
        print("Subscriptions ending after 7 days not found.")

    moscow_tz = pytz.timezone("Europe/Moscow")

    for subscription in subscriptions:
        telegram_username = subscription.customer.telegram_username
        chat_id = subscription.customer.chat_id
        subscription_start_date = subscription.start_date.astimezone(
            moscow_tz
        ).strftime("%d/%m/%Y %H:%M:%S")
        subscription_end_date = subscription.end_date.astimezone(moscow_tz).strftime(
            "%d/%m/%Y %H:%M:%S"
        )
        subscription_plan = subscription.plan.period
        subscription_price = subscription.plan.price

        for admin in admins_of_group:
            try:
                # Firstly, send a reminder to user
                message = TelegramMessageSender.create_message_about_reminder(
                    telegram_username=telegram_username,
                    subscription_plan=subscription_plan,
                    subscription_start_date=subscription_start_date,
                    subscription_end_date=subscription_end_date,
                    subscription_price=subscription_price,
                    day=7,
                    syntax_word="дней",
                )

                response = TelegramMessageSender.send_message_to_chat(
                    message=message, chat_id=chat_id
                )

                if response.status_code == 200:
                    print(f"Reminder sent to user {telegram_username}.")

                    # Secondly, notify about it admins of group
                    message = (
                        f"Hi, {admin.telegram_username}!\n\n"
                        f"A reminder about extending the subscription was successfully sent to @{telegram_username}\n\n"
                    )

                    response = TelegramMessageSender.send_message_to_chat(
                        message=message, chat_id=admin.chat_id
                    )

                    if response.status_code == 200:
                        print("Log message was successfully sent to admin")
                    else:
                        print(
                            f"Failed to sent log message to admin. Status code: {response.status_code}"
                        )
                else:
                    print(
                        f"Failed to send reminder to user {telegram_username}. Status code: {response.status_code}"
                    )
            except Exception as e:
                print(f"Failed to send reminder to user {telegram_username}: {str(e)}")
