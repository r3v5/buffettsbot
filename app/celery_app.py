import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")


app = Celery("core")
app.config_from_object("django.conf:settings")
app.conf.broker_url = settings.CELERY_BROKER_URL

# Configure Celery Beat
app.conf.beat_schedule = {
    "find_new_subscriptions": {
        "task": "subscription_service.tasks.find_new_subscriptions",
        "schedule": 10.0,
    },
    "delete_expired_subscriptions": {
        "task": "subscription_service.tasks.delete_expired_subscriptions",
        "schedule": 10.0,
    },
    "notify_about_expiring_subscriptions_1_day": {
        "task": "subscription_service.tasks.notify_about_expiring_subscriptions_1_day",
        "schedule": crontab(minute=0, hour=0),
    },
    "notify_about_expiring_subscriptions_3_days": {
        "task": "subscription_service.tasks.notify_about_expiring_subscriptions_3_days",
        "schedule": crontab(minute=0, hour=0),
    },
    "notify_about_expiring_subscriptions_7_days": {
        "task": "subscription_service.tasks.notify_about_expiring_subscriptions_7_days",
        "schedule": crontab(minute=0, hour=0),
    },
    "test_notify": {
        "task": "subscription_service.tasks.test_notify",
        "schedule": 30.0,
    },
}

app.autodiscover_tasks()
