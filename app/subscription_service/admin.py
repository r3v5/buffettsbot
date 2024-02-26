from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import TelegramUser, Plan, Subscription


class TelegramUserAdmin(UserAdmin):
    model = TelegramUser
    list_display = (
        'telegram_id',
        'chat_id',
        'telegram_username',
        'first_name',
        'last_name',
        'at_private_group',
        'date_joined',
        'is_staff',
    )
    search_fields = ('telegram_id', 'chat_id', "telegram_username", 'first_name', 'last_name')
    ordering = ('telegram_id', 'chat_id', "telegram_username", 'first_name', 'last_name', 'at_private_group', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'at_private_group')

admin.site.register(TelegramUser, TelegramUserAdmin)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['period', 'price']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'plan', 'format_start_date', 'format_end_date']

    def format_start_date(self, obj: Subscription) -> str:
        return obj.start_date.strftime('%Y-%m-%d %H:%M:%S Moscow Time')
    format_start_date.short_description = 'Start Date (Moscow Time)'
    
    def format_end_date(self, obj: Subscription) -> str:
        return obj.end_date.strftime('%Y-%m-%d %H:%M:%S Moscow Time') if obj.end_date else '-'
    format_end_date.short_description = 'End Date (Moscow Time)'