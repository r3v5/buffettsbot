from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
import pytest
import json
from subscription_service.models import TelegramUser, Plan, Subscription


@pytest.mark.django_db
def test_create_telegram_user():
    url = reverse('create-telegram-user')
    data = {
        "telegram_id": 2141241241245,
        "chat_id": 2141241241245,
        "telegram_username": "@TestUser",
        "first_name": "Conor",
        "last_name": "McGregor"
    }
    client = APIClient()
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert TelegramUser.objects.count() == 1
    assert TelegramUser.objects.get().telegram_username == '@TestUser'


@pytest.mark.django_db
def test_invalid_telegram_user():
    url = reverse('create-telegram-user')
    data = {
        'telegram_id': 12345,
        'chat_id': 54321,
        'first_name': 'John',
        'last_name': 'Doe'
    }
    client = APIClient()
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert TelegramUser.objects.count() == 0
    assert 'telegram_username' in response.data
    expected_errors = {'telegram_username': ['This field is required.']}
    assert response.data == expected_errors


@pytest.mark.django_db
def test_valid_create_subscription():
    # Create sample data
    TelegramUser.objects.create(telegram_username='@test_user')
    Plan.objects.create(period='2 days', price=19)
    subscriptions = Subscription.objects.all()
    assert len(subscriptions) == 0


    # Prepare data for POST request
    data = {
        'telegram_username': '@test_user',
        'plan': '2 days',
        'transaction_hash': '357648462a7b472c7ac1123550023a0674aca4849fc385bd67e3a51aeb492564'
    }


    client = APIClient()
    url = reverse('create-subscription')


    # Make POST request
    response = client.post(url, data, format='json')


    assert response.status_code == status.HTTP_201_CREATED

    subscriptions = Subscription.objects.all()
    assert len(subscriptions) == 1


@pytest.mark.django_db
def test_invalid_create_subscription():
    # Create sample data
    TelegramUser.objects.create(telegram_username='@test_user')
    Plan.objects.create(period='2 days', price=19)
    subscriptions = Subscription.objects.all()
    assert len(subscriptions) == 0


    # Prepare data for POST request
    data = {
        'telegram_username': '@test_user',
        'transaction_hash': '357648462a7b472c7ac1123550023a0674aca4849fc385bd67e3a51aeb492564'
    }


    client = APIClient()
    url = reverse('create-subscription')


    # Make POST request
    response = client.post(url, data, format='json')


    assert response.status_code == status.HTTP_404_NOT_FOUND

    subscriptions = Subscription.objects.all()
    assert len(subscriptions) == 0