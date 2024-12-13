from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.forms.models import model_to_dict
from django.utils import timezone
from django.conf import settings
from celery import shared_task

from datetime import timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass

from kernel.signals import process_terminated_signal, ux_input_signal
from kernel.models import Process, Service, ServiceRule, Operator, ProcessFrameState
from kernel.types import ProcessState
from kernel.sys_lib import sys_call, add_periodic_task

# ================ 1. 基础数据结构 ================
@dataclass
class ContextFrame:
    """进程上下文栈帧"""
    process: Process
    parent_frame: Optional['ContextFrame']
    local_vars: Dict[str, Any]
    inherited_context: Dict[str, Any]
    return_value: Any
    status: str = 'ACTIVE'

    def __init__(self, process: Process, parent_frame=None):
        self.process = process
        self.parent_frame = parent_frame
        self.local_vars = {}  # 本地变量
        self.return_value = None  # 返回值
        self.status = 'ACTIVE'  # 栈帧状态
        
        if parent_frame:
            self.inherited_context = parent_frame.get_inheritable_context()
        else:
            self.inherited_context = {}

    def get_inheritable_context(self) -> Dict[str, Any]:
        """获取可继承的上下文变量"""
        return {
            'customer': self.process.entity_content_object,
            'business_context': self.process.control_context,
            'schedule_context': self.process.schedule_context,
        }

class ContextStack:
    def __init__(self):
        self.frames = []
        
    def push(self, process: Process):
        parent_frame = self.frames[-1] if self.frames else None
        frame = ContextFrame(process, parent_frame)
        self.frames.append(frame)
        return frame
        
    def pop(self):
        return self.frames.pop() if self.frames else None
        
    def current_frame(self):
        return self.frames[-1] if self.frames else None

# ================ 2. 状态管理 ================
class ProcessStateManager:
    """进程状态持久化管理器"""
    
    @staticmethod
    def save_frame_state(frame: ContextFrame) -> ProcessFrameState:
        """保存栈帧状态"""
        state_data = {
            'process': frame.process,
            'parent_frame_id': frame.parent_frame.process.id if frame.parent_frame else None,
            'status': frame.status,
            'local_vars': frame.local_vars,
            'inherited_context': frame.inherited_context,
            'return_value': frame.return_value,
            'timestamp': timezone.now()
        }
        return ProcessFrameState.objects.create(**state_data)

    @staticmethod
    def restore_frame_state(process: Process) -> Optional[ContextFrame]:
        """恢复栈帧状态"""
        try:
            state = ProcessFrameState.objects.get(process=process)
            parent_frame = None
            if state.parent_frame_id:
                parent_process = Process.objects.get(id=state.parent_frame_id)
                parent_frame = ProcessStateManager.restore_frame_state(parent_process)
            
            frame = ContextFrame(process, parent_frame)
            frame.local_vars = state.local_vars
            frame.inherited_context = state.inherited_context
            frame.status = state.status
            frame.return_value = state.return_value
            return frame
        except ProcessFrameState.DoesNotExist:
            return None

# ================ 3. 上下文管理 ================
class ProcessContextManager:
    """进程上下文管理器"""
    
    def __init__(self, process: Process):
        self.process = process
        self.frame = None
        self.state_manager = ProcessStateManager()

    def __enter__(self) -> ContextFrame:
        # 尝试恢复或创建新的栈帧
        self.frame = (
            self.state_manager.restore_frame_state(self.process) or 
            ContextFrame(self.process)
        )
        return self.frame

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self._handle_completion()
        else:
            self._handle_exception(exc_val)
        self.state_manager.save_frame_state(self.frame)

    def _handle_completion(self):
        """处理正常完成的情况"""
        if self.frame.return_value:
            self._process_return_value()
        RuleEvaluator().evaluate_rules(self.frame)

    def _handle_exception(self, exception):
        """处理异常情况"""
        self.frame.status = 'ERROR'
        self.frame.return_value = {'error': str(exception)}

    def _process_return_value(self):
        """处理返回值"""
        # 更新进程状态
        self.process.state = ProcessState.TERMINATED.name
        self.process.save()
        
        # 如果有父进程，将返回值传递给父进程
        if self.frame.parent_frame:
            self.frame.parent_frame.local_vars['child_return'] = self.frame.return_value

def preprocess_context(instance: Process, created: bool) -> dict:
    """预处理上下文"""
    process_context = model_to_dict(instance)
    model_context = model_to_dict(instance.form_content_object) if instance.form_content_object else {}
    control_context = instance.control_context if instance.control_context else {}
    schedule_context = instance.schedule_context if instance.schedule_context else {}
    context = {**model_context, **process_context, **control_context, **schedule_context}
    context.update({"instance": instance})
    context.update({"customer": instance.entity_content_object})
    context.update({"created": created, "timezone_now": timezone.now()})
    return context

# ================ 4. 规则评估 ================
class RuleEvaluator:
    """规则评估器"""
    
    def evaluate_rules(self, frame: ContextFrame):
        """评估当前上下文中的规则"""
        eval_context = self._build_evaluation_context(frame)
        rules = ServiceRule.objects.filter(service=frame.process.service)
        
        for rule in rules:
            if self._evaluate_condition(rule, eval_context):
                self._execute_action(rule, eval_context)

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
            return True
        except Exception as e:
            print(f"规则条件评估错误: {e}")
            return False

    def _execute_action(self, rule: ServiceRule, context: Dict[str, Any]):
        """执行规则动作"""
        try:
            if rule.system_instruction:
                # 执行系统操作
                self._execute_system_operand(rule.system_instruction, context)
            
            # if rule.operand_service:
            #     # 创建下一个服务进程
            #     self._create_next_service_process(rule.operand_service, context)
        except Exception as e:
            print(f"规则动作执行错误: {e}")

