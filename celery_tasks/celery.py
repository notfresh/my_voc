from __future__ import absolute_import, unicode_literals
from celery import Celery


app = Celery('celery_tasks', broker='pyamqp://guest@localhost//', backend='amqp://', include=['celery_tasks.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
    worker_max_tasks_per_child=1,
    broker_pool_limit=None
)
