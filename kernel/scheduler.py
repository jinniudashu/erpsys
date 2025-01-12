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

from kernel.signals import operand_finished, ux_input_signal
from kernel.models import Process, Service, ServiceProgram, ServiceRule, Operator, ProcessContextSnapshot
from kernel.types import ProcessState, CONTEXT_SCHEMA
from kernel.sys_lib import sys_call, ContextFrame, ContextStack, ProcessExecutionContext, ProcessCreator, update_task_list, update_entity_task_group_list

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
                self._execute_action(rule, eval_context)
                frame.events_triggered_log.append({
                    'rule_id': rule.erpsys_id,
                    'rule_label': rule.label,
                    'event_expression': rule.event.expression,
                    'evaluated_at': timezone.now().isoformat()
                })

    def _build_evaluation_context(self, frame: ContextFrame) -> Dict[str, Any]:
        """构建扁平化的规则评估上下文"""
        # 1. 序列化进程信息
        process = frame.process
        process_data = {
            'id': process.id,
            'name': process.name,
            'state': process.state,
            'service_id': process.service.id if process.service else None,
            'service_name': process.service.name if process.service else None,
            'program_entrypoint': process.program_entrypoint,
            'priority': process.priority,
            'created_at': process.created_at.isoformat() if process.created_at else None,
        }

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
            # 进程信息（使用 process_ 前缀避免命名冲突）
            'process_id': process_data['id'],
            'process_name': process_data['name'],
            'process_state': process_data['state'],
            'process_service': process_data['service_name'],
            'process_entrypoint': process_data['program_entrypoint'],
            'process_priority': process_data['priority'],
            'process_created_at': process_data['created_at'],

            # 操作者信息
            'operator_id': process.operator.id if process.operator else None,
            'operator_name': str(process.operator) if process.operator else None,

            # 实体对象信息
            'entity_id': process.entity_content_object.id if process.entity_content_object else None,
            'entity_type': process.entity_content_type.model if process.entity_content_type else None,
            'entity_name': str(process.entity_content_object) if process.entity_content_object else None,

            # 时间信息
            'current_time': timezone.now().isoformat(),

            # 返回值
            'result': frame.return_value,
        }

        # 4. 合并本地变量（可能覆盖上面的基础信息）
        context.update(frame.local_vars)

        # 5. 合并继承的上下文（优先级最低）
        context.update(inherited_data)

        return context

    def _evaluate_condition(self, rule: ServiceRule, context: Dict[str, Any]) -> bool:
        """评估规则条件"""
        try:
            print('评估上下文：', context)
            if rule.event and rule.event.expression:
                return eval(rule.event.expression, {}, context)
            return False  # 如果没有事件或表达式，返回False表示条件不满足
        except Exception as e:
            print(f"规则条件评估错误: {e}")
            return False

    def _execute_action(self, rule: ServiceRule, context: Dict[str, Any]):
        if rule.system_instruction:
            sys_call_str = rule.system_instruction.sys_call
            context['operand_service'] = rule.operand_service
            sys_call(sys_call_str, **context)

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
        service_program = ServiceProgram.objects.get(sys_default=True)
        service_rule = ServiceRule.objects.get(service_program=service_program, service__name='user_login')
        params = {
            'service_rule': service_rule,
            'entity_content_object': operator,
            'operator': operator,
            'state': ProcessState.TERMINATED.name,
            'priority': 0,
            'program_entrypoint': service_program.erpsys_id,
            'init_params': {}
        }

        # import pdb; pdb.set_trace()  # 在这里设置断点
        # 创建一个登录进程
        creator = ProcessCreator(need_business_record=False)
        proc = creator.create_process(params)

        # 发送登录作业完成信号
        operand_finished.send(sender=on_user_login, pid=proc, request=request, form_data=None, formset_data=None)

@receiver(operand_finished)
def operand_finished_handler(sender, **kwargs):
    """
    业务表单变更后，在此处评估业务状态变更情况
    1. 检查是否有规则预定义的业务事件发生
    2. 如果发生业务事件，执行预定业务程序
    3. 更新进程状态
    """
    process = kwargs['pid']
    with ProcessExecutionContext(process) as frame:
        # 评估规则
        evaluator = RuleEvaluator()
        evaluator.evaluate_rules(frame)

    # *************************************************
    # 检查表单内服务指令，立即执行/计划执行
    # *************************************************

