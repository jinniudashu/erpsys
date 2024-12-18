from django.db.models import Q, Manager
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.conf import settings

import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import datetime, timedelta
from enum import Enum, auto

from kernel.models import Service, Process, WorkOrder
from kernel.types import ProcessState

from applications.models import *

def sys_call(sys_call_str, **kwargs):
    """
    系统调用入口函数
    """

    def start_one_service(**kwargs):
        # 准备新的服务作业进程参数
        # operation_proc = kwargs['operation_proc']
        # customer = operation_proc.customer
        # current_operator = kwargs['operator']

        # 创建新的服务作业进程
        proc = sys_create_process(**kwargs)

        return proc

    def start_batch_service(**kwargs):
        pass

    def end_service_program(**kwargs):
        pass

    def return_calling_service(**kwargs):
        pass

    def create_batch_process(**kwargs):
        pass
        return f'创建n个服务作业进程'

    def send_back(**kwargs):
        '''
        退单
        '''
        # 获取当前进程的父进程
        proc = kwargs['operation_proc']
        parent_proc = proc.parent_proc
        if parent_proc and parent_proc.service == kwargs['operand_service']:  # 如果父进程服务是规则指定的下一个服务，执行退单
            parent_proc.return_form()
            print('退回表单 至:', parent_proc)

    SysCall = {
        'start_one_service': start_one_service,  # 开始一个服务
        'start_batch_service': start_batch_service,  # 开始多个服务
        'end_service_program': end_service_program,  # 结束服务程序
        'return_calling_service': return_calling_service,  # 返回调用服务
    }

    return SysCall[sys_call_str](**kwargs)

# 创建业务记录
def sys_create_business_record(**kwargs):
    service = kwargs.get('sys_call_operand')
    model_name = service.config['subject']['name']
    params = {
        'label': service.label,
        'pid': kwargs.get('instance'),
        'master': kwargs.get('customer')
    }

    # 创建业务记录
    service_data_instance = eval(model_name).objects.create(**params)

    return service_data_instance

# 创建进程
def sys_create_process(**kwargs):
    service = kwargs.get('sys_call_operand')
    parent = kwargs.get('parent')
    previous = kwargs.get('instance')
    operator = kwargs.get('operator')
    entity_content_object = kwargs.get('entity_content_object')
    state = kwargs.get('state')
    priority = kwargs.get('priority')

    params = {
        'name': service.label,
        'parent': parent,
        'previous': previous,
        'service': service,
        'entity_content_object': entity_content_object,
        'state': ProcessState.NEW.name,
        'priority': 0
    }
    proc = Process.objects.create(**params)
    kwargs['instance'] = proc  # 传递新创建的进程实例

    # 创建业务记录
    business_form_instance = sys_create_business_record(**kwargs)

    # 更新进程表单信息
    proc.form_content_object = business_form_instance
    proc.form_url = f"/{settings.CUSTOMER_SITE_NAME}/applications/{service.config['subject']['name'].lower()}/{business_form_instance.id}/change/"
    proc.save()

# 更新操作员任务列表
def update_task_list(operator, is_public):
    # 当前操作员有权限操作的服务列表
    allowed_services = operator.allowed_services()

    processes = Process.objects.filter(
        state=ProcessState.NEW.name,  # 状态: '新建'
        service__in=allowed_services, # 服务作业进程的服务在allowed_services中
    )
    processes = processes.filter(operator__isnull=True) if is_public else processes.filter(operator=operator)

    label = '公共任务' if is_public else '私有任务'
    work_order = WorkOrder.objects.get(label=label).config

    task_list, work_order_head_filtered = get_represent_list(processes, work_order)

    # 构造channel_message
    if is_public:
        channel_group_name = 'public_task_list'
        channel_message_type = 'send_public_task_list'
        task_list = [{'title': '公共任务', 'task_list': task_list, 'task_head': work_order_head_filtered}]
    else:
        channel_group_name = operator.erpsys_id
        channel_message_type = 'send_private_task_list'
        # 根据schedule_time是否为当天分组：今日安排/本周安排
        task_list = [{'title': '今日安排', 'task_list': task_list, 'task_head': work_order_head_filtered}]

    message = {'type': channel_message_type, 'data': task_list}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(channel_group_name, message)

