from django.db import transaction
from django.db.models import F

def can_allocate_resource(resource_id, units_needed=1):
    """
    检查某资源是否能分配给本进程 
    """
    with transaction.atomic():
        # 1. select_for_update() 保证行级锁
        resource = ResourceStatus.objects.select_for_update().get(pk=resource_id)
        # 2. 校验容量
        if resource.current_usage + units_needed <= resource.capacity:
            return True
        else:
            return False

def allocate_resource(resource_id, units_needed=1):
    """
    资源分配
    """
    with transaction.atomic():
        resource = ResourceStatus.objects.select_for_update().get(pk=resource_id)
        # 再次检查并更新
        if resource.current_usage + units_needed > resource.capacity:
            raise RuntimeError("Resource capacity exceeded")
        resource.current_usage = F('current_usage') + units_needed
        resource.save()

def release_resource(resource_id, units_released=1):
    """
    资源释放
    """
    with transaction.atomic():
        resource = ResourceStatus.objects.select_for_update().get(pk=resource_id)
        # 避免出现负数
        resource.current_usage = F('current_usage') - units_released
        if resource.current_usage < 0:
            resource.current_usage = 0
        resource.save()

def is_in_resource_schedule(resource, current_time):
    # 对比 resource 的时间表，若 current_time 在 resource 的可用区间内则 True，否则 False
    # 或者 resourceCalendar.objects.filter(resource=..., start__lte=current_time, end__gte=current_time) ...
    return False