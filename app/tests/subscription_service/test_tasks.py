from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from subscription_service.models import Plan, Subscription, TelegramUser
from subscription_service.tasks import (
    delete_expired_subscriptions,
    find_new_subscriptions,
    notify_about_expiring_subscriptions_1_day,
    notify_about_expiring_subscriptions_3_days,
    notify_about_expiring_subscriptions_7_days,
)


@pytest.mark.django_db
@patch("subscription_service.tasks.TelegramMessageSender")
def test_find_new_subscriptions(mock_telegram_message_sender):
    # Create mock objects
    admin_user = TelegramUser.objects.create(
        chat_id=1, telegram_username="admin", is_staff=True
    )
    plan = Plan.objects.create(period="2 days", price=10)
    Subscription.objects.create(
        customer=admin_user,
        plan=plan,
        transaction_hash="1234567890",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=2),
    )

    # Mock TelegramMessageSender
    mock_telegram_message_sender.create_message_about_add_user.return_value = (
        "Test message"
    )
    mock_telegram_message_sender.send_message_to_chat.return_value.status_code = 200

    # Run Celery task
    find_new_subscriptions()

    # Assertions
    assert Subscription.objects.filter(customer=admin_user).exists() is True


@pytest.mark.django_db
@patch("subscription_service.tasks.TelegramMessageSender")
def test_delete_expired_subscriptions(mock_telegram_message_sender):
    # Create mock objects
    admin_user = TelegramUser.objects.create(
        chat_id=1, telegram_username="admin", is_staff=True
    )
    plan = Plan.objects.create(period="2 days", price=10)
    Subscription.objects.create(
        customer=admin_user,
        plan=plan,
        transaction_hash="1234567890",
        start_date=datetime.now() - timedelta(days=5),
        end_date=datetime.now() - timedelta(days=3),
    )

    # Mock TelegramMessageSender
    mock_telegram_message_sender.create_message_about_delete_user.return_value = (
        "Test message"
    )
    mock_telegram_message_sender.send_message_to_chat.return_value.status_code = 200

    # Run Celery task
    delete_expired_subscriptions()

    # Assertions
    assert not Subscription.objects.filter(customer=admin_user).exists()
    assert admin_user.at_private_group is False


@pytest.mark.django_db
def test_notify_about_expiring_subscriptions_1_day():
    # Create a subscription ending in 1 day
    user = TelegramUser.objects.create(telegram_username="expiring_user", chat_id=789)
    plan = Plan.objects.create(period="2 days", price=10)
    subscription = Subscription.objects.create(
        customer=user,
        plan=plan,
        transaction_hash="expiring_abc123",
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=1),
    )

    # Call the Celery task
    notify_about_expiring_subscriptions_1_day()

    # Assertions
    subscription.refresh_from_db()
    assert subscription.customer.telegram_username == "expiring_user"


@pytest.mark.django_db
def test_notify_about_expiring_subscriptions_3_days():
    # Create a subscription ending in 3 days
    user = TelegramUser.objects.create(
        telegram_username="expiring_user_3_days", chat_id=789
    )
    plan = Plan.objects.create(period="2 days", price=10)
    subscription = Subscription.objects.create(
        customer=user,
        plan=plan,
        transaction_hash="expiring_3_days_abc123",
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=3),
    )

    # Call the Celery task
    notify_about_expiring_subscriptions_3_days()

    # Assertions
    subscription.refresh_from_db()
    assert subscription.customer.telegram_username == "expiring_user_3_days"
    # Add more assertions as needed


@pytest.mark.django_db
def test_notify_about_expiring_subscriptions_7_days():
    # Create a subscription ending in 7 days
    user = TelegramUser.objects.create(
        telegram_username="expiring_user_7_days", chat_id=789
    )
    plan = Plan.objects.create(period="2 days", price=10)
    subscription = Subscription.objects.create(
        customer=user,
        plan=plan,
        transaction_hash="expiring_7_days_abc123",
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=7),
    )

    # Call the Celery task
    notify_about_expiring_subscriptions_7_days()

    # Assertions
    subscription.refresh_from_db()
    assert subscription.customer.telegram_username == "expiring_user_7_days"
