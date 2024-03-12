from django.contrib import admin

from .models import Plan, Subscription, TelegramUser


class TelegramUserAdmin(admin.ModelAdmin):
    model = TelegramUser
    list_display = (
        "chat_id",
        "telegram_username",
        "first_name",
        "last_name",
        "at_private_group",
        "date_joined",
        "is_staff",
        "is_superuser",
    )
    search_fields = (
        "chat_id",
        "telegram_username",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
    )
    ordering = (
        "chat_id",
        "telegram_username",
        "first_name",
        "last_name",
        "at_private_group",
        "date_joined",
        "is_staff",
        "is_superuser",
    )
    list_filter = ("is_staff", "is_superuser", "at_private_group")


admin.site.register(TelegramUser, TelegramUserAdmin)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["period", "price"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["customer", "plan", "transaction_hash", "start_date", "end_date"]
