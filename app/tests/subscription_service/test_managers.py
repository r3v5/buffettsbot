import pytest
from django.contrib.auth import get_user_model

from subscription_service.models import TelegramUser

UserModel = get_user_model()


@pytest.mark.django_db
class TestTelegramUserManager:

    def test_create_user(self):
        # Test creating a regular user
        user = TelegramUser.objects.create_user(
            chat_id=123456,
            telegram_username="test_user",
            first_name="John",
            last_name="Doe",
            at_private_group=False,
            password=None,
        )
        assert user.telegram_username == "test_user"
        assert user.at_private_group is False

    def test_create_superuser(self):
        # Test creating a superuser
        superuser = TelegramUser.objects.create_superuser(
            chat_id=789012, telegram_username="admin", password="admin123"
        )
        assert superuser.is_superuser is True
        assert superuser.is_staff is True
        # Add more assertions as needed

    def test_create_user_invalid_input(self):
        # Test creating a user with invalid input
        with pytest.raises(ValueError):
            TelegramUser.objects.create_user(
                chat_id=None,
                telegram_username=None,
                first_name="John",
                last_name="Doe",
                at_private_group=False,
                password="password123",
            )
