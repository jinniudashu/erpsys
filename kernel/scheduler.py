from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.forms.models import model_to_dict
from django.utils import timezone
from django.conf import settings

from datetime import timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json
import jsonschema

from kernel.signals import ux_input_signal
from kernel.models import Process, Service, ServiceProgram, ServiceRule, Operator, ProcessContextSnapshot
from kernel.types import ProcessState, CONTEXT_SCHEMA
from kernel.sys_lib import sys_call

# ================ 1. 基础上下文数据结构 ================
class ContextFrame:
    def __init__(self, process, parent_frame=None):
        self.process = process
        self.parent_frame = parent_frame  # 指向父帧
        self.status = 'ACTIVE'  
        self.local_vars = {}  # 任务执行过程中的局部变量
        self.return_value = None # 任务的返回值
        self.error_info = None # 如果任务失败，存储错误信息
        self.program_pointer = None  # 服务程序计数器，指向服务执行到的位置
        self.registers = {}  # 用于存储任务执行过程中的操作员前端上下文数据，类似于 CPU 寄存器
        self.resource_management = {} # 描述任务占用的资源，例如打开的文件、数据库连接等
        self.accounting = {}  # 描述任务所属的账务信息
        self.scheduling_info = {  # 调度相关信息
            "last_scheduled_time": None,
            "operator_time_used": 0, # 任务作业节点占用时间
        }

        if parent_frame:
            self.inherited_context = parent_frame.get_inheritable_context()
        else:
            self.inherited_context = {}

    def get_inheritable_context(self):
        """获取可继承的上下文数据"""
        return {
            'resource_management': self.resource_management,  # 资源管理信息可继承
            'accounting': self.accounting,  # 账务信息可继承
            'scheduling_info': self.scheduling_info,  # 调度信息可继承
        }

    def to_dict(self):
        """将当前帧序列化为字典"""
        return {
            "process_id": self.process.id,
            "status": self.status,
            "local_vars": self.local_vars,
            "inherited_context": self.inherited_context,
            "return_value": self.return_value,
            "error_info": self.error_info,
            "program_pointer": self.program_pointer,
            "registers": self.registers,
            "resource_management": self.resource_management,
            "accounting": self.accounting,
            "scheduling_info": self.scheduling_info
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
        frame.program_pointer = data.get("program_pointer")
        frame.registers = data.get("registers", {})
        frame.resource_management = data.get("resource_management", {})
        frame.accounting = data.get("accounting", {})
        frame.scheduling_info = data.get("scheduling_info", {
            "last_scheduled_time": None,
            "operator_time_used": 0
        })
        return frame

class ContextStack:
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
            "timestamp": timezone.now().isoformat()
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

# ================ 2. 进程上下文管理 ================
class ProcessExecutionContext:
    """
    进程执行上下文管理器：
    1. 支持多级调用栈（通过ContextStack保存多个ContextFrame）。
    2. 每次进入和退出时创建新的版本快照（version号），可回溯。
    3. 在存储和恢复时对上下文数据进行JSON Schema验证，确保数据结构一致性。
    4. 恢复操作是幂等的，多次恢复同一版本不会改变数据，只读不写，直到上下文更新才产生新版本。

    进一步可做：
    - 可选择在进入/退出时自动调用某些 SysCall（如cleanup_service）来做资源回收（更新资源状态）等操作
    """
    def __init__(self, process, version=None):
        self.process = process
        self.version = version
        self.stack = None

    def __enter__(self):
        # 首先恢复上下文，如果version指定就恢复指定版本，否则恢复最新版本
        self.stack, self.version = self._restore_context(self.process, self.version) or self._init_new_stack(self.process)
        return self.stack.current_frame()

    def __exit__(self, exc_type, exc_val, exc_tb):
        frame = self.stack.current_frame()
        if exc_type is None:
            self._handle_completion(frame)
        else:
            self._handle_exception(frame, exc_val)

        # Detect changes in context using hash comparison
        current_context_hash = hash(json.dumps(self.stack.to_dict(), sort_keys=True))
        if getattr(self, '_previous_context_hash', None) != current_context_hash:
            self.version = self._save_context(self.stack, self.process)
            self._previous_context_hash = current_context_hash

    def _init_new_stack(self, process):
        stack = ContextStack()
        stack.push(process)
        # 初始版本为1或基于已存在的最高版本+1
        latest_version = self._get_latest_version(process)
        return (stack, latest_version + 1)

    def _restore_context(self, process, version=None):
        """
        从DB中恢复上下文栈:
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
            def process_lookup(pid):
                from kernel.models import Process
                return Process.objects.get(id=pid)

            stack = ContextStack.from_dict(data, process_lookup)
            return stack, snapshot.version
        return None

    def _save_context(self, stack, process):
        """
        将当前栈存储为新版本快照。版本号=旧版本号+1
        """
        latest_version = self._get_latest_version(process)
        new_version = latest_version + 1
        context_data = stack.to_dict()
        # 验证数据前再保存，确保数据符合schema
        jsonschema.validate(instance=context_data, schema=CONTEXT_SCHEMA)

        with transaction.atomic():
            ProcessContextSnapshot.objects.select_for_update().create(
                process=process,
                version=new_version,
                context_data=context_data
            )
        return new_version

    def _get_latest_version(self, process):
        snapshot = ProcessContextSnapshot.objects.filter(process=process).order_by('-version').first()
        return snapshot.version if snapshot else 0

    def _handle_completion(self, frame):
        """
        处理完成逻辑，比如当任务完成时是否需要更新frame状态或写入return_value。
        此处只是示例，实际可根据业务需求调整。
        """
        print('此处添加任务完成处理逻辑：', frame.process)
        # if frame.return_value:
        #     # 如果有返回值，根据业务逻辑更新进程状态
        #     frame.process.state = "TERMINATED"
        #     frame.process.save()

    def _handle_exception(self, frame, exception):
        """
        处理异常，设置frame状态并记录错误信息
        """
        print('此处添加任务异常处理逻辑：', frame.process)
        # frame.status = 'ERROR'
        # frame.return_value = {'error': str(exception)}
        # # 根据业务需求更新Process状态
        # frame.process.state = "ERROR"
        # frame.process.save()

# ================ 3. 规则评估 ================
class RuleEvaluator:
    """规则评估器：记录规则评估和执行日志到上下文"""
    
    def evaluate_rules(self, frame: ContextFrame):
        """评估当前上下文中的规则，并记录执行日志到frame.local_vars"""
        eval_context = self._build_evaluation_context(frame)

        service_program_id = frame.local_vars.get('service_program_id')
        if not service_program_id:
            raise ValueError("No ServiceProgram ID found in context")
        service_program = ServiceProgram.objects.get(erpsys_id=service_program_id)

        # 限定规则范围
        rules = ServiceRule.objects.filter(
            service_program=service_program,
            service=frame.process.service,
        )
        
        # 确保local_vars中有rules_log列表
        if 'rules_log' not in frame.local_vars:
            frame.local_vars['rules_log'] = []

        for rule in rules:
            rule_log_entry = {
                'rule_id': rule.id,
                'rule_label': rule.label,
                'event_expression': rule.event.expression if rule.event else None,
                'evaluated_at': timezone.now().isoformat(),
                'condition_result': False,
                'action_executed': False,
                'error': None
            }
            try:
                condition_met = self._evaluate_condition(rule, eval_context)
                rule_log_entry['condition_result'] = condition_met
                if condition_met:
                    self._execute_action(rule, eval_context)
                    rule_log_entry['action_executed'] = True
            except Exception as e:
                rule_log_entry['error'] = str(e)
                # 保留问题：是否需要transition_to
                # if frame:
                #     frame.transition_to(ProcessState.ERROR, str(e))
            finally:
                # 无论成功失败，将日志记录追加到rules_log中
                frame.local_vars['rules_log'].append(rule_log_entry)


    def _build_evaluation_context(self, frame: ContextFrame) -> Dict[str, Any]:
        """构建规则评估上下文"""
        context = {
            'process': frame.process,
            'result': frame.return_value,
            'local_vars': frame.local_vars,
            'inherited_context': frame.inherited_context,
            'customer': frame.process.entity_content_object,
            'current_time': timezone.now(),
        }
        return context

    def _evaluate_condition(self, rule: ServiceRule, context: Dict[str, Any]) -> bool:
        """评估规则条件"""
        try:
            if rule.event and rule.event.expression:
                return eval(rule.event.expression, {}, context)
            return False  # 如果没有事件或表达式，返回False表示条件不满足
        except Exception as e:
            print(f"规则条件评估错误: {e}")
            return False

    def _execute_action(self, rule: ServiceRule, context: Dict[str, Any]):
        if rule.system_instruction:
            sys_call_str = rule.system_instruction.sys_call
            context['sys_call_operand'] = rule.operand_service
            sys_call(sys_call_str, **context)

# ================ 4. 使用规则评估器的调度器或入口函数 ================
def execute_process(process: Process):
    """任务执行的统一入口"""
    with ProcessExecutionContext(process) as frame:
        # 在任务执行前后评估规则
        evaluator = RuleEvaluator()
        evaluator.evaluate_rules(frame)

@receiver(user_logged_in)
def on_user_login(sender, user, request, **kwargs):
    """
    处理用户登录信号
    登录后创建一个登录进程，state=TERMINATED
    标准业务逻辑：设置操作员资源状态为可用
    """
    if request.path == f'/{settings.CUSTOMER_SITE_NAME}/login/':  # 应用登录
        # 创建一个登录进程, state=TERMINATED
        operator = Operator.objects.get(user=user)
        params = {
            'service': Service.objects.get(name='user_login'),
            'entity_content_object': operator,
            'operator': operator,
            'state': ProcessState.TERMINATED.name,
            'priority': 0
        }
        Process.objects.create(**params)

@receiver(post_save, sender=Process, dispatch_uid="post_save_process")
def on_process_save(sender, instance: Process, created: bool, **kwargs):
    """
    处理进程保存信号
    构造业务上下文，根据业务规则评估业务状态，调度作业
    """
    # context = preprocess_context(instance, created)
    if created:
        print(f"进程创建: {instance}")
        # 处理创建事件
        with ProcessExecutionContext(instance) as frame:
            frame.local_vars['created_at'] = str(instance.created_time)

    if instance.state == ProcessState.READY.name:
        print(f"进程状态变更: {instance}")
        # 处理状态变更事件
        with ProcessExecutionContext(instance) as frame:
            frame.local_vars['state_changed'] = f"状态更新为 {instance.state}"
            frame.local_vars['state_ready'] = True
            # frame.local_vars['state_changed'] = f"{old_state} -> {new_state}"

    if instance.state == ProcessState.TERMINATED.name:
        print(f"进程完成: {instance}")
        # 处理完成事件
        with ProcessExecutionContext(instance) as frame:
            frame.return_value = {'message': 'Process completed successfully'}

    # 如果有异常状态处理
    if instance.state == ProcessState.ERROR.name:
        print(f"进程异常信号: {instance}")
        with ProcessExecutionContext(instance) as frame:
            frame.status = 'ERROR'
            frame.return_value = {'error': str(instance.error)}
    
    # 从当前进程上下文中获取服务程序，如果没找到，使用系统默认的标准服务程序
    service_program = ServiceProgram.objects.get(erpsys_id=instance.program_entrypoint)

    # 根据服务程序，检查规则
    rules = ServiceRule.objects.filter(service_program=service_program, service=instance.service)
    for rule in rules:
        if eval(rule.event.expression, {}, context):
            print("发生--", rule.service, rule.event, "执行->", rule.system_instruction, rule.operand_service)
            sys_call_str = rule.system_instruction.sys_call
            context['sys_call_operand'] = rule.operand_service
            sys_call(sys_call_str, **context)

    # *************************************************
    # 检查表单内服务指令，立即执行/计划执行
    # *************************************************

@receiver(ux_input_signal)
def on_ux_input(**kwargs):
    """接收人工指令调度"""
    """
    系统外部输入中断信号，需要即时响应
    优先级最高
    """
    pass

def on_timer_signal(**kwargs):
    # 将Celery的定时任务信号转译为业务事件
    """接收定时信号调度"""
    """
    操作系统时钟中断信号，
    可检查各业务进程状态，启动提醒服务进程、分析报告服务进程等
    优先级最低
    """
    # ??? 每分钟执行一次，查询所有定时规则，检查是否满足条件，满足则执行SOP
    print("timer_signal was received.", kwargs)

# def preprocess_context(instance: Process, created: bool) -> dict:
#     """预处理上下文"""
#     process_context = model_to_dict(instance)
#     model_context = model_to_dict(instance.form_content_object) if instance.form_content_object else {}
#     # control_context = instance.control_context if instance.control_context else {}
#     # schedule_context = instance.schedule_context if instance.schedule_context else {}
#     # context = {**model_context, **process_context, **control_context, **schedule_context}
#     context = {**model_context, **process_context}
#     context.update({"instance": instance})
#     context.update({"entity_content_object": instance.entity_content_object})
#     context.update({"created": created, "timezone_now": timezone.now()})
#     context.update({"parent": instance.parent})

#     return context

def scheduling_loop():
    """
    定时任务，每隔一段时间（30秒），就执行一次调度过程。
    """
    with transaction.atomic():
        # 1. 搜集所有处于 READY 状态的进程
        ready_processes = Process.objects.select_for_update().filter(
            state=ProcessState.READY.name
        ).order_by('-priority', 'created_time')

        # 2. 根据资源可用情况，决定哪些进程能进入 RUNNING，哪些进程要保持 WAITING
        for proc in ready_processes:
            # 检查对应资源是否可用
            if attempt_resource_allocation(proc):
                # attempt_resource_allocation(proc) 内部会做：
                # 解析 proc.control_context 里的资源需求；
                # select_for_update() 获取锁；
                # 判断剩余容量与排班；
                # 成功则更新 current_usage 并返回 True，否则 False。

                # 切换状态为 RUNNING
                proc.state = ProcessState.RUNNING.name
                proc.start_time = timezone.now()
                proc.save()
            elif proc.operator is None:
                # 如果无法分配资源，则进入 WAITING
                proc.state = ProcessState.WAITING.name
                proc.save()

        # 3. 对于已经 RUNNING 的进程，检查是否已经完成或需要释放资源
        running_processes = Process.objects.filter(state=ProcessState.RUNNING.name)
        for proc in running_processes:
            # 如果满足某些完成条件(自己判断) or 超时 or 出错
            if check_if_process_done(proc):
                with transaction.atomic():
                    release_all_resources_for_process(proc)
                    proc.state = ProcessState.TERMINATED.name
                    proc.end_time = timezone.now()
                    proc.save()
            # 否则继续保持 RUNNING

        # 4. 其他额外逻辑（异常检测/重试等），省略...

def attempt_resource_allocation(process):
    resource = process.control_context.get('resource')
    if resource and resource['available'] > 0:
        resource['available'] -= 1
        process.control_context.update({'resource': resource})
        process.save()
        return True
    return False

# @dataclass
# class ProcessContext:
#     """Process execution context with enhanced state tracking"""
#     process_id: int
#     state: ProcessState
#     start_time: Optional[timezone.datetime] = None
#     end_time: Optional[timezone.datetime] = None
#     error_message: Optional[str] = None
#     retry_count: int = 0
#     max_retries: int = 3
#     timeout_seconds: int = 300  # 5 minutes default timeout
#     priority: int = 0
#     local_vars: Dict[str, Any] = None
#     parent_context: Optional['ProcessContext'] = None

#     def __post_init__(self):
#         if self.local_vars is None:
#             self.local_vars = {}
#         if self.state == ProcessState.NEW:
#             self.start_time = timezone.now()

#     def transition_to(self, new_state: ProcessState, error: Optional[str] = None) -> bool:
#         """
#         Transition process to a new state with validation and logging
#         Returns True if transition was successful
#         """
#         # Validate state transition
#         if not self._is_valid_transition(new_state):
#             return False
            
#         # Update state and timestamps
#         self.state = new_state
#         if new_state == ProcessState.TERMINATED:
#             self.end_time = timezone.now()
#         elif new_state == ProcessState.ERROR:
#             self.error_message = error
#             self.retry_count += 1

#         return True

#     def _is_valid_transition(self, new_state: ProcessState) -> bool:
#         """Validate if state transition is allowed"""
#         # Define valid state transitions
#         valid_transitions = {
#             ProcessState.NEW: {ProcessState.READY},
#             ProcessState.READY: {ProcessState.RUNNING, ProcessState.ERROR},
#             ProcessState.RUNNING: {ProcessState.WAITING, ProcessState.BLOCKED, ProcessState.TERMINATED, ProcessState.ERROR},
#             ProcessState.WAITING: {ProcessState.READY, ProcessState.ERROR},
#             ProcessState.BLOCKED: {ProcessState.READY, ProcessState.ERROR},
#             ProcessState.ERROR: {ProcessState.READY} if self.retry_count < self.max_retries else {ProcessState.TERMINATED},
#             ProcessState.TERMINATED: set()  # No valid transitions from TERMINATED
#         }
        
#         return new_state in valid_transitions.get(self.state, set())

#     def has_timed_out(self) -> bool:
#         """Check if process has exceeded its timeout duration"""
#         if not self.start_time or self.state == ProcessState.TERMINATED:
#             return False
#         elapsed = (timezone.now() - self.start_time).total_seconds()
#         return elapsed > self.timeout_seconds

#     def get_execution_time(self) -> Optional[float]:
#         """Get total execution time in seconds"""
#         if not self.start_time:
#             return None
#         end = self.end_time or timezone.now()
#         return (end - self.start_time).total_seconds()

#     def can_retry(self) -> bool:
#         """Check if process can be retried after error"""
#         return self.state == ProcessState.ERROR and self.retry_count < self.max_retries
