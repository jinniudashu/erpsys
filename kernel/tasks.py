from celery import shared_task
from django_celery_beat.models import PeriodicTask

import subprocess

@shared_task
def task_backup_data():
    subprocess.run(['python', 'backup.py', 'crontab'])

@shared_task
def timer_interrupt(task_name):
    # get timer.pid
    # get pid.stack
    # get pid.stack.pc
    # execute pid.stack.pc
    try:
        task = PeriodicTask.objects.get(name=task_name)
        print("Task arguments:", task.args)
    except PeriodicTask.DoesNotExist:
        print("Task not found")    
    return task