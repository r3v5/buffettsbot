from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class TelegramUserManager(BaseUserManager):
    def create_user(
            self, 
            telegram_id: int, 
            chat_id: int, 
            telegram_username: str, 
            first_name: str,
            last_name: str,
            at_private_group: bool,
            password=None) -> 'TelegramUser':
        if not telegram_id and not chat_id and not telegram_username:
            raise ValueError('telegram_id field must be set\nchat_id field must be set\ntelegram_username field must be set')
        user = self.model(telegram_id=telegram_id, chat_id=chat_id, telegram_username=telegram_username, first_name=first_name, last_name=last_name, at_private_group=at_private_group)
        user.set_password(password)
        user.save(using=self._db)
        return user
    

    def create_superuser(self, telegram_username: str, password=None) -> 'TelegramUser':
        user = self.create_user(
            telegram_id=None, 
            chat_id=None, 
            telegram_username=telegram_username,
            password=password,
            first_name='', 
            last_name='', 
            at_private_group=True
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user