from celery import shared_task
from django_celery_beat.models import PeriodicTask

@shared_task
def timer_interrupt(task_name):
    # get timer.pid
    # get pid.stack
    # get pid.stack.pc
    # execute pid.stack.pc
    try:
        task = PeriodicTask.objects.get(name=task_name)
        # 现在你可以访问任务实例的所有字段
        print("Task arguments:", task.args)
    except PeriodicTask.DoesNotExist:
        print("Task not found")    
    return task_name