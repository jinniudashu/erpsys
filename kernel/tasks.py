from celery import shared_task
from django_celery_beat.models import PeriodicTask

import subprocess

from kernel.sys_lib import sys_call

@shared_task
def task_backup_data():
    subprocess.run(['python', 'backup.py', 'crontab'])

@shared_task
def execute_sys_call_task(sys_call_name: str, context: dict) -> dict:
    """仅作为异步执行入口"""
    print('执行异步任务：execute_sys_call_task')
    # 这里简化处理，直接将 context 传给 sys_call
    result = sys_call(sys_call_name, **context)  # 调用同步实现
    print('异步任务执行结果：', result)
    return {
        "success": result.success,
        "message": result.message,
        "data": result.data
    }

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
