from django.db.models import Q, Manager
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import datetime
import json
import jsonschema
import hashlib
import re

from kernel.models import (
    Service, ServiceRule, ProcessContextSnapshot,
    Process, Operator, WorkOrder
)
from kernel.types import ProcessState, CONTEXT_SCHEMA

from applications.models import *

# ================ 1. 基础上下文数据结构 ================
class ContextFrame:
    """
    上下文帧：表示某个Process的执行上下文，含局部变量、调用日志等。
    支持嵌套时，child frame 的 parent_frame 即为父Process对应的frame。
    """
    def __init__(self, process: Process, parent_frame: 'ContextFrame' = None):
        self.process = process
        self.parent_frame = parent_frame  # 父帧
        self.status = 'ACTIVE'
        self.local_vars = {}  # 任务执行过程中的局部变量
        self.return_value = None  # 任务（服务函数）的返回值
        self.inherited_context = parent_frame.get_inheritable_context() if parent_frame else {}
        self.events_triggered_log = []  # 记录任务触发的事件日志
        self.error_info = None  # 任务出错时存储信息

    def get_inheritable_context(self) -> dict:
        """
        获取可从父帧继承的上下文。默认父帧的 local_vars 为可继承部分,
        这里可根据业务需要做细粒度筛选。
        """
        if self.parent_frame:
            return dict(self.parent_frame.local_vars)  # 浅拷贝一份即可
        return {}

    def to_dict(self) -> dict:
        """将当前帧序列化为字典，供持久化用。"""
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
    def from_dict(cls, data: dict, process_lookup) -> 'ContextFrame':
        """
        从字典创建帧实例。process_lookup: 通过erpsys_id定位Process实例的回调。
        """
        process = process_lookup(data["process_id"])
        frame = cls(process, parent_frame=None)
        frame.status = data["status"]
        frame.local_vars = data["local_vars"]
        frame.inherited_context = data["inherited_context"]
        frame.return_value = data.get("return_value")
        frame.error_info = data.get("error_info")
        frame.events_triggered_log = data.get("events_triggered_log", [])
        return frame

class ContextStack:
    """
    上下文堆栈：管理多个ContextFrame，用于模拟函数调用栈。
    栈顶frame即当前执行中的Process。
    """
    def __init__(self):
        self.frames: List[ContextFrame] = []
        
    def push(self, process: Process, parent_frame: ContextFrame = None) -> ContextFrame:
        """
        入栈并创建新的ContextFrame；若提供parent_frame，则将其设置为新frame的父帧。
        若不提供，则默认以上一个栈顶frame作为父帧。
        """
        if parent_frame is None and self.frames:
            parent_frame = self.frames[-1]

        frame = ContextFrame(process, parent_frame)
        self.frames.append(frame)
        return frame

    def pop(self) -> Optional[ContextFrame]:
        """出栈并返回当前frame"""
        return self.frames.pop() if self.frames else None

    def current_frame(self) -> Optional[ContextFrame]:
        """获取栈顶frame"""
        return self.frames[-1] if self.frames else None

    def to_dict(self) -> dict:
        """将整个上下文栈序列化为可JSON化的字典结构"""
        return {
            "frames": [f.to_dict() for f in self.frames],
        }

    @classmethod
    def from_dict(cls, data: dict, process_lookup) -> 'ContextStack':
        """
        反序列化生成ContextStack对象。
        需要借助process_lookup(process_id)来从erpsys_id恢复真实的Process对象。
        """
        # 先做结构校验
        jsonschema.validate(instance=data, schema=CONTEXT_SCHEMA)

        stack = cls()
        # frames按顺序还原，假设下标0是底层
        for frame_data in data["frames"]:
            frame = ContextFrame.from_dict(frame_data, process_lookup)
            # 先暂存
            stack.frames.append(frame)

        # 第二遍遍历，重新关联parent_frame（如果同一堆栈内）
        for i in range(len(stack.frames)):
            if i > 0:
                stack.frames[i].parent_frame = stack.frames[i - 1]
        return stack

