from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from datetime import timedelta
from celery.schedules import crontab

# 设置Django的环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erpsys.settings')

app = Celery('erpsys')

# 从 Django 设置中加载 Celery 配置: 使用Redis作为消息代理
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.update(
    broker_connection_retry_on_startup=True,
)

# 自动从所有已注册的Django app中加载任务
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'backup-data-daily': {
        'task': 'kernel.tasks.task_backup_data',
        'schedule': 30,  # 30秒
    },
}