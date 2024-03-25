from celery import Celery
from celery.schedules import crontab
from django.conf import settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forum_v3.settings')

app = Celery('forum_v3')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'user-promotion-every-night': {
        'task': 'forum.tasks.users_promotion',
        'schedule': crontab(hour='4'),
        'options': {'expires': 7200}
    },
    'count-comments-every-one-minute': {
        'task': 'forum.tasks.test_task',
        'schedule': crontab(minute='*/1'),
    },
}
