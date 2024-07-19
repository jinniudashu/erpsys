from django.db.models import Q
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, IntervalSchedule

import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from kernel.models import *
from kernel.types import ProcessState

from applications.models import *
def sys_create_business_record(**kwargs):
    print('running sys_create_service_instance:', kwargs)
    service = kwargs.get('service')
    model_name = service.config['subject']['name']
    params = {
        'label': service.label,
        'pid': kwargs.get('instance'),
    }
    service_data_instance = eval(model_name).objects.create(**params)

    return service_data_instance

def sys_create_process(**kwargs):
    print('running sys_create_process:', kwargs)
    service = kwargs.get('service')
    params = {
        'parent': kwargs.get('instance'),
        'service': service,
        'state': ProcessState.NEW.name,
    }
    proc = Process.objects.create(**params)

    kwargs['instance'] = proc
    business_entity_instance = sys_create_business_record(**kwargs)
    proc.content_object = business_entity_instance
    # proc.url = 
    proc.save()



def add_periodic_task(every, task_name):
    interval_schedule, created = IntervalSchedule.objects.get_or_create(
        every=every,
        period=IntervalSchedule.SECONDS,
    )
    periodic_task = PeriodicTask.objects.create(
        name=task_name,
        interval=interval_schedule,
        task='kernel.tasks.timer_interrupt',
        args=json.dumps([task_name]),  # 将任务名作为参数传递
        one_off=True
    )