def update_entity_task_group_list(entity):
    """
    更新实体作业任务分组列表
    """
    # 任务分组条件
    group_condition = [
        {"group_title": "已安排", "state_set": {ProcessState.NEW.name, ProcessState.READY.name}},
        {"group_title": "执行中", "state_set": {ProcessState.RUNNING.name}},
        {"group_title": "暂停", "state_set": {ProcessState.WAITING.name}},
        {"group_title": "已完成", "state_set": {ProcessState.TERMINATED.name}}        
    ]

    work_order = WorkOrder.objects.get(label='实体作业任务清单').config

    task_list = []
    for condition in group_condition:
        processes = entity.get_task_list(condition['state_set'])
        group_tasks, work_order_head_filtered = get_represent_list(processes, work_order)

        task_list.append({
            'group_title': condition['group_title'],
            'task_list': group_tasks,
            'task_head': work_order_head_filtered
        })

    # 发送channel_message给操作员
    channel_message_type = 'send_task_list'
    message = {
        'type': channel_message_type,
        'data': {
            'task_list': task_list,
        }
    }
    channel_group_name = entity.erpsys_id
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(channel_group_name, message)

# 搜索基本信息列表
def search_profiles(search_content, search_text, operator):
    match search_content:
        case 'entity':
            operators = Operator.objects.all()
            instances = operators.filter(
                Q(label__icontains=search_text) |
                Q(name__icontains=search_text) |
                Q(pym__icontains=search_text)
            ) if search_text else operators
            work_order = WorkOrder.objects.get(label='搜索个人表头').config
        case 'service':
            allowed_services = operator.allowed_services()
            services = Service.objects.all()
            instances = services.filter(
                Q(label__icontains=search_text) |
                Q(name__icontains=search_text) |
                Q(pym__icontains=search_text)
            ) if search_text else services
            work_order = WorkOrder.objects.get(label='搜索服务表头').config

    # 构造work-order represent list
    return get_represent_list(instances, work_order)

def get_entity_profile(entity):
    """
    根据实体类型获取对应工单配置
    返回实体基本信息列表和表头
    """
    # 如果entity是Operator实例
    if isinstance(entity, Operator):
        work_order = WorkOrder.objects.get(label='客户Profile表头').config
    else:
        raise ValueError("实体类型不支持")

    work_order_content, work_order_head_filtered = get_represent_list([entity], work_order)
    return {'profile_content': work_order_content[0], 'profile_header': work_order_head_filtered}

# 根据工单配置返回内容列表和表头
def get_represent_list(instances, work_order):
    represent_list = []
    for instance in instances:
        work_order_content = {}
        for work_order_field in work_order:
            work_order_content[work_order_field['name']] = get_nested_field_value(instance, work_order_field['value_expression'])

        represent_list.append(work_order_content)

    # 剔除 work_order 列表中每个字典元素中的value_expression键值对，以免传到前端
    work_order_head_filtered = [{k: v for k, v in item.items() if k != 'value_expression'} for item in work_order]

    return represent_list, work_order_head_filtered

def get_nested_field_value(instance, value_expression):
    """
    递归获取由 '.' 分隔的字段路径中的最末端字段值。
    
    :param instance: Django 模型实例
    :param value_expression: 字符串，django Field字段名的级联组合，使用 '.' 作为分隔符
    :return: 最末端字段的值
    """
    # 分离当前字段和后续字段
    fields = value_expression.split('.', 1)
    current_field = fields[0]
    
    # 获取当前字段的值:
    # 1. 处理Profile反向关联字段, 取第一个对象
    # 2. 如果字段链中还有"."，且当前字段是外键对象，则递归处理
    value = getattr(instance, current_field, None)
    if isinstance(value, models.Manager):
        value = value.all().first()
    if len(fields) > 1 and value is not None:
        return get_nested_field_value(value, fields[1])
    
    return format_field_value(value)

def format_field_value(value):
    """
    格式化字段值，确保返回可序列化的类型
    """
    if isinstance(value, (str, int, float, bool)):
        return value
    elif isinstance(value, datetime):
        return value.strftime('%y-%m-%d %H:%M')
    elif value is None:
        return ''
    else:
        return str(value)

def get_customer_profile_field_value(customer, field_name):
    # 获取客户基本信息表model和系统API字段，用于查询hssc_customer_number和hssc_name
    customer_entity = Operator.objects.get(name='Operator')
    customer_profile_model = customer_entity.base_form.service_set.all()[0].name.capitalize()
    api_fields_map = customer_entity.base_form.api_fields
    hssc_field = api_fields_map.get(field_name, None).get('field_name')

    profile = eval(customer_profile_model).objects.filter(customer=customer).last()

    if profile:
        return getattr(profile, hssc_field)
    else:
        return ''

# 创建定时任务
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
