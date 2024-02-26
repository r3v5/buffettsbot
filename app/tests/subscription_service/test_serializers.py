import pytest
from subscription_service.serializers import TelegramUserSerializer


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