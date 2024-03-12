import pytest
from django.urls import resolve, reverse

from subscription_service.views import SubscriptionAPIView, TelegramUserAPIView


@pytest.mark.django_db
def test_create_user_url():
    resolver = reverse("create-telegram-user")
    assert resolve(resolver).func.view_class == TelegramUserAPIView


@pytest.mark.django_db
def test_manage_subscription_url():
    resolver = reverse("manage-subscription")
    assert resolve(resolver).func.view_class == SubscriptionAPIView
