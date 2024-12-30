from django.db.models import Q, Manager
from django.utils import timezone
from django.conf import settings
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import datetime, timedelta
from enum import Enum, auto
import json

from kernel.models import Service, Process, WorkOrder, ServiceProgram
from kernel.types import ProcessState

from applications.models import *

class SysCallResult:
    def __init__(self, success: bool, message: str = "", data: Optional[dict] = None):
        self.success = success
        self.message = message
        self.data = data or {}

    def __repr__(self):
        return f"<SysCallResult success={self.success} message={self.message} data={self.data}>"

class SysCallInterface(ABC):
    """
    系统调用抽象接口
    """
    @abstractmethod
    def execute(self, **kwargs) -> SysCallResult:
        """
        执行系统调用。kwargs 里应包含所需的关键参数，如 process, operand_service, operator, context 等。
        返回 SysCallResult。
        进一步可做：
        - 遇到业务错误（如参数非法）可以抛自定义异常，再由上层捕获并写日志到上下文
        """
        pass

class StartOneServiceCall(SysCallInterface):
    """
    启动一个新的服务进程
    """
    def execute(self, **kwargs) -> SysCallResult:
        """
        必需参数：
            - process: 当前过程
            - operand_service: 要启动的新服务
            - operator: 操作员 (可选，但多数情况下需要)
            - entity_content_object: 新进程的关联业务对象
            - ...
        """
        # 1. 参数校验
        if "operand_service" not in kwargs:
            return SysCallResult(
                success=False,
                message="Missing operand_service for start_one_service",
            )
        operand_service = kwargs["operand_service"]
        if not isinstance(operand_service, Service):
            return SysCallResult(False, "operand_service is not a valid Service object")
        
        # 2. 业务逻辑：创建新的Process
        process = kwargs.get("process")
        operator = kwargs.get("operator")
        entity_object = kwargs.get("entity_content_object")

        new_proc = Process.objects.create(
            parent=process,
            service=operand_service,
            operator=operator,
            entity_content_object=entity_object,
            state=ProcessState.NEW.name,
            name=f"{operand_service.label}",
        )
        # 3. 返回成功信息
        return SysCallResult(
            success=True,
            message="Successfully started one service",
            data={"new_process_id": new_proc.id}
        )

class EndServiceProgramCall(SysCallInterface):
    def execute(self, **kwargs) -> SysCallResult:
        """
        标记当前服务程序结束，或做后续清理
        """
        process = kwargs.get("process")
        if not process:
            return SysCallResult(False, "No process provided")

        # 这里根据您的业务逻辑判断结束条件
        # 示例：将 process 设置为 TERMINATED
        process.state = ProcessState.TERMINATED.name
        process.end_time = timezone.now()
        process.save()

        return SysCallResult(True, f"ServiceProgram ended for process {process.id}")

class StartBatchServiceCall(SysCallInterface):
    def execute(self, **kwargs) -> SysCallResult:
        """
        批量启动服务进程
        """
        pass

class CallServiceProgramCall(SysCallInterface):
    def execute(self, **kwargs) -> SysCallResult:
        """
        调用服务程序
        """
        pass

class ReturnCallingServiceCall(SysCallInterface):
    def execute(self, **kwargs) -> SysCallResult:
        """
        返回调用服务
        """
        pass

CALL_REGISTRY = {
    "start_one_service": StartOneServiceCall,
    "start_batch_service": StartBatchServiceCall,
    "end_service_program": EndServiceProgramCall,
    "call_service_program": CallServiceProgramCall,
    "return_calling_service": ReturnCallingServiceCall,
    # ... 其它
}    

def sys_call(sys_call_name: str, **kwargs) -> SysCallResult:
    """
    统一系统调用入口
    """
    call_class = CALL_REGISTRY.get(sys_call_name)
    if not call_class:
        return SysCallResult(False, f"Undefined sys_call '{sys_call_name}'")

    call_instance = call_class()
    
    try:
        result = call_instance.execute(**kwargs)
        return result
    except Exception as ex:
        # 统一异常处理
        return SysCallResult(False, f"Exception in sys_call '{sys_call_name}': {ex}")

