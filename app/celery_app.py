import os, time
from celery import Celery
from celery.schedules import crontab
from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")


app = Celery("core")
app.config_from_object("django.conf:settings")
app.conf.broker_url = settings.CELERY_BROKER_URL

app.autodiscover_tasks()


@app.task()
def debug_task():
    time.sleep(20)
    print("Hello from debug_task")