from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from datetime import timedelta

# 设置Django的环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erpsys.settings')

app = Celery('erpsys')

# 使用Redis作为消息代理
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动从所有已注册的Django app中加载任务
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'add-every-5-seconds': {
        'task': 'kernel.tasks.add',
        'schedule': timedelta(seconds=5),  # 每5秒执行一次
        'args': (12, 16)
    },
}
