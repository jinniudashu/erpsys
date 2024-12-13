#1. 上下文栈帧设计
class ContextFrame:
    def __init__(self, process: Process, parent_frame=None):
        self.process = process
        self.parent_frame = parent_frame
        self.local_vars = {}  # 本地变量
        self.return_value = None  # 返回值
        self.status = 'ACTIVE'  # 栈帧状态
        
        # 继承父栈帧的相关上下文
        if parent_frame:
            self.inherited_context = parent_frame.get_inheritable_context()
            
    def get_inheritable_context(self):
        """获取可继承的上下文变量"""
        return {
            'customer': self.process.customer,
            'contract': self.process.contract_service_proc,
            'business_context': parent_frame.process.business_context
            # 其他需要继承的上下文...
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

class ProcessStateManager:
    """进程状态持久化管理器"""
    def save_frame_state(self, frame: ContextFrame) -> dict:
        """保存栈帧状态"""
        state = {
            'process_id': frame.process.id,
            'parent_frame_id': frame.parent_frame.id if frame.parent_frame else None,
            'status': frame.status,
            'local_vars': self._serialize_vars(frame.local_vars),
            'inherited_context': self._serialize_vars(frame.inherited_context),
            'return_value': self._serialize_vars(frame.return_value),
            'timestamp': timezone.now()
        }
        return ProcessFrameState.objects.create(**state)

    def restore_frame_state(self, process_id: int) -> ContextFrame:
        """恢复栈帧状态"""
        state = ProcessFrameState.objects.get(process_id=process_id)
        frame = ContextFrame(
            process=Process.objects.get(id=process_id),
            parent_frame=self._restore_parent_frame(state.parent_frame_id)
        )
        frame.local_vars = self._deserialize_vars(state.local_vars)
        frame.inherited_context = self._deserialize_vars(state.inherited_context)
        frame.status = state.status
        frame.return_value = self._deserialize_vars(state.return_value)
        return frame
    
# 2. 上下文管理器
class ProcessContextManager:
    def __init__(self, process: Process):
        self.process = process
        self.frame = None
        self.state_manager = ProcessStateManager()

    def __enter__(self):
        try:
            # 尝试恢复已存在的状态
            self.frame = self.state_manager.restore_frame_state(self.process.id)
        except ProcessFrameState.DoesNotExist:
            # 创建新的栈帧
            parent_frame = get_current_active_frame()
            self.frame = ContextFrame(self.process, parent_frame)
        
        # 保存初始状态
        self.state_manager.save_frame_state(self.frame)
        return self.frame

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self._handle_completion()
            else:
                self._handle_exception(exc_val)
        finally:
            # 保存最终状态
            self.state_manager.save_frame_state(self.frame)
                
    def _handle_completion(self, frame):
        # 处理返回值
        if frame.return_value:
            self._process_return_value(frame)
            
        # 触发规则评估
        self._evaluate_rules(frame)

# 3. 任务执行集成
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

#4. 规则评估集成
class RuleEvaluator:
    def __init__(self, context_frame: ContextFrame):
        self.frame = context_frame
        
    def evaluate(self):
        """评估当前上下文中的规则"""

        eval_context = self._build_evaluation_context()

        rules = get_applicable_rules(context.process)
        for rule in rules:
            if rule.evaluate(eval_context):
                # 执行规则定义的操作
                execute_rule_action(rule, eval_context)

        # rules = ServiceRule.objects.filter(service=self.frame.process.service)        
        # for rule in rules:
        #     if eval(rule.event.expression, {}, context):
        #         self._execute_rule_action(rule, context)
                
    def _build_evaluation_context(self):
        """构建规则评估上下文"""
        eval_context = {
            'process': self.frame.process,
            'result': self.frame.return_value,
            'local_vars': self.frame.local_vars,
            'inherited_context': self.frame.inherited_context
        }

        context = {}
        # 合并当前帧的本地变量
        context.update(self.frame.local_vars)
        # 合并继承的上下文
        context.update(self.frame.inherited_context)
        # 添加进程相关信息
        context.update(preprocess_context(self.frame.process, False))
        return context
    
