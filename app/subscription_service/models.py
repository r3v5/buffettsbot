from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import TelegramUserManager


class TelegramUser(AbstractBaseUser, PermissionsMixin):
    chat_id = models.PositiveBigIntegerField(
        unique=True, primary_key=True, null=False, blank=False
    )
    telegram_username = models.CharField(unique=True, blank=False, max_length=256)
    first_name = models.CharField(null=True, blank=True, max_length=256)
    last_name = models.CharField(null=True, blank=True, max_length=256)
    at_private_group = models.BooleanField(null=True, blank=True, default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)

    objects = TelegramUserManager()

    USERNAME_FIELD = "telegram_username"
    REQUIRED_FIELDS = ["chat_id"]

    def __str__(self) -> str:
        return self.telegram_username

    def add_to_private_group(self) -> None:
        self.at_private_group = True
        self.save(update_fields=["at_private_group"])

    def delete_from_private_group(self) -> None:
        self.at_private_group = False
        self.save(update_fields=["at_private_group"])


class Plan(models.Model):
    PERIOD_CHOICES = [
        ("3 minutes", "3 minutes"),
        ("2 days", "2 days"),
        ("1 month", "1 month"),
        ("3 months", "3 months"),
        ("6 months", "6 months"),
        ("1 year", "1 year"),
    ]

    period = models.CharField(unique=True, max_length=20, choices=PERIOD_CHOICES)
    price = models.PositiveIntegerField(null=False, blank=False)

    def __str__(self) -> str:
        return f"{self.period} Plan - ${self.price}"


class Subscription(models.Model):
    customer = models.OneToOneField(
        TelegramUser, on_delete=models.CASCADE, null=False, blank=False
    )
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=False, blank=False)
    transaction_hash = models.CharField(
        unique=True, null=False, blank=False, max_length=256
    )
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=False, blank=False)

    def save(self, *args, **kwargs):
        if self.plan:
            self.set_duration()
            self.set_end_date()
        else:
            raise ValueError("A subscription must have a plan.")

        super().save(*args, **kwargs)

    def set_duration(self):
        if self.plan.period == "3 minutes":
            self.duration = timedelta(minutes=3)

        elif self.plan.period == "2 days":
            self.duration = timedelta(days=2)

        elif self.plan.period == "1 month":
            self.duration = timedelta(days=30)

        elif self.plan.period == "3 months":
            self.duration = timedelta(days=90)

        elif self.plan.period == "6 months":
            self.duration = timedelta(days=180)

        elif self.plan.period == "1 year":
            self.duration = timedelta(days=365)

    def set_end_date(self):
        if self.start_date and self.duration:
            self.end_date = self.start_date + self.duration
