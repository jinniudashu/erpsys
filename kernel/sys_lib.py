from django.db.models import Q, Manager
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import datetime, timedelta
from enum import Enum, auto
import json
import jsonschema
import hashlib
import re

from kernel.models import Service, Process, WorkOrder, ServiceProgram, ServiceRule, ProcessContextSnapshot
from kernel.types import ProcessState, CONTEXT_SCHEMA

from applications.models import *

# ================ 1. 基础上下文数据结构 ================
class ContextFrame:
    """
    上下文帧
    """
    def __init__(self, process, parent_frame=None):
        self.process = process
        self.parent_frame = parent_frame  # 指向父帧
        self.status = 'ACTIVE'  
        self.local_vars = {}  # 任务执行过程中的局部变量
        self.return_value = None # 任务的返回值
        self.inherited_context = parent_frame.get_inheritable_context() if parent_frame else {}
        self.events_triggered_log = [] # 记录任务触发的事件日志
        self.error_info = None # 如果任务失败，存储错误信息
        # self.resource_management = {} # 描述任务占用的资源，例如打开的文件、数据库连接等
        # self.accounting = {}  # 描述任务所属的账务信息
        # self.scheduling_info = {  # 调度相关信息
        #     "last_scheduled_time": None,
        #     "operator_time_used": 0, # 任务作业节点占用时间
        # }

    def get_inheritable_context(self):
        """获取可继承的上下文数据"""
        return {}

    def to_dict(self):
        """将当前帧序列化为字典"""
        return {
            "process_id": self.process.erpsys_id,
            "status": self.status,
            "local_vars": self.local_vars,
            "inherited_context": self.inherited_context,
            "return_value": self.return_value,
            "error_info": self.error_info,
            "events_triggered_log": self.events_triggered_log
        }

    @classmethod
    def from_dict(cls, data, process_lookup):
        """从字典创建帧实例"""
        process = process_lookup(data["process_id"])
        frame = cls(process)
        frame.status = data["status"]
        frame.local_vars = data["local_vars"]
        frame.inherited_context = data["inherited_context"]
        frame.return_value = data.get("return_value")
        frame.error_info = data.get("error_info")
        frame.events_triggered_log = data.get("events_triggered_log", [])
        return frame

class ContextStack:
    """
    上下文堆栈
    """
    def __init__(self):
        self.frames = []  # 存储所有上下文帧的列表
        
    def push(self, process):
        # 获取当前栈顶帧作为父帧
        parent_frame = self.frames[-1] if self.frames else None
        # 创建新帧，并关联父帧
        frame = ContextFrame(process, parent_frame)

        # 继承服务程序标识
        if parent_frame:
            frame.local_vars['service_program_id'] = parent_frame.local_vars.get('service_program_id')

        # 将新帧压入栈
        self.frames.append(frame)

        return frame
        
    def pop(self):
        return self.frames.pop() if self.frames else None
        
    def current_frame(self):
        return self.frames[-1] if self.frames else None

    def to_dict(self):
        return {
            "frames": [f.to_dict() for f in self.frames],
            # "timestamp": timezone.now().isoformat()
        }

    @classmethod
    def from_dict(cls, data, process_lookup):
        # 验证数据
        jsonschema.validate(instance=data, schema=CONTEXT_SCHEMA)
        stack = cls()
        # frames需要按照顺序重建，由于有parent关系，可以直接按顺序还原
        # 假设frames按栈顺序存储（第0个是底层）
        for frame_data in data["frames"]:
            frame = ContextFrame.from_dict(frame_data, process_lookup)
            stack.frames.append(frame)
        return stack