def old_sys_call(sys_call_str, **kwargs):
    """
    系统调用入口函数
    """

    def start_one_service(**kwargs):
        """
        启动
        """
        # 准备新的服务作业进程参数
        # operation_proc = kwargs['operation_proc']
        # customer = operation_proc.customer
        # current_operator = kwargs['operator']

        # ================ 分别处理人工任务类型和系统任务类型 ================

        # 创建新的服务作业进程
        proc = sys_create_process(**kwargs)

        return proc

    def start_batch_service(**kwargs):
        """
        批量启动
        """
        # ================ 分别处理人工任务类型和系统任务类型 ================
        pass

    def end_service_program(**kwargs):
        """"
        结束
        """
        pass

    def call_service_program(**kwargs):
        """
        调用
        """
        # 获取当前进程的父进程
        proc = kwargs['operation_proc']
        parent_proc = proc.parent_proc
        if parent_proc and parent_proc.service == kwargs['operand_service']:  # 如果父进程服务是规则指定的下一个服务，执行调用
            parent_proc.call_service_program()
            print('调用服务程序 至:', parent_proc)

    def return_calling_service(**kwargs):
        """"
        返回
        """
        pass

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
    service_rule = kwargs.get('service_rule', None)
    if not service_rule :
        raise ValueError("service_rule is required")
    service_program = service_rule.service_program
    service = service_rule.service
    parent = kwargs.get('parent')
    previous = kwargs.get('instance')
    operator = kwargs.get('operator')
    entity_content_object = kwargs.get('entity_content_object', None)
    state = kwargs.get('state', ProcessState.NEW.name)
    priority = kwargs.get('priority', 0)

    params = {
        'name': f"{service_program.label} - {service_rule.service.label} - {operator}",
        'parent': parent,
        'previous': previous,
        'service': service,
        'entity_content_object': entity_content_object,
        'state': state,
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

    # 将服务程序信息写入上下文
    context_stack = ContextStack()
    frame = context_stack.push(proc)
    frame.local_vars['service_program_id'] = service_program.erpsys_id
    frame.local_vars['service_rule_id'] = service_rule.erpsys_id

    return proc

# ================ 待整理吸收：分别处理人工任务类型和系统任务类型 ================
# # 1. 创建人工任务
# def create_manual_task(process: Process):
#     with ProcessContextManager(process) as context:
#         # 创建待办事项
#         task_item = create_task_item(process)
#         # 设置状态为等待
#         context.status = 'WAITING'
#         # 挂起当前执行
#         suspend_execution(context)
#         return task_item

# # 2. 人工处理过程（在系统外部进行）
# # 系统接受到任务表单保存信号后，调用此函数恢复执行
# # 3. 恢复执行
# def resume_manual_task(task_item, result):
#     process = task_item.process
#     with ProcessContextManager(process) as context:
#         # 恢复上下文
#         restore_context(context)
#         # 设置处理结果
#         context.return_value = result
#         context.status = 'COMPLETED'
#         # 触发规则评估和后续处理
#         handle_task_completion(context)

# # 3. 自动任务执行
# def execute_automatic_task(process: Process):
#     with ProcessContextManager(process) as context:
#         # 执行实际任务
#         result = _do_execute_process(process)
#         context.return_value = result
#         return result

# ========================================================

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

def get_program_entrypoints(model_str):
    '''
    获取所有服务程序的入口点
    参数:
    model_str: 模型名字符串小写
    返回格式:
    [
        {'title': '入口点名称', 'id': '入口点erpsys_id'}
    ]
    '''
    # 使用model_str过滤entity_content_type
    programs = ServiceProgram.objects.filter(entity_content_type__model=model_str)
    program_entrypoints = []
    for program in programs:
        first_rule = program.servicerule_set.all().order_by('order').first()
        if first_rule:
            program_entrypoints.append({'title': first_rule.service.label, 'id': first_rule.erpsys_id})

    return program_entrypoints

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
