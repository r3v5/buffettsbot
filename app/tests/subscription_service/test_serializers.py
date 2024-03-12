from datetime import datetime, timedelta

import pytest
import pytz
from django.utils import timezone

from subscription_service.models import Plan, Subscription, TelegramUser
from subscription_service.serializers import (
    GetSubscriptionSerializer,
    PostSubscriptionSerializer,
    TelegramUserSerializer,
)


@pytest.mark.django_db
def test_valid_telegram_user_serializer():
    valid_serializer_data = {
        "chat_id": 2141241241245,
        "telegram_username": "@TestUser",
        "first_name": "Conor",
        "last_name": "McGregor",
    }
    serializer = TelegramUserSerializer(data=valid_serializer_data)
    assert serializer.is_valid()
    assert serializer.validated_data == valid_serializer_data
    assert serializer.data == valid_serializer_data
    assert serializer.errors == {}


@pytest.mark.django_db
def test_invalid_telegram_user_serializer():
    invalid_serializer_data = {
        "chat_id": 2141241241245,
    }
    serializer = TelegramUserSerializer(data=invalid_serializer_data)
    assert not serializer.is_valid()
    assert serializer.validated_data == {}
    assert serializer.data == invalid_serializer_data
    assert serializer.errors == {"telegram_username": ["This field is required."]}


@pytest.mark.django_db
def test_valid_post_subscription_serializer():
    user = TelegramUser.objects.create(
        chat_id=67890,
        telegram_username="@test_user",
    )
    plan = Plan.objects.create(period="2 days", price=19)
    subscription_data = {
        "customer": user.chat_id,
        "plan": plan.id,
        "transaction_hash": "63247632g236776322",
        "start_date": timezone.now(),
    }
    serializer = PostSubscriptionSerializer(data=subscription_data)
    assert serializer.is_valid()
    serializer.save()

    # Check if the object is saved in the database
    assert Subscription.objects.filter(transaction_hash="63247632g236776322").exists()
    saved_subscription = Subscription.objects.get(customer=user)
    expected_end_date = subscription_data["start_date"] + timedelta(days=2)
    assert saved_subscription.end_date.replace(
        microsecond=0
    ) == expected_end_date.replace(microsecond=0)


@pytest.mark.django_db
def test_invalid_post_subscription_serializer():
    user = TelegramUser.objects.create(
        chat_id=67890,
        telegram_username="@test_user",
    )
    plan = Plan.objects.create(period="2 days", price=19)
    subscription_data = {
        "customer": user.chat_id,
        "plan": plan.id,
    }
    serializer = PostSubscriptionSerializer(data=subscription_data)
    assert not serializer.is_valid()
    assert "transaction_hash" in serializer.errors
    assert not Subscription.objects.filter(customer=user).exists()


@pytest.mark.django_db
def test_valid_get_subscription_serializer():
    # Create a TelegramUser
    user = TelegramUser.objects.create(
        chat_id=67890,
        telegram_username="test_user",
    )

    # Create a Plan
    plan = Plan.objects.create(period="2 days", price=19)

    # Create a Subscription
    start_date = datetime(2024, 3, 1, 0, 38, 38, tzinfo=pytz.UTC)
    end_date = start_date + timezone.timedelta(days=2)
    subscription = Subscription.objects.create(
        customer=user,
        plan=plan,
        transaction_hash="iu2grug8273g87329892837tg3293",
        start_date=start_date,
        end_date=end_date,
    )

    # Serialize the subscription
    serializer = GetSubscriptionSerializer(instance=subscription)

    # Define the expected serialized data
    expected_data = {
        "customer": "test_user",
        "plan": "2 days",
        "price": 19,
        "transaction_hash": "iu2grug8273g87329892837tg3293",
        "start_date": start_date.astimezone(pytz.timezone("Europe/Moscow")).strftime(
            "%d/%m/%Y %H:%M:%S"
        ),
        "end_date": end_date.astimezone(pytz.timezone("Europe/Moscow")).strftime(
            "%d/%m/%Y %H:%M:%S"
        ),
    }

    assert serializer.data == expected_data


@pytest.mark.django_db
def test_invalid_get_subscription_serializer():
    subscription_data = {
        # Missing 'customer' field
        "plan": {"period": "1 month", "price": 20},
        "transaction_hash": "0x123456789",
        "start_date": "2022-03-01T12:00:00Z",
        "end_date": "2022-03-31T12:00:00Z",
    }

    # Serialize the data
    serializer = GetSubscriptionSerializer(data=subscription_data)

    # Ensure that serializer validation fails
    assert not serializer.is_valid()

    # Check if 'customer' field is required
    assert "customer" in serializer.errors

    # Check if 'price' field is required
    assert "price" in serializer.errors