def send_channel_message(group_name, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(group_name, message)

def get_task_list(operator):
    task_list ={'public': [1,2,3], 'private': [1,2,3]}
    # 发送channel_message给操作员
    send_channel_message(operator.erpsys_id, {'type': 'send_tasks', 'data': task_list})

def get_customer_profile_field_value(customer, field_name):
    # 获取客户基本信息表model和系统API字段，用于查询hssc_customer_number和hssc_name
    customer_entity = Resource.objects.get(name='Operator')
    customer_profile_model = customer_entity.base_form.service_set.all()[0].name.capitalize()
    api_fields_map = customer_entity.base_form.api_fields
    hssc_field = api_fields_map.get(field_name, None).get('field_name')

    profile = eval(customer_profile_model).objects.filter(customer=customer).last()

    if profile:
        return getattr(profile, hssc_field)
    else:
        return ''

# 更新操作员可见的未分配的服务作业进程
def update_unassigned_procs(operator):
    # 业务逻辑：
    # 先筛选出可行的作业进程available_operation_proc：
    # 1. 服务作业进程的状态为0（未分配）；
    # 2. 服务作业进程的操作员为空；
    # 3. priority_operator为空或者当前操作员隶属于priority_operator；

    # 有权限操作的服务id列表
    # allowed_services = [
    #     service
    #     for service in Service.objects.all
    #     if set(service.role.all()).intersection(set(operator.staff.role.all()))
    # ]

    # allowed_operation_proc = Process.objects.filter(
    #     operator__isnull=True,  # 操作员为空
    #     state__in=[0, 3],  # 状态为0（未分配）或3（挂起）
    #     service__in=allowed_services, # 服务作业进程的服务在allowed_services中
    # )

    # available_operation_proc = allowed_operation_proc.filter(
    #     Q(priority_operator__isnull=True) |  # 优先操作员为空
    #     Q(priority_operator__is_workgroup=True, priority_operator__workgroup__members__in=[operator.staff])  # 当前操作员隶属于优先操作小组
    # )

    # # 根据日期过滤出共享服务（今日待处理服务），过期任务，近期任务(本周待处理服务）
    # today = timezone.now().date()
    # layout_items = [
    #     {'title': '共享服务', 'unassigned_procs': available_operation_proc.filter(scheduled_time__date=today)},
    #     {'title': '过期服务', 'unassigned_procs': available_operation_proc.filter(scheduled_time__date__lt=today)},
    #     # {'title': '近期任务', 'unassigned_procs': available_operation_proc.filter(scheduled_time__date__gt=today, scheduled_time__date__lt=today+datetime.timedelta(days=7))},
    # ]

    # # 构造channel_message items
    # items = []
    # for item in layout_items:
    #     unassigned_procs = []
    #     for proc in item['unassigned_procs']:
    #         hssc_customer_number = get_customer_profile_field_value(proc.customer, 'hssc_customer_number')
    #         hssc_name = get_customer_profile_field_value(proc.customer, 'hssc_name')
    #         unassigned_procs.append({
    #             'id': proc.id,
    #             'service_id': proc.service.id,
    #             'service_label': proc.service.label,
    #             'username': proc.customer.user.username,
    #             'customer_number': hssc_customer_number,
    #             'customer_name': hssc_name,
    #             'charge_staff': proc.customer.charge_staff.label if proc.customer.charge_staff else '',
    #             'acceptance_timeout': proc.acceptance_timeout,
    #             'scheduled_time': proc.scheduled_time.strftime("%y.%m.%d %H:%M"),
    #             'state': proc.state,
    #         })
    #     items.append({'title': item['title'], 'unassigned_procs': unassigned_procs})

    items=[{'title': 'test', 'unassigned_procs': []}]
    # 发送channel_message给操作员
    send_channel_message('unassigned_procs', {'type': 'send_unassigned_procs', 'data': items})

# 更新工作台职员任务列表
def update_staff_todo_list(operator):
    # 根据operator过滤出操作员的今日安排、紧要安排、本周安排
    # layout_items = [
    #     {'title': '今日服务安排', 'todos': Process.objects.staff_todos_today(operator)},
    #     {'title': '紧要服务安排', 'todos': Process.objects.staff_todos_urgent(operator)},
    #     {'title': '本周服务安排', 'todos': Process.objects.staff_todos_week(operator)},
    # ]

    # # 构造channel_message items
    # items = []
    # for item in layout_items:
    #     todos = []
    #     for todo in item['todos']:
    #         hssc_customer_number = get_customer_profile_field_value(todo.customer, 'hssc_customer_number')
    #         hssc_name = get_customer_profile_field_value(todo.customer, 'hssc_name')
    #         todos.append({
    #             'id': todo.id,
    #             'customer_id': todo.customer.id,
    #             'username': todo.customer.user.username,
    #             'customer_number': hssc_customer_number,
    #             'customer_name': hssc_name,
    #             'service_label': todo.service.label,
    #             'service_id': todo.service.id,
    #             'customer_phone': todo.customer.phone,
    #             'customer_address': todo.customer.address,
    #             'completion_timeout': todo.completion_timeout,
    #             'scheduled_time': todo.scheduled_time.strftime("%m.%d %H:%M"),
    #             'state': todo.state,
    #         })
    #     items.append({'title': item['title'], 'todos': todos})

    items=[{'title': 'test', 'todos': []}]
    # 发送channel_message给操作员
    # send_channel_message(operator.erpsys_id, {'type': 'send_staff_todo_list', 'data': items})
    send_channel_message('9', {'type': 'send_staff_todo_list', 'data': items})

# 更新客户服务列表
def update_customer_services_list(customer, history_days=0, history_service_name=''):
    # 判断服务表单是否已经完成，已完成返回空字符串''，否则返回'*'
    def is_service_form_completed(proc):
        content_object = proc.content_object
        # 表单所有字段
        content_object_fields = [field.name for field in content_object._meta.get_fields()]

        # 表单基类字段
        # base_class_fields = [field.name for field in HsscFormModel._meta.get_fields()]
        base_class_fields = []

        # 表单非基类字段
        non_base_class_fields = [field for field in content_object_fields if field not in base_class_fields]
        for field in non_base_class_fields:
            field_value = getattr(content_object, field)
            if field_value is None or field_value == '':
                return '*'

        return ''

    # 已安排服务
    scheduled_services_today = [
        {
            'service_entry': proc.entry,
            'service_label': proc.service.label,
            'service_id': proc.service.id,
            'completion_timeout': proc.completion_timeout,
            'operator_id': proc.operator.id if proc.operator else '0',
            'state': proc.state,
        } for proc in customer.get_scheduled_services('TODAY')
    ]
    scheduled_services_recent = [
        {
            'service_entry': proc.entry,
            'service_label': proc.service.label,
            'service_id': proc.service.id,
            'completion_timeout': proc.completion_timeout,
            'operator_id': proc.operator.id if proc.operator else '0',
            'state': proc.state,
        } for proc in customer.get_scheduled_services('RECENT')
    ]

    # 历史服务
    history_services = []

    # 如果service是安排服务包和安排服务，则获取所安排服务包或服务的label，并添加到service.label后面；否则获取service的label, 并获取服务表单完成标识
    for proc in customer.get_history_services(history_days, history_service_name):
        service_label = proc.service.label
        is_completed = ''

        if proc.service.name == 'CustomerSchedulePackage':
            service_label = service_label + ' -- ' + proc.content_object.servicepackage.label
        elif proc.service.name == 'CustomerSchedule':
            service_label = service_label + ' -- ' + proc.content_object.service.label

            # 获取服务表单完成标识
            is_completed = is_service_form_completed(proc)

        # 构造历史服务列表
        history_services.append({
            'service_entry': proc.entry,
            'service_label': f'{service_label} {is_completed}',
            'service_id': proc.service.id,
        })

    servicesList = {
        'scheduled_services_today': scheduled_services_today,
        'scheduled_services_recent': scheduled_services_recent,
        'history_services': history_services,
    }
    # 发送channel_message给操作员
    send_channel_message(f'customer_services_{customer.id}', {'type': 'send_service_list', 'data': servicesList})
