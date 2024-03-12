from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import localtime
from rest_framework import status
from rest_framework.test import APIClient

from subscription_service.models import Plan, Subscription, TelegramUser


@pytest.mark.django_db
def test_create_telegram_user():
    url = reverse("create-telegram-user")
    data = {
        "chat_id": 2141241241245,
        "telegram_username": "@TestUser",
        "first_name": "Conor",
        "last_name": "McGregor",
    }
    client = APIClient()
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert TelegramUser.objects.count() == 1
    assert TelegramUser.objects.get().telegram_username == "@TestUser"


@pytest.mark.django_db
def test_invalid_telegram_user():
    url = reverse("create-telegram-user")
    data = {
        "chat_id": 54321,
        "first_name": "John",
        "last_name": "Doe",
    }
    client = APIClient()
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert TelegramUser.objects.count() == 0
    assert "telegram_username" in response.data
    expected_errors = {"telegram_username": ["This field is required."]}
    assert response.data == expected_errors


@pytest.mark.django_db
def test_valid_subscription_create():
    # Create necessary test data
    user = TelegramUser.objects.create(
        chat_id=123456,
        telegram_username="test_user",
    )
    plan = Plan.objects.create(period="1 month", price=10)
    subscriptions = Subscription.objects.all()
    assert len(subscriptions) == 0

    # Mock TronTransactionAnalyzer's response
    with patch(
        "subscription_service.utils.TronTransactionAnalyzer.validate_tx_hash"
    ) as mock_validate_tx_hash:
        mock_validate_tx_hash.return_value = True  # Mock the response as successful

        # Make a POST request to the API endpoint
        client = APIClient()
        url = reverse(
            "manage-subscription"
        )  # Assuming you have a URL name for the subscription create endpoint
        data = {
            "telegram_username": user.telegram_username,
            "plan": plan.period,
            "transaction_hash": "a2497862faf68c54e6b745f9b84fcb4e6a736b3cd108696590b7ba8e3910b170",
        }
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        subscriptions = Subscription.objects.all()
        assert len(subscriptions) == 1

        # Check if user's subscription is created
        assert Subscription.objects.filter(customer=user, plan=plan).exists()


@pytest.mark.django_db
def test_invalid_create_subscription():
    # Create necessary test data
    user = TelegramUser.objects.create(
        chat_id=123456,
        telegram_username="test_user",
        first_name="Test",
        last_name="User",
        at_private_group=True,
        is_staff=False,
    )
    plan = Plan.objects.create(period="1 month", price=10)

    # Mock TronTransactionAnalyzer's response
    with patch(
        "subscription_service.utils.TronTransactionAnalyzer.validate_tx_hash"
    ) as mock_validate_tx_hash:
        mock_validate_tx_hash.return_value = False

        # Make a POST request to the API endpoint
        client = APIClient()
        url = reverse(
            "manage-subscription"
        )  # Assuming you have a URL name for the subscription create endpoint
        data = {
            "telegram_username": "test_user",
            "plan": "1 month",
            "transaction_hash": "your_invalid_transaction_hash_here",
        }
        response = client.post(url, data, format="json")

        # Assertions
        assert (
            response.status_code == 400
        )  # Check if response status code is as expected

        # Check if subscription is not created
        assert not Subscription.objects.filter(customer=user, plan=plan).exists()

        # Check if the correct error message is returned in the response
        assert response.data["message"] == "Transaction is not valid"


@pytest.mark.django_db
def test_valid_get_subscription():
    # Create a TelegramUser
    user = TelegramUser.objects.create(
        chat_id=92412523532,
        telegram_username="test_user",
    )

    print(f"User: {user}")

    # Create a Plan
    plan = Plan.objects.create(period="2 days", price=19)

    # Create a Subscription
    subscription = Subscription.objects.create(
        customer=user,
        plan=plan,
        transaction_hash="0x123456789abcdef",
        start_date=timezone.now(),
    )

    print(f"User have subscription: {Subscription.objects.get(customer=user)}")

    # Convert subscription.start_date to the local time zone
    local_start_date = localtime(subscription.start_date)

    # Convert subscription.start_date to a string with the same format as response.data['start_date']
    expected_start_date_str = local_start_date.strftime("%d/%m/%Y %H:%M:%S")

    # Calculate the expected end date and convert it to the local time zone
    expected_end_date = subscription.end_date
    expected_end_date = localtime(expected_end_date)

    # Convert expected_end_date to a string with the same format as response.data['end_date']
    expected_end_date_str = expected_end_date.strftime("%d/%m/%Y %H:%M:%S")

    # Prepare data for POST request
    data = {"telegram_username": user.telegram_username}

    client = APIClient()
    url = reverse("manage-subscription")

    # Make a GET request with the user's telegram_username
    response = client.get(url, data, format="json")

    print(f"response: {response.data}")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["customer"] == user.telegram_username
    assert response.data["plan"] == plan.period
    assert response.data["price"] == plan.price
    assert response.data["transaction_hash"] == subscription.transaction_hash
    assert response.data["start_date"] == expected_start_date_str
    assert response.data["end_date"] == expected_end_date_str


@pytest.mark.django_db
def test_invalid_get_subscription():
    # Create a TelegramUser
    user = TelegramUser.objects.create(
        chat_id=3253253253,
        telegram_username="test_user",
        first_name="Test",
        last_name="User",
    )

    # Prepare data for POST request
    data = {"telegram_username": user.telegram_username}

    client = APIClient()
    url = reverse("manage-subscription")

    # Make a GET request with a non-existent subscription
    response = client.get(url, data, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "message" in response.data
    assert response.data["message"] == "Subscription not found"

    # Prepare data for POST request
    data = {"telegram_username": "@fox"}

    client = APIClient()
    url = reverse("manage-subscription")

    # Make a GET request with a non-existent user's telegram_username
    response = client.get(url, data, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "message" in response.data
    assert response.data["message"] == "User not found"