@receiver(post_save, sender=Process, dispatch_uid="post_save_process")
def on_process_save(sender, instance: Process, created: bool, **kwargs):
    """
    更新进程业务状态后，更新任务队列，输出刷新后的任务调度信号
    """
    if instance.operator and instance.operator.user.is_staff:
        update_task_list(instance.operator, True)
        # 更新操作员的今日安排、紧要安排、本周安排
        update_task_list(instance.operator, False)

        update_entity_task_group_list(instance.entity_content_object)

    # # 根据状态执行相应的处理逻辑
    # match instance.state:
    #     case ProcessState.READY.name:
    #         _handle_ready_state(frame)
    #     case ProcessState.RUNNING.name:
    #         _handle_running_state(frame)
    #     case ProcessState.WAITING.name:
    #         _handle_waiting_state(frame)
    #     case ProcessState.SUSPENDED.name:
    #         _handle_suspended_state(frame)
    #     case ProcessState.TERMINATED.name:
    #         _handle_terminated_state(frame)
    #     case ProcessState.ERROR.name:
    #         _handle_error_state(frame)
    #     case _:
    #         logger.warning(f"Unhandled process state: {instance.state}")            

def _handle_ready_state(self, frame):
    """处理就绪状态"""
    frame.local_vars['state_changed'] = "状态更新为READY"
    frame.local_vars['state_ready'] = True
    # 将进程加入调度队列
    scheduler = ProcessScheduler()
    scheduler.add_to_run_queue(frame.process)

def _handle_running_state(self, frame):
    """处理运行状态"""
    frame.local_vars['state_changed'] = "状态更新为RUNNING"
    frame.scheduling_info['last_scheduled_time'] = timezone.now()

def _handle_waiting_state(self, frame):
    """处理等待状态"""
    frame.local_vars['state_changed'] = "状态更新为WAITING"
    # 记录等待原因
    frame.local_vars['wait_reason'] = frame.process.wait_reason

def _handle_suspended_state(self, frame):
    """处理挂起状态"""
    frame.local_vars['state_changed'] = "状态更新为SUSPENDED"
    # 保存挂起时的上下文信息
    frame.local_vars['suspend_info'] = {
        'suspended_at': timezone.now(),
        'suspend_reason': frame.process.suspend_reason
    }

def _handle_terminated_state(self, frame):
    """处理终止状态"""
    frame.local_vars['state_changed'] = "状态更新为TERMINATED"
    frame.return_value = {'message': 'Process completed successfully'}
    # 清理资源
    resource_manager = ResourceManager()
    resource_manager.release_all(frame.process)

def _handle_error_state(self, frame):
    """处理错误状态"""
    frame.status = 'ERROR'
    frame.return_value = {'error': str(frame.process.error)}
    # 错误处理和恢复
    error_handler = ProcessErrorHandler()
    error_handler.handle_error(frame.process, frame.process.error)

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

    """
    示例：定时任务，每隔一段时间（30秒），就执行一次调度过程。
    """
    with transaction.atomic():
        # 1. 搜集所有处于 READY 状态的进程
        ready_processes = Process.objects.select_for_update().filter(
            state=ProcessState.READY.name
        ).order_by('-priority', 'created_at')

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

@receiver(ux_input_signal)
def on_ux_input(**kwargs):
    """接收人工指令调度"""
    """
    系统外部输入中断信号，需要即时响应
    优先级最高
    """
    pass

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

# ******** Linux风格的优化建议 ********
# 1.进程调度机制
# class ProcessScheduler:
#     def __init__(self):
#         self.run_queue = []  # 运行队列
#         self.wait_queue = [] # 等待队列
#         self._time_slice = 100  # 时间片大小(ms)
        
#     def schedule(self):
#         """调度器主循环"""
#         while True:
#             process = self._pick_next_process()
#             if process:
#                 self._context_switch(process)
#                 self._run_process(process)
            
#     def _pick_next_process(self):
#         """选择下一个要运行的进程"""
#         # 实现优先级调度
#         return max(self.run_queue, key=lambda p: p.priority, default=None)
        
#     def preempt(self, current_process):
#         """抢占式调度"""
#         if current_process.time_slice_used >= self._time_slice:
#             # 时间片用完，重新调度
#             self.run_queue.append(current_process)
#             return self._pick_next_process()

