import pytest
from django.urls import resolve, reverse
from subscription_service.views import TelegramUserAPIView


@pytest.mark.django_db
def test_create_user_url():
    resolver = reverse('create-telegram-user')
    assert resolve(resolver).func.view_class == TelegramUserAPIView