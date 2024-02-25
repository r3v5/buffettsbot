from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .managers import TelegramUserManager


class TelegramUser(AbstractBaseUser, PermissionsMixin):
    telegram_id = models.PositiveBigIntegerField(null=True)
    chat_id = models.PositiveBigIntegerField(null=True)
    telegram_username = models.CharField(unique=True, blank=False, max_length=256)
    first_name = models.CharField(null=True, blank=True, max_length=256)
    last_name = models.CharField(null=True, blank=True, max_length=256)
    at_private_group = models.BooleanField(null=True, blank=True, default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)

    objects = TelegramUserManager()

    USERNAME_FIELD = 'telegram_username'
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return self.telegram_username   