# 2. 进程状态管理 建议引入更完整的状态转换机制：
# class ProcessStateManager:
#     def __init__(self, process):
#         self.process = process
#         self._state_transitions = {
#             ProcessState.NEW: [ProcessState.READY],
#             ProcessState.READY: [ProcessState.RUNNING, ProcessState.SUSPENDED],
#             ProcessState.RUNNING: [ProcessState.READY, ProcessState.WAITING, ProcessState.TERMINATED],
#             ProcessState.WAITING: [ProcessState.READY],
#             ProcessState.SUSPENDED: [ProcessState.READY],
#             ProcessState.TERMINATED: []
#         }
    
#     def can_transition_to(self, new_state):
#         """检查状态转换是否合法"""
#         return new_state in self._state_transitions[self.process.state]

# 3. 进程间通信(IPC)
# class IPCManager:
#     def __init__(self):
#         self._message_queues = {}
#         self._shared_memory = {}
#         self._semaphores = {}
    
#     def create_message_queue(self, queue_id):
#         """创建消息队列"""
#         self._message_queues[queue_id] = Queue()
    
#     def send_message(self, queue_id, message):
#         """发送消息"""
#         self._message_queues[queue_id].put(message)
    
#     def receive_message(self, queue_id):
#         """接收消息"""
#         return self._message_queues[queue_id].get()

# 4. 资源管理 引入资源限制和监控
# class ResourceManager:
#     def __init__(self):
#         self.memory_limit = settings.PROCESS_MEMORY_LIMIT
#         self.cpu_limit = settings.PROCESS_CPU_LIMIT
        
#     def allocate_resources(self, process):
#         """分配资源"""
#         if self._check_resource_availability():
#             process.resources = {
#                 'memory': self.memory_limit,
#                 'cpu': self.cpu_limit
#             }
#             return True
#         return False
    
#     def monitor_usage(self, process):
#         """监控资源使用"""
#         current_usage = self._get_process_usage(process)
#         if current_usage > process.resources:
#             self._handle_resource_overflow(process)

# 5. 信号处理机制
# class SignalManager:
#     def __init__(self):
#         self._handlers = defaultdict(list)
        
#     def register_handler(self, signal, handler):
#         """注册信号处理器"""
#         self._handlers[signal].append(handler)
    
#     def send_signal(self, process_id, signal):
#         """发送信号"""
#         process = Process.objects.get(id=process_id)
#         for handler in self._handlers[signal]:
#             handler(process)
            
#     def handle_signal(self, signal, process):
#         """处理信号"""
#         if signal == Signals.SIGTERM:
#             self._terminate_process(process)
#         elif signal == Signals.SIGSTOP:
#             self._suspend_process(process)

# 6. 进程同步机制 添加同步原语
# class SynchronizationManager:
#     def __init__(self):
#         self._locks = {}
#         self._conditions = {}
#         self._events = {}
        
#     def acquire_lock(self, lock_id, process):
#         """获取锁"""
#         if lock_id not in self._locks:
#             self._locks[lock_id] = Lock()
#         return self._locks[lock_id].acquire()
    
#     def wait_for_condition(self, condition_id, predicate):
#         """条件等待"""
#         if condition_id not in self._conditions:
#             self._conditions[condition_id] = Condition()
#         with self._conditions[condition_id]:
#             while not predicate():
#                 self._conditions[condition_id].wait()

# 7. 错误处理和恢复
# class ProcessErrorHandler:
#     def __init__(self):
#         self.max_retries = 3
        
#     def handle_error(self, process, error):
#         """处理进程错误"""
#         if process.retry_count < self.max_retries:
#             self._retry_process(process)
#         else:
#             self._terminate_process(process)
#             self._notify_admin(process, error)
    
#     def _retry_process(self, process):
#         """重试进程"""
#         process.retry_count += 1
#         process.state = ProcessState.READY
#         process.save()

# 8. 系统调用接口
# class SystemCallInterface:
#     @staticmethod
#     def fork(parent_process):
#         """创建子进程"""
#         return ProcessCreator().clone_process(parent_process)
    
#     @staticmethod
#     def exit(process, exit_code):
#         """退出进程"""
#         process.exit_code = exit_code
#         process.state = ProcessState.TERMINATED
#         process.save()
    
#     @staticmethod
#     def wait(process, child_pid):
#         """等待子进程"""
#         child = Process.objects.get(pid=child_pid)
#         while child.state != ProcessState.TERMINATED:
#             time.sleep(0.1)
