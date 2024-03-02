from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Plan, Subscription, TelegramUser


class TelegramUserAdmin(UserAdmin):
    model = TelegramUser
    list_display = (
        "telegram_id",
        "chat_id",
        "telegram_username",
        "first_name",
        "last_name",
        "at_private_group",
        "date_joined",
        "is_staff",
    )
    search_fields = (
        "telegram_id",
        "chat_id",
        "telegram_username",
        "first_name",
        "last_name",
    )
    ordering = (
        "telegram_id",
        "chat_id",
        "telegram_username",
        "first_name",
        "last_name",
        "at_private_group",
        "date_joined",
    )
    list_filter = ("is_staff", "is_superuser", "at_private_group")


admin.site.register(TelegramUser, TelegramUserAdmin)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["period", "price"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["customer", "plan", "transaction_hash", "start_date", "end_date"]
