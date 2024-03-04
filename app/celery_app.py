import os
import time

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")


app = Celery("core")
app.config_from_object("django.conf:settings")
app.conf.broker_url = settings.CELERY_BROKER_URL

# Configure Celery Beat
app.conf.beat_schedule = {
    "add_users_to_private_group": {
        "task": "subscription_service.tasks.add_user_to_private_group",
        "schedule": 10.0,
    }
}

app.autodiscover_tasks()
