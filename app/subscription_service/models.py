from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import timedelta
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


class Plan(models.Model):
    PERIOD_CHOICES = [
        ('2 days', '2 days'),
        ('1 month', '1 month'),
        ('3 months', '3 months'),
        ('6 months', '6 months'),
        ('1 year', '1 year'),
    ]

    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    price = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.period} Plan - ${self.price}"

    def save(self, *args: dict, **kwargs: dict) -> None:
        if self.period:
            if self.period == '2 days':
                self.price = 19
            elif self.period == '1 month':
                self.price = 150
            elif self.period == '3 months':
                self.price = 400
            elif self.period == '6 months':
                self.price = 600
            elif self.period == '1 year':
                self.price = 1000
        super(Plan, self).save(*args, **kwargs)


class Subscription(models.Model):
    customer = models.OneToOneField(TelegramUser, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    transaction_hash = models.CharField(unique=True, null=False, blank=False, max_length=256, default='0x')
    start_date = models.DateTimeField(default=timezone.localtime)
    end_date = models.DateTimeField(null=True, blank=True)


    def save(self, *args: dict, **kwargs: dict) -> None:
        if self.plan.period == '2 days':
            self.end_date = self.start_date + timedelta(days=2)
        elif self.plan.period == '1 month':
            self.end_date = self.start_date + timedelta(days=30)
        elif self.plan.period == '3 months':
            self.end_date = self.start_date + timedelta(days=90)
        elif self.plan.period == '6 months':
            self.end_date = self.start_date + timedelta(days=180)
        elif self.plan.period == '1 year':
            self.end_date = self.start_date + timedelta(days=365)
        
        super(Subscription, self).save(*args, **kwargs)

        # Update the related user's at_group field to True
        self.customer.at_private_group = True
        self.customer.save(update_fields=['at_private_group'])