from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
import pytest
from subscription_service.models import TelegramUser, Plan, Subscription
from django.utils import timezone
from django.utils.timezone import localtime
import datetime


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
    url = reverse('manage-subscription')


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
    url = reverse('manage-subscription')


    # Make POST request
    response = client.post(url, data, format='json')


    assert response.status_code == status.HTTP_404_NOT_FOUND

    subscriptions = Subscription.objects.all()
    assert len(subscriptions) == 0


@pytest.mark.django_db
def test_valid_get_subscription():
    # Create a TelegramUser
    user = TelegramUser.objects.create(
        telegram_username='@test_user',
        first_name='Test',
        last_name='User'
    )


    # Create a Plan
    plan = Plan.objects.create(
        period='2 days',
        price=19
    )


    # Create a Subscription
    subscription = Subscription.objects.create(
        customer=user,
        plan=plan,
        transaction_hash='0x123456789abcdef',
        start_date=timezone.now(),
        end_date=timezone.now() + datetime.timedelta(days=2)
    )

    # Convert subscription.start_date to the local time zone
    local_start_date = localtime(subscription.start_date)

    # Convert subscription.start_date to a string with the same format as response.data['start_date']
    expected_start_date_str = local_start_date.strftime('%d/%m/%Y %H:%M:%S')

    # Calculate the expected end date and convert it to the local time zone
    expected_end_date = subscription.end_date
    expected_end_date = localtime(expected_end_date)

    # Convert expected_end_date to a string with the same format as response.data['end_date']
    expected_end_date_str = expected_end_date.strftime('%d/%m/%Y %H:%M:%S')

    # Prepare data for POST request
    data = {
        'telegram_username': user.telegram_username
    }


    client = APIClient()
    url = reverse('manage-subscription')


    # Make a GET request with the user's telegram_username
    response = client.get(url, data, format='json')

    print(f'response: {response.data}')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['customer'] == user.telegram_username
    assert response.data['plan'] == plan.period
    assert response.data['price'] == plan.price
    assert response.data['transaction_hash'] == subscription.transaction_hash
    assert response.data['start_date'] == expected_start_date_str
    assert response.data['end_date'] == expected_end_date_str


@pytest.mark.django_db
def test_invalid_get_subscription():
    # Create a TelegramUser
    user = TelegramUser.objects.create(
        telegram_username='@test_user',
        first_name='Test',
        last_name='User'
    )

    # Prepare data for POST request
    data = {
        'telegram_username': user.telegram_username
    }

    client = APIClient()
    url = reverse('manage-subscription')

    # Make a GET request with a non-existent subscription
    response = client.get(url, data, format='json')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'message' in response.data
    assert response.data['message'] == 'Subscription not found'


    # Prepare data for POST request
    data = {
        'telegram_username': '@fox'
    }

    client = APIClient()
    url = reverse('manage-subscription')

    # Make a GET request with a non-existent user's telegram_username
    response = client.get(url, data, format='json')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'message' in response.data
    assert response.data['message'] == 'User not found'