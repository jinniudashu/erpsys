from celery import shared_task

@shared_task
def timer_interrupt():
    # get timer.pid
    # get pid.stack
    # get pid.stack.pc
    # execute pid.stack.pc
    return 'execute pid.stack.pc'