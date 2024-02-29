import pytest
from subscription_service.serializers import TelegramUserSerializer, SubscriptionSerializer
from subscription_service.models import TelegramUser, Plan, Subscription
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError


@pytest.mark.django_db
def test_valid_telegram_user_serializer():
    valid_serializer_data = {
        "telegram_id": 2141241241245,
        "chat_id": 2141241241245,
        "telegram_username": "@TestUser",
        "first_name": "Conor",
        "last_name": "McGregor"
    }
    serializer = TelegramUserSerializer(data=valid_serializer_data)
    assert serializer.is_valid()
    assert serializer.validated_data == valid_serializer_data
    assert serializer.data == valid_serializer_data
    assert serializer.errors == {}


@pytest.mark.django_db
def test_invalid_telegram_user_serializer():
    invalid_serializer_data = {
        "telegram_id": 2141241241245,
        "chat_id": 2141241241245,
    }
    serializer = TelegramUserSerializer(data=invalid_serializer_data)
    assert not serializer.is_valid()
    assert serializer.validated_data == {}
    assert serializer.data == invalid_serializer_data
    assert serializer.errors == {"telegram_username": ["This field is required."]}


@pytest.mark.django_db
def test_valid_subscription_serializer():
    user = TelegramUser.objects.create(
        telegram_id=12345,
        chat_id=67890,
        telegram_username='@test_user',
        first_name='Test',
        last_name='User',
        at_private_group=False
    )
    plan = Plan.objects.create(period='2 days', price=19)
    subscription_data = {
        'customer': user.id,
        'plan': plan.id,
        'transaction_hash': 'Test Transaction Hash',
        'start_date': timezone.now()
    }
    serializer = SubscriptionSerializer(data=subscription_data)
    assert serializer.is_valid()
    serializer.save()
    saved_subscription = Subscription.objects.get(customer=user)
    expected_end_date = subscription_data['start_date'] + timedelta(days=2)
    assert saved_subscription.end_date.replace(microsecond=0) == expected_end_date.replace(microsecond=0)


    # Check if the related user's at_private_group field is updated to True
    updated_user = TelegramUser.objects.get(id=user.id)
    assert updated_user.at_private_group == True


@pytest.mark.django_db
def test_invalid_subscription_serializer():
    # Create a TelegramUser
    user = TelegramUser.objects.create(
        telegram_id=12345,
        chat_id=67890,
        telegram_username='@test_user',
        first_name='Test',
        last_name='User',
        at_private_group=False
    )

    # Create a Plan
    plan = Plan.objects.create(period='2 days', price=19)

    # Define subscription data with missing required fields
    invalid_subscription_data = {
        'customer': user.id,
        'transaction_hash': 'Test Transaction Hash'
    }

    # Try to serialize the invalid data
    serializer = SubscriptionSerializer(data=invalid_subscription_data)

    assert not serializer.is_valid()
    assert serializer.validated_data == {}
    assert serializer.data == invalid_subscription_data
    assert serializer.errors == {"plan": ["This field is required."]}