# ================ 5. 进程调度器 ================
class ProcessScheduler:
    """进程调度器"""
    
    def schedule(self, process: Process):
        """调度进程执行"""
        with ProcessContextManager(process) as context:
            if self._is_manual_process(process):
                return self._handle_manual_process(context)
            else:
                return self._handle_automatic_process(context)

    def _is_manual_process(self, process: Process) -> bool:
        """判断是否为人工处理进程"""
        # 根据服务配置或其他条件判断
        return process.service.config.get('is_manual', False) if process.service.config else False

    def _handle_manual_process(self, context: ContextFrame):
        """处理人工任务"""
        task_item = self._create_task_item(context.process)
        context.status = 'WAITING'
        return task_item

    def _handle_automatic_process(self, context: ContextFrame):
        """处理自动任务"""
        result = self._execute_process(context.process)
        context.return_value = result
        return result

    def _create_task_item(self, process: Process) -> Dict[str, Any]:
        """创建任务项"""
        return {
            'process_id': process.id,
            'service': process.service.label,
            'customer': process.entity_content_object.label if process.entity_content_object else None,
            'priority': process.priority,
            'scheduled_time': process.scheduled_time,
        }

    def _execute_process(self, process: Process) -> Dict[str, Any]:
        """执行自动处理进程"""
        # 实际的进程执行逻辑
        return {'status': 'completed'}

# ================ 6. 信号处理 ================
"""
从两类四种Django信号解析业务事件
人工触发信号: 1. 用户登录信号; 2. 人工指令信号
系统触发信号: 1. Process实例状态变更信号; 2. 系统定时信号(Celery提供)
"""
# @receiver(user_logged_in)
def on_user_login(sender, user, request, **kwargs):
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

        # 日志记录

# @receiver(post_save, sender=Process)
def on_process_save(sender, instance: Process, created: bool, **kwargs):
    """
    处理进程保存信号
    构造业务上下文，根据业务规则评估业务状态，调度作业
    """
    # if created:
    #     ProcessScheduler().schedule(instance)

    # 构造进程上下文
    context = preprocess_context(instance, created)

    # 检查服务相关规则
    rules = ServiceRule.objects.filter(service=instance.service)
    for rule in rules:
        # 向上下文添加业务规则附带的参数值
        # context.update(rule.parameter_values if rule.parameter_values else {})        
        print("检查服务规则：", rule, " | 规则表达式：", rule.event.expression)
        print("上下文：", context)
        if eval(rule.event.expression, {}, context):
            print("发生--", rule.service, rule.event, "执行->", rule.system_instruction, rule.operand_service)
            sys_call_str = rule.system_instruction.sys_call
            context['sys_call_operand'] = rule.operand_service
            sys_call(sys_call_str, **context)

    # *************************************************
    # 检查表单内服务指令，立即执行/计划执行
    # *************************************************

# @receiver(ux_input_signal)
def on_user_input(sender, process: Process, input_data: Dict[str, Any], **kwargs):
    """处理用户输入信号"""
    with ProcessContextManager(process) as context:
        context.local_vars.update(input_data)
        context.status = 'READY'

# @shared_task
def on_timer_signal(sender, process: Process, **kwargs):
    """
    处理系统定时信号
    将Celery的定时任务信号转译为业务事件
    相当于操作系统时钟中断信号
    可检查各业务进程状态，启动提醒服务进程、分析报告服务进程等
    优先级最低
    """
    with ProcessContextManager(process) as context:
        context.status = 'READY'

# ================ 7. 任务执行集成 ================
def execute_process(process: Process):
    """任务执行的统一入口"""
    with ProcessContextManager(process) as context:
        if process.is_manual:
            # 人工任务：创建任务项，等待人工处理
            task_item = create_manual_task(process, context)
            context.status = 'WAITING'
            return task_item
        else:
            # 自动任务：直接执行
            result = execute_automatic_task(process, context)
            context.return_value = result
            return result
                    
# 1. 创建人工任务
def create_manual_task(process: Process):
    with ProcessContextManager(process) as context:
        # 创建待办事项
        task_item = create_task_item(process)
        # 设置状态为等待
        context.status = 'WAITING'
        # 挂起当前执行
        suspend_execution(context)
        return task_item

# 2. 人工处理过程（在系统外部进行）
# 系统接受到任务表单保存信号后，调用此函数恢复执行
# 3. 恢复执行
def resume_manual_task(task_item, result):
    process = task_item.process
    with ProcessContextManager(process) as context:
        # 恢复上下文
        restore_context(context)
        # 设置处理结果
        context.return_value = result
        context.status = 'COMPLETED'
        # 触发规则评估和后续处理
        handle_task_completion(context)

# 3. 自动任务执行
def execute_automatic_task(process: Process):
    with ProcessContextManager(process) as context:
        # 执行实际任务
        result = _do_execute_process(process)
        context.return_value = result
        return result