class ProcessExecutionContext:
    """
    进程执行上下文管理器：
    1. 支持多级调用栈（通过ContextStack保存多个ContextFrame）。
    2. 每次进入和退出时创建新的版本快照（version号），可回溯。
    3. 在存储和恢复时对上下文数据进行JSON Schema验证，确保数据结构一致性。

    待实现优化：
    - 可选择在进入/退出时自动调用某些 SysCall（如cleanup_service）来做资源回收（更新资源状态）等操作
    """
    def __init__(self, process, parent_frame=None, version=None):
        self.process = process
        self.parent_frame = parent_frame
        self.version = version
        self.stack = None

        # 从数据库加载上一次的哈希值
        self._previous_context_hash = self._get_last_context_hash(process) if process else None        
        print('ProcessExecutionContext.__init__ 创建进程上下文：', self.process, self.version)

    def __enter__(self):
        # 如果有父上下文帧，继承父上下文栈
        if self.parent_frame:
            self.stack = self.parent_frame.stack
        else:
            # 创建新的上下文栈
            self.stack = ContextStack()

        frame = self.stack.push(self.process)
        
        # 将进程信息序列化并加入到上下文
        process_info = {
            'process_id': self.process.erpsys_id,
            'process_name': self.process.name,
            'process_state': self.process.state,
            'process_service': self.process.service.name if self.process.service else None,
            'process_operator': str(self.process.operator) if self.process.operator else None,
            'process_priority': self.process.priority,
            'process_created_at': self.process.created_at.isoformat() if self.process.created_at else None,
            'process_updated_at': self.process.updated_at.isoformat() if self.process.updated_at else None
        }
        frame.local_vars.update(process_info)  # 将进程信息添加到上下文中

        # 返回当前帧
        return frame

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 在退出上下文时保存快照（如有变化）
        current_frame = self.stack.current_frame()

        if exc_type is None:
            print('此处添加任务完成处理逻辑：', current_frame.process)            
        else:
            print('此处添加任务异常处理逻辑：', current_frame.process)

        current_hash = self._calculate_context_hash(self.stack)

        if self._previous_context_hash != current_hash:
            print("检测到上下文变化，保存新版本")
            self.version = self._save_context(self.stack, self.process, current_hash)  # 传入当前哈希值
            self._previous_context_hash = current_hash

    def _calculate_context_hash(self, stack):
        """计算并返回当前上下文的哈希值"""
        def normalize(d):
            if isinstance(d, dict):
                return {k: normalize(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [normalize(x) for x in d]
            return d
            
        context_dict = stack.to_dict()
        normalized_dict = normalize(context_dict)
        return hashlib.sha256(json.dumps(normalized_dict, sort_keys=True).encode()).hexdigest()

    def _init_new_stack(self, process):
        """初始化新的上下文栈"""
        # 1. 创建新的上下文栈
        stack = ContextStack()
        stack.push(process)
        frame = stack.current_frame()  # 获取当前帧

        # 2. 初始化参数设置
        if hasattr(self, 'init_params') and self.init_params:
            # 2.1 设置核心参数
            frame.local_vars.update({
                'service_program_id': self.init_params.get('program_entrypoint'),
            })
            
            # 2.2 设置其他自定义参数
            custom_params = {
                k: v for k, v in self.init_params.items() 
                if k not in ['program_entrypoint']
            }
            if custom_params:
                frame.local_vars.update(custom_params)

        # 3. 版本号管理
        latest_version = self._get_latest_version(process)

        return (stack, latest_version + 1)

    def _restore_context(self, process, version=None):
        """
        从DB中恢复上下文栈：
        - 如果指定version，则尝试加载对应的版本。
        - 如果未指定version，加载最新版本。
        - 返回(stack, version)或None如果无历史。
        幂等恢复：恢复不会修改数据库，只读操作。
        """
        qs = ProcessContextSnapshot.objects.filter(process=process)
        if version:
            qs = qs.filter(version=version)
        else:
            qs = qs.order_by('-version')

        snapshot = qs.first()
        if snapshot:
            # 验证数据结构
            data = snapshot.context_data
            # 数据验证在ContextStack.from_dict中进行
            def process_lookup(process_id):
                from kernel.models import Process
                return Process.objects.get(erpsys_id=process_id)

            stack = ContextStack.from_dict(data, process_lookup)
            return stack, snapshot.version
        return None

    def _save_context(self, stack, process, current_hash):
        """保存上下文快照，同时保存哈希值"""
        context_data = stack.to_dict()
        
        # 验证上下文数据结构
        try:
            jsonschema.validate(context_data, CONTEXT_SCHEMA)
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError(f"Invalid context data structure: {str(e)}")
            
        # 获取最新版本号
        latest_version = self._get_latest_version(process)
        new_version = latest_version + 1
        
        # 创建新的快照
        ProcessContextSnapshot.objects.create(
            process=process,
            version=new_version,
            context_data=context_data,
            context_hash=current_hash  # 保存当前哈希值
        )
        
        return new_version

    def _get_last_context_hash(self, process):
        """从数据库获取最后一次的上下文哈希值"""
        last_snapshot = ProcessContextSnapshot.objects.filter(
            process=process
        ).order_by('-version').first()
        return last_snapshot.context_hash if last_snapshot else None

    def _get_latest_version(self, process):
        snapshot = ProcessContextSnapshot.objects.filter(process=process).order_by('-version').first()
        return snapshot.version if snapshot else 0

class ProcessCreator:
    """
    进程创建器：负责创建进程和相关业务记录
    """
    def __init__(self, need_business_record=True):
        """
        Args:
            need_business_record: 是否创建业务记录。某些情况下不需要创建业务记录，
                                  比如用户登录服务进程（登录信息由Django系统记录）
        """
        self.context = None
        self.need_business_record = need_business_record
    
    def prepare_context(self, params):
        print('prepare_context 准备进程上下文：', params)
        """准备进程上下文"""
        self.context = ProcessExecutionContext(None)
        # 初始化基本参数
        self.context.init_params = params  # 存储初始化参数
        return self.context

    def create_business_record(self, process):
        """创建业务记录"""
        model_name = process.service.config['subject']['name']
        model_class = eval(model_name)

        params = {
            'label': process.service.label,
            'pid': process
        }

        # 检查模型是否有master字段
        if hasattr(model_class, 'master'):
            params['master'] = process.entity_content_object

        return model_class.objects.create(**params)

    def create_process(self, kwargs):
        """
        创建新的服务进程，同时继承父上下文。
        Args:
            kwargs: 包含进程创建所需参数的字典。
            parent_frame: 父任务的上下文帧（可选）。
        """        
        # 验证必需参数
        service_rule = kwargs.get('service_rule')
        if not service_rule:
            raise ValueError("service_rule is required")

        # 获取服务程序和服务信息
        service_program = service_rule.service_program
        service = kwargs.get('service')
        operand_service = service_rule.operand_service

        # 获取操作者信息
        operator = kwargs.get('operator')
        if not operator:
            raise ValueError("operator is required")

        # 获取初始化参数
        parent_frame = kwargs.get('parent_frame', None)
        init_params = kwargs.get('init_params', {})

        # 准备进程创建参数
        print('create_process 准备进程创建参数：', kwargs)
        process_params = {
            'name': f"{service_program.label} - {service.label} - {operator}",
            'parent': kwargs.get('parent', None),
            'previous': kwargs.get('previous', None),
            'service': service,
            'entity_content_object': kwargs.get('entity_content_object'),
            'state': kwargs.get('state', ProcessState.NEW.name),
            'operator': operator,
            'priority': kwargs.get('priority', 0),
            "program_entrypoint": service_program.erpsys_id
        }

        # 1. 创建新的 Process 对象
        process = Process.objects.create(**process_params)
        if not process.parent:
            process.parent = process

        # 2. 创建业务记录（如果需要）
        if self.need_business_record:
            business_form_instance = self.create_business_record(process)
            
            # 更新进程表单信息
            process.form_content_object = business_form_instance
            process.form_url = f"/{settings.CUSTOMER_SITE_NAME}/applications/{service.config['subject']['name'].lower()}/{business_form_instance.id}/change/"
            process.save()

        # 3. 创建上下文环境
        with ProcessExecutionContext(process, parent_frame=parent_frame) as frame:
            # 继承父上下文变量（如果有父上下文）
            if parent_frame:
                frame.parent_frame = parent_frame
                frame.local_vars.update(parent_frame.local_vars)

            frame.local_vars.update(init_params)  # 存储初始化参数
        
            # 4. 将服务程序信息写入上下文
            frame.local_vars.update({
                'service_program_id': service_program.erpsys_id,
                'service_rule_id': service_rule.erpsys_id
            })

            # 5. 执行业务规则评估
            evaluator = RuleEvaluator()
            evaluator.evaluate_rules(frame)

        print(f"Process created: {process.id} with context {frame.to_dict()}")
        
        return process

class RuleEvaluator:
    """规则评估器：记录规则评估和执行日志到上下文"""
    
    def evaluate_rules(self, frame: ContextFrame):
        """根据规则评估当前上下文中的业务事件，并记录执行日志到frame.local_vars"""
        eval_context = self._build_evaluation_context(frame)

        service_program_id = frame.process.program_entrypoint
        if not service_program_id:
            raise ValueError("No ServiceProgram ID found in context")
        service_program = ServiceProgram.objects.get(erpsys_id=service_program_id)

        # 限定规则范围
        rules = ServiceRule.objects.filter(
            service_program=service_program,
            service=frame.process.service,
        )

        for rule in rules:
            condition_met = self._evaluate_condition(rule, eval_context)
            if condition_met:
                # frame.local_vars['service_rule_id'] = rule.erpsys_id
                frame.local_vars['operand_process_id'] = frame.process.parent.erpsys_id
                frame.events_triggered_log.append({
                    'rule_id': rule.erpsys_id,
                    'rule_label': rule.label,
                    'event_expression': rule.event.expression,
                    'evaluated_at': timezone.now().isoformat()
                })
                eval_context['service_rule_id'] = rule.erpsys_id
                self._execute_action(rule, eval_context)

    def _build_evaluation_context(self, frame: ContextFrame) -> Dict[str, Any]:
        """构建扁平化的规则评估上下文"""
        # 1. 直接使用frame.local_vars中已有的进程信息
        process_info = frame.local_vars

        # 2. 获取完整的继承上下文链
        def get_inherited_chain(context_dict, depth=0, max_depth=10):
            if not context_dict or depth >= max_depth:
                return {}
            
            result = context_dict.copy()
            parent_context = frame.parent_frame.inherited_context if frame.parent_frame else {}
            parent_data = get_inherited_chain(parent_context, depth + 1)
            
            # 子级上下文优先
            parent_data.update(result)
            return parent_data

        inherited_data = get_inherited_chain(frame.inherited_context)

        # 3. 构建扁平化上下文
        context = {
            **process_info,  # 带前缀的进程信息
            **inherited_data,  # 继承的上下文数据
        }

        print('扁平化上下文：', context)

        return context

    def _evaluate_condition(self, rule: ServiceRule, context: Dict[str, Any]) -> bool:
        """评估规则条件"""
        try:
            print('评估上下文：', context)
            if rule.event and rule.event.expression:
                # 将表达式中的进程相关字段替换为带前缀的形式
                expression = rule.event.expression
                # 替换所有进程相关字段
                field_mappings = {
                    r'\bstate\b': 'process_state',
                    r'\bname\b': 'process_name',
                    r'\bservice\b': 'process_service',
                    r'\boperator\b': 'process_operator',
                    r'\bpriority\b': 'process_priority',
                    r'\bcreated_at\b': 'process_created_at',
                    r'\bupdated_at\b': 'process_updated_at'
                }
                for old_field, new_field in field_mappings.items():
                    expression = re.sub(old_field, new_field, expression)
                print('转换后的表达式：', expression)
                return eval(expression, {}, context)
            return False  # 如果没有事件或表达式，返回False表示条件不满足
        except Exception as e:
            print(f"规则条件评估错误: {e}")
            return False

    def _execute_action(self, rule: ServiceRule, context: Dict[str, Any]):
        if rule.system_instruction:
            sys_call_str = rule.system_instruction.sys_call
            # 1) 将关键的上下文数据序列化后交给 Celery
            # 2) 当前函数不再阻塞等待子进程创建，而是只发送消息
            print('执行系统调用：', sys_call_str, context)
            # 调用 Celery 任务
            from kernel.tasks import execute_sys_call_task
            result = execute_sys_call_task.delay(sys_call_str, context)
            # 这样在此处我们就不会立即创建新进程，也不会产生嵌套上下文。
            # 父上下文在后续 _execute_action 结束后即可退出并保存快照，
            # Worker 那边才会在一个新上下文里创建子进程。

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

class StartService(SysCallInterface):
    """
    启动一个新的服务进程
    """
    def execute(self, **kwargs) -> SysCallResult:
        """
        必需参数：
            - service_rule_id: 服务规则 erpsys_id
            - process_id: 当前过程 erpsys_id
            - operand_service: 要启动的新服务
            - operator: 操作员 (可选，但多数情况下需要)
            - entity_content_object: 新进程的关联业务实体，多数情况下为父进程关联的业务实体
            - ...
        """
        print('执行系统调用 start_one_service：', kwargs)
        # 1. 参数校验
        if "service_rule_id" not in kwargs:
            return SysCallResult(
                success=False,
                message="Missing service_rule_id for start_service",
            )
        service_rule_id = kwargs.get("service_rule_id")
        service_rule = ServiceRule.objects.get(erpsys_id = service_rule_id)
        operand_service = service_rule.operand_service
        
        if not isinstance(operand_service, Service):
            return SysCallResult(False, "operand_service is not a valid Service object")
        
        # 2. 业务逻辑：创建新的Process
        previous_process_id = kwargs.get("process_id")
        previous_process = Process.objects.get(erpsys_id = previous_process_id)
        operator = previous_process.operator
        entity_content_object = previous_process.entity_content_object

        params = {
            "parent": previous_process.parent,
            "previous": previous_process,
            "service_rule": service_rule,
            "service": operand_service,
            "operator": operator,
            "entity_content_object": entity_content_object,
            "name": f"{operand_service.label}",
            "parent_frame": kwargs.get("parent_frame", None),
        }
        print('新服务进程创建参数：', params)

        # 3. 创建新的进程
        creator = ProcessCreator()
        # 获取当前进程的父帧
        proc = creator.create_process(params)

        print(f"新服务进程 created: {proc}")

        # 4. 返回成功信息
        return SysCallResult(
            success=True,
            message="Successfully started one service",
            data={"new_process_id": proc.id}
        )

class CallSubService(SysCallInterface):
    def execute(self, **kwargs) -> SysCallResult:
        """
        调用服务程序
        """
        pass

class CallingReturn(SysCallInterface):
    def execute(self, **kwargs) -> SysCallResult:
        """
        返回调用服务
        """
        pass

class StartIterationService(SysCallInterface):
    def execute(self, **kwargs) -> SysCallResult:
        """
        启动迭代服务
        """
        pass

class StartParallelService(SysCallInterface):
    def execute(self, **kwargs) -> SysCallResult:
        """
        并行启动服务进程
        """
        pass

CALL_REGISTRY = {
    "start_service": StartService,
    "call_sub_service": CallSubService,
    "calling_return": CallingReturn,
    "start_iteration_service": StartIterationService,
    "start_parallel_service": StartParallelService,
    # ... 其它
}    

def sys_call(sys_call_name: str, **kwargs) -> SysCallResult:
    """
    统一系统调用入口
    """
    call_class = CALL_REGISTRY.get(sys_call_name)
    if not call_class:
        return SysCallResult(False, f"Undefined sys_call '{sys_call_name}'")

    try:
        return call_class().execute(**kwargs)
    except Exception as e:
        return SysCallResult(False, f"Exception in sys_call '{sys_call_name}': {e}")

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
        {'title': '入口点名称', 'service_rule_id': '入口点erpsys_id'}
    ]
    '''
    # 使用model_str过滤entity_content_type
    programs = ServiceProgram.objects.filter(manual_start=True, entity_content_type__model=model_str)
    program_entrypoints = []
    for program in programs:
        first_rule = program.servicerule_set.all().order_by('order').first()
        if first_rule:
            program_entrypoints.append({'title': first_rule.service.label, 'service_rule_id': first_rule.erpsys_id})

    return program_entrypoints

# 创建定时任务
# def add_periodic_task(every, task_name):
#     interval_schedule, created = IntervalSchedule.objects.get_or_create(
#         every=every,
#         period=IntervalSchedule.SECONDS,
#     )
#     periodic_task = PeriodicTask.objects.create(
#         name=task_name,
#         interval=interval_schedule,
#         task='kernel.tasks.timer_interrupt',
#         args=json.dumps([task_name]),  # 将任务名作为参数传递
#         one_off=True
#     )