class ProcessExecutionContext:
    """
    进程执行上下文管理器：
    - 通过ContextStack存储多个ContextFrame，支持多级嵌套调用；
    - 在进入/退出时，对上下文进行快照并存储到ProcessContextSnapshot中（若有变化）；
    - 结合SysCall机制可实现“调用子服务 -> 挂起当前进程 -> 等子进程结束 -> 子进程call_return -> 父进程恢复”。
    """
    def __init__(self, process: Process, parent_frame: ContextFrame = None, version: int = None):
        self.process = process
        self.parent_frame = parent_frame
        self.version = version
        self.stack: ContextStack = None
        self._previous_context_hash = self._get_last_context_hash(process) if process else None

    def __enter__(self) -> ContextFrame:
        # 若父帧存在，则沿用其stack，否则从DB中加载或新建stack
        if self.parent_frame:
            self.stack = self.parent_frame.stack
        else:
            # 先尝试从DB恢复最新上下文
            restored = self._restore_context(self.process)
            if restored:
                self.stack, self.version = restored
            else:
                self.stack = ContextStack()
                self.version = 0

        # push新的frame
        new_frame = self.stack.push(self.process, parent_frame=self.parent_frame)
        # 把Process本身信息放到local_vars，做评估时可访问
        process_info = {
            'process_id': self.process.erpsys_id,
            'process_name': self.process.name,
            'process_state': self.process.state,
            'process_service': self.process.service.name if self.process.service else None,
            'process_operator': str(self.process.operator) if self.process.operator else None,
            'process_priority': self.process.priority,
            'process_created_at': self.process.created_at.isoformat() if self.process.created_at else None,
            'process_updated_at': self.process.updated_at.isoformat() if self.process.updated_at else None,
        }
        new_frame.local_vars.update(process_info)

        return new_frame

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出上下文时，将stack序列化并保存至DB(若有变化)。
        """
        current_hash = self._calculate_context_hash(self.stack)
        if current_hash != self._previous_context_hash:
            self.version = self._save_context(self.stack, self.process, current_hash)
            self._previous_context_hash = current_hash

        # 在正常结束时，如需清理资源或进行收尾，可在此添加逻辑
        if exc_type is not None:
            current_frame = self.stack.current_frame()
            if current_frame:
                current_frame.error_info = str(exc_val)
            print(f"ProcessExecutionContext: 捕获异常 {exc_val} (process={self.process})")

    def _calculate_context_hash(self, stack: ContextStack) -> str:
        """
        计算当前上下文的哈希值，用于判断上下文是否有更新。
        """
        def normalize(d):
            if isinstance(d, dict):
                return {k: normalize(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [normalize(x) for x in d]
            return d

        context_dict = stack.to_dict()
        normalized_dict = normalize(context_dict)
        return hashlib.sha256(json.dumps(normalized_dict, sort_keys=True).encode()).hexdigest()

    def _restore_context(self, process: Process, version: int = None) -> Optional[tuple]:
        """
        从数据库加载上下文堆栈：
        - 如果指定version，则加载对应版本；
        - 否则加载最新版本。
        """
        qs = ProcessContextSnapshot.objects.filter(process=process)
        if version:
            qs = qs.filter(version=version)
        else:
            qs = qs.order_by('-version')

        snapshot = qs.first()
        if not snapshot:
            return None

        data = snapshot.context_data

        def process_lookup(pid):
            return Process.objects.get(erpsys_id=pid)

        stack = ContextStack.from_dict(data, process_lookup)
        return stack, snapshot.version

    def _save_context(self, stack: ContextStack, process: Process, current_hash: str) -> int:
        """
        将当前stack序列化保存为新的ProcessContextSnapshot，并返回新的version号。
        """
        context_data = stack.to_dict()
        # 验证结构
        jsonschema.validate(context_data, CONTEXT_SCHEMA)

        # 获取最新version
        latest_version = (
            ProcessContextSnapshot.objects.filter(process=process)
            .order_by('-version')
            .first()
        )
        new_version = latest_version.version + 1 if latest_version else 1

        ProcessContextSnapshot.objects.create(
            process=process,
            version=new_version,
            context_data=context_data,
            context_hash=current_hash
        )
        return new_version

    def _get_last_context_hash(self, process: Process) -> Optional[str]:
        """获取上次保存的快照哈希"""
        last_snapshot = ProcessContextSnapshot.objects.filter(process=process).order_by('-version').first()
        return last_snapshot.context_hash if last_snapshot else None

class ProcessCreator:
    """
    进程创建器：根据 ServiceRule 等信息创建 Process 和相应业务表单
    """
    def __init__(self, need_business_record: bool = True):
        self.need_business_record = need_business_record

    def create_process(self, kwargs: dict) -> Process:
        """
        创建新的服务进程，并将其纳入上下文管理。
        kwargs 必需包含以下字段：
          - service_rule: ServiceRule实例
          - service: Service实例
          - operator: Operator实例
          - state: 初始状态 (可选，默认NEW)
          - entity_content_object: 业务实体 (可选)
          - parent_frame: 父进程上下文帧 (可选)
        """        
        service_rule = kwargs.get('service_rule')
        if not service_rule:
            raise ValueError("service_rule is required")

        service_program = service_rule.target_service
        service = kwargs.get('service')
        if not service:
            raise ValueError("service is required")

        operator = kwargs.get('operator')
        if not operator:
            raise ValueError("operator is required")

        parent_frame = kwargs.get('parent_frame', None)
        entity = kwargs.get('entity_content_object', None)

        # 创建Process
        process_params = {
            'name': f"{service_program.label} - {service.label} - {operator}",
            'parent': kwargs.get('parent', None),
            'previous': kwargs.get('previous', None),
            'service': service,
            'entity_content_object': entity,
            'state': kwargs.get('state', ProcessState.NEW.name),
            'operator': operator,
            'priority': kwargs.get('priority', 0),
            'program_entrypoint': service_program.erpsys_id
        }
        process = Process.objects.create(**process_params)

        # 若此Process无显式 parent，则自指向（默认让 parent=自己）
        if not process.parent:
            process.parent = process
            process.save()

        # 若需创建业务记录
        if self.need_business_record:
            form_obj =self._create_business_record(process)
            # 更新进程表单信息
            process.form_content_object = form_obj
            model_name = process.service.config.get('subject')['name']
            process.form_url = f"/{settings.CUSTOMER_SITE_NAME}/applications/{model_name.lower()}/{form_obj.id}/change/"
            process.save()

        # 用上下文管理器写入init_params并评估规则
        init_params = kwargs.get('init_params', {})
        with ProcessExecutionContext(process, parent_frame=parent_frame) as frame:
            frame.local_vars.update(init_params)
            frame.local_vars.update({
                'service_program_id': service_program.erpsys_id,
                'service_rule_id': service_rule.erpsys_id
            })

            evaluator = RuleEvaluator()
            evaluator.evaluate_rules(frame)

        return process

    def _create_business_record(self, process):
        """
        根据service.config['subject']中的模型名，为此Process创建业务表单实例。
        如果该模型定义了master字段，则自动关联 process.entity_content_object。        
        """
        if not process.service or not process.service.config:
            return
        subject_conf = process.service.config.get('subject')
        if not subject_conf or 'name' not in subject_conf:
            return

        model_name = subject_conf['name']
        model_class = eval(model_name)

        params = {
            'label': process.service.label,
            'pid': process
        }

        if hasattr(model_class, 'master'):
            params['master'] = process.entity_content_object

        return model_class.objects.create(**params)

class RuleEvaluator:
    """
    规则评估器：对当前Frame上下文进行条件判断，若满足则执行对应系统指令
    """

    def evaluate_rules(self, frame: ContextFrame):
        process = frame.process
        service_program_id = process.program_entrypoint
        if not service_program_id:
            return

        try:
            sp = Service.objects.get(erpsys_id=service_program_id)
        except Service.DoesNotExist:
            return

        # 找到与当前Process匹配的所有规则
        rules = ServiceRule.objects.filter(
            target_service=sp,
            service=process.service
        )
        eval_context = self._build_evaluation_context(frame)

        for rule in rules:
            if rule.event and rule.event.expression:
                if self._evaluate_condition(rule, eval_context):
                    # 命中后执行系统指令
                    frame.events_triggered_log.append({
                        'rule_id': rule.erpsys_id,
                        'rule_label': rule.label,
                        'event_expression': rule.event.expression,
                        'evaluated_at': timezone.now().isoformat()
                    })
                    # frame.local_vars['operand_process_id'] = frame.process.parent.erpsys_id
                    self._execute_action(rule, eval_context)

    def _build_evaluation_context(self, frame: ContextFrame) -> Dict[str, Any]:
        """
        构建规则评估上下文。默认把frame.local_vars和父帧(inherited_context)的变量进行合并。
        """
        # 也可加入更多业务信息
        ctx = {}
        ctx.update(frame.inherited_context)
        ctx.update(frame.local_vars)
        return ctx

        # """构建扁平化的规则评估上下文"""
        # # 1. 直接使用frame.local_vars中已有的进程信息
        # process_info = frame.local_vars

        # # 2. 获取完整的继承上下文链
        # def get_inherited_chain(context_dict, depth=0, max_depth=10):
        #     if not context_dict or depth >= max_depth:
        #         return {}
            
        #     result = context_dict.copy()
        #     parent_context = frame.parent_frame.inherited_context if frame.parent_frame else {}
        #     parent_data = get_inherited_chain(parent_context, depth + 1)
            
        #     # 子级上下文优先
        #     parent_data.update(result)
        #     return parent_data

        # inherited_data = get_inherited_chain(frame.inherited_context)

        # # 3. 构建扁平化上下文
        # context = {
        #     **process_info,  # 带前缀的进程信息
        #     **inherited_data,  # 继承的上下文数据
        # }

        # print('扁平化上下文：', context)

        # return context

    def _evaluate_condition(self, rule: ServiceRule, context: Dict[str, Any]) -> bool:
        """
        评估 rule.event.expression 中的条件表达式。
        注意：表达式中会使用 process_state, process_name 等专门加了process前缀的进程对象字段。
        """
        try:
            expression = rule.event.expression
            return eval(expression, {}, context)
        except Exception as e:
            print(f"[RuleEvaluator] 条件评估异常: {e}")
            return False

        # """评估规则条件"""
        # try:
        #     print('评估上下文：', context)
        #     if rule.event and rule.event.expression:
        #         # 将表达式中的进程相关字段替换为带前缀的形式
        #         expression = rule.event.expression
        #         # 替换所有进程相关字段
        #         field_mappings = {
        #             r'\bstate\b': 'process_state',
        #             r'\bname\b': 'process_name',
        #             r'\bservice\b': 'process_service',
        #             r'\boperator\b': 'process_operator',
        #             r'\bpriority\b': 'process_priority',
        #             r'\bcreated_at\b': 'process_created_at',
        #             r'\bupdated_at\b': 'process_updated_at'
        #         }
        #         for old_field, new_field in field_mappings.items():
        #             expression = re.sub(old_field, new_field, expression)
        #         print('转换后的表达式：', expression)
        #         return eval(expression, {}, context)
        #     return False  # 如果没有事件或表达式，返回False表示条件不满足
        # except Exception as e:
        #     print(f"规则条件评估错误: {e}")
        #     return False

    def _execute_action(self, rule: ServiceRule, context: Dict[str, Any]):
        if not rule.system_instruction:
            return

        sys_call_name = rule.system_instruction.sys_call
        context['service_rule_id'] = rule.erpsys_id
        from kernel.tasks import execute_sys_call_task
        # 异步调用 Celery 任务
        execute_sys_call_task.delay(sys_call_name, context)

# ================ 2. 系统指令实现（SysCall） ================
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
        pass

class StartService(SysCallInterface):
    """
    启动一个新的 primitive Service
    （与“调用服务”区别：它仅启动单一服务进程，而不修改当前进程状态）
    """
    def execute(self, **kwargs) -> SysCallResult:
        try:
            # 1. 校验
            service_rule_id = kwargs.get("service_rule_id")
            if not service_rule_id:
                return SysCallResult(False, "缺少 service_rule_id 参数")

            sr = ServiceRule.objects.get(erpsys_id=service_rule_id)
            operand_service = sr.operand_service
            if not operand_service:
                return SysCallResult(False, "当前规则未指定 operand_service")

            # 2. 找到当前process（发起方）
            process_id = kwargs.get("process_id")
            if not process_id:
                return SysCallResult(False, "缺少 process_id 参数")
            proc = Process.objects.get(erpsys_id=process_id)

            operator = proc.operator
            entity = proc.entity_content_object

            # 3. 创建新Process
            params = {
                "parent": proc.parent,
                "previous": proc,
                "service_rule": sr,
                "service": operand_service,
                "operator": operator,
                "entity_content_object": entity,
                "name": operand_service.label,
                "parent_frame": kwargs.get("parent_frame", None),
            }
            creator = ProcessCreator()
            new_proc = creator.create_process(params)

            return SysCallResult(
                success=True,
                message="成功启动新的服务进程",
                data={"new_process_id": new_proc.erpsys_id}
            )
        except Exception as e:
            return SysCallResult(False, f"StartService异常: {e}")

class CallSubService(SysCallInterface):
    def execute(self, **kwargs) -> SysCallResult:
        """
        在当前进程内调用另一个子服务（可primitive，也可服务函数）；
        当前进程进入 WAITING，待子服务完成后再恢复。
        """
        try:
            # 1. 校验
            service_rule_id = kwargs.get("service_rule_id")
            if not service_rule_id:
                return SysCallResult(False, "缺少 service_rule_id 参数")

            sr = ServiceRule.objects.get(erpsys_id=service_rule_id)
            operand_service = sr.operand_service
            if not operand_service:
                return SysCallResult(False, "当前规则未指定 operand_service")

            process_id = kwargs.get("process_id")
            if not process_id:
                return SysCallResult(False, "缺少 process_id 参数")

            parent_process = Process.objects.get(erpsys_id=process_id)

            # 2. 当父进程还没终止时，将其挂起为WAITING
            if parent_process.state != ProcessState.TERMINATED.name:
                parent_process.state = ProcessState.WAITING.name
                parent_process.save()

            # 3. 创建子进程
            operator = parent_process.operator
            entity = parent_process.entity_content_object

            # 先读取父上下文
            with ProcessExecutionContext(parent_process) as parent_frame:
                params = {
                    "parent": parent_process,
                    "previous": parent_process,
                    "service_rule": sr,
                    "service": operand_service,
                    "operator": operator,
                    "entity_content_object": entity,
                    "parent_frame": parent_frame,  # 建立子进程时的上下文嵌套
                }
                creator = ProcessCreator()
                child_proc = creator.create_process(params)

            return SysCallResult(
                True,
                "已创建子服务进程，父进程已挂起等待子进程完成",
                data={"child_process_id": child_proc.erpsys_id}
            )
        except Exception as e:
            return SysCallResult(False, f"CallSubService异常: {e}")

class CallingReturn(SysCallInterface):
    """
    从子服务返回到父服务:
    1. 将当前子进程置为 TERMINATED;
    2. 弹出当前Frame，恢复父Frame;
    3. 父进程置为 READY 或 RUNNING。
    """
    def execute(self, **kwargs) -> SysCallResult:
        try:
            child_process_id = kwargs.get("process_id")
            if not child_process_id:
                return SysCallResult(False, "缺少当前process_id参数")

            child_process = Process.objects.get(erpsys_id=child_process_id)
            parent_process = child_process.parent
            if not parent_process or (parent_process == child_process):
                # 如果parent_process == 自己，说明此进程是顶层，可能不需要返回
                return SysCallResult(False, "无法调用返回：父进程不存在或与子进程相同")

            # 1. 子进程结束
            child_process.state = ProcessState.TERMINATED.name
            child_process.save()

            # 2. 弹出上下文堆栈
            with ProcessExecutionContext(child_process) as child_frame:
                # 将child_frame的返回值写回父frame的 local_vars（如有需求）
                return_value = child_frame.return_value

            # 手动恢复父上下文(让父进程回到RUNNING或就绪态)
            parent_process.refresh_from_db()
            parent_state = parent_process.state
            if parent_state == ProcessState.WAITING.name:
                parent_process.state = ProcessState.RUNNING.name
                parent_process.save()

            return SysCallResult(
                True,
                "子进程已返回并终止，父进程恢复",
                data={"parent_process_id": parent_process.erpsys_id, "return_value": return_value}
            )
        except Exception as e:
            return SysCallResult(False, f"CallingReturn异常: {e}")

class StartIterationService(SysCallInterface):
    """
    启动循环服务：同一个Service重复执行N次或直到条件终止
    在业务中常用于“一系列相同流程的多次重复”场景
    """
    def execute(self, **kwargs) -> SysCallResult:
        """
        参数约定：
          - service_rule_id
          - process_id
          - iterations: 需要执行的次数
        """
        try:
            service_rule_id = kwargs.get("service_rule_id")
            if not service_rule_id:
                return SysCallResult(False, "缺少 service_rule_id")

            sr = ServiceRule.objects.get(erpsys_id=service_rule_id)
            operand_service = sr.operand_service
            if not operand_service:
                return SysCallResult(False, "当前规则未指定 operand_service")

            process_id = kwargs.get("process_id")
            if not process_id:
                return SysCallResult(False, "缺少 process_id")

            parent_process = Process.objects.get(erpsys_id=process_id)
            operator = parent_process.operator
            entity = parent_process.entity_content_object

            iterations = kwargs.get("iterations", 1)
            if not isinstance(iterations, int) or iterations <= 0:
                return SysCallResult(False, f"非法循环次数: {iterations}")

            with ProcessExecutionContext(parent_process) as parent_frame:
                created_ids = []
                creator = ProcessCreator()
                for i in range(iterations):
                    params = {
                        "parent": parent_process,
                        "previous": parent_process,
                        "service_rule": sr,
                        "service": operand_service,
                        "operator": operator,
                        "entity_content_object": entity,
                        "init_params": {"iteration_index": i + 1},
                        "parent_frame": parent_frame
                    }
                    child_proc = creator.create_process(params)
                    created_ids.append(child_proc.erpsys_id)

            return SysCallResult(
                True,
                f"成功创建 {iterations} 个循环子进程",
                data={"child_process_ids": created_ids}
            )
        except Exception as e:
            return SysCallResult(False, f"StartIterationService异常: {e}")

class StartParallelService(SysCallInterface):
    """
    启动并行服务：同一个Service并发生成多个子进程，如会诊调度给多位医生。
    业务侧可等到全部完成后再做后续处理。
    """
    def execute(self, **kwargs) -> SysCallResult:
        """
        参数约定：
          - service_rule_id
          - process_id
          - threads: 并发数量(或指定执行的若干Operator)
        """
        try:
            service_rule_id = kwargs.get("service_rule_id")
            if not service_rule_id:
                return SysCallResult(False, "缺少 service_rule_id")

            sr = ServiceRule.objects.get(erpsys_id=service_rule_id)
            operand_service = sr.operand_service
            if not operand_service:
                return SysCallResult(False, "当前规则未指定 operand_service")

            process_id = kwargs.get("process_id")
            if not process_id:
                return SysCallResult(False, "缺少 process_id")

            parent_process = Process.objects.get(erpsys_id=process_id)
            entity = parent_process.entity_content_object

            threads = kwargs.get("threads", 1)
            # 并发数检查
            if not isinstance(threads, int) or threads <= 0:
                return SysCallResult(False, f"并发数量无效: {threads}")

            # 若传入operators列表，则优先针对指定操作员，否则默认与父进程同一operator
            operators_list = kwargs.get("operators", [])
            if not operators_list:
                operators_list = [parent_process.operator.erpsys_id] * threads

            with ProcessExecutionContext(parent_process) as parent_frame:
                child_ids = []
                creator = ProcessCreator()
                for index, op_id in enumerate(operators_list, start=1):
                    op = Operator.objects.get(erpsys_id=op_id)
                    params = {
                        "parent": parent_process,
                        "previous": parent_process,
                        "service_rule": sr,
                        "service": operand_service,
                        "operator": op,
                        "entity_content_object": entity,
                        "init_params": {"parallel_index": index},
                        "parent_frame": parent_frame
                    }
                    proc = creator.create_process(params)
                    child_ids.append(proc.erpsys_id)

            return SysCallResult(
                True,
                "并行子进程已全部创建",
                data={"child_process_ids": child_ids}
            )
        except Exception as e:
            return SysCallResult(False, f"StartParallelService异常: {e}")

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
    programs = Service.objects.filter(manual_start=True, serve_content_type__model=model_str)
    program_entrypoints = []
    for program in programs:
        first_rule = program.servicerule_set.all().order_by('order').first()
        if first_rule:
            program_entrypoints.append({'title': first_rule.service.label, 'service_rule_id': first_rule.erpsys_id})
    print("program_entrypoints: ", program_entrypoints, "model_str: ", model_str, "programs: ", programs, "first_rule:")
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
