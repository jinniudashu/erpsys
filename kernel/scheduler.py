from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.forms.models import model_to_dict
from django.utils import timezone
from datetime import timedelta

from enum import Enum, auto

from kernel.signals import process_terminated_signal, ux_input_signal
from kernel.models import Process, Service, ServiceRule, Operator
from kernel.types import ProcessState
from kernel.sys_lib import sys_create_process, add_periodic_task


@receiver(user_logged_in)
def on_user_login(sender, user, request, **kwargs):
    if request.path == '/applications/login/':  # 应用登录
        # 创建一个登录进程, state=TERMINATED
        params = {
            'service': Service.objects.get(name='user_login'),
            'operator': Operator.objects.get(user=user),
            'state': ProcessState.TERMINATED.name,
        }
        Process.objects.create(**params)

# 从两类四种Django信号解析业务事件
# 一、全局信号
# 1. 用户登录信号
# 2. 人工指令信号
# 3. 系统时钟信号
# 二、服务进程状态信号
# 4. Process实例状态变更信号

# 以业务事件为参数，查表ServiceRule，执行SOP

def schedule(rule, **kwargs):
    def create_process(**kwargs):
        kwargs['service'] = rule.next_service

        # 准备新的服务作业进程参数
        # operation_proc = kwargs['operation_proc']
        # customer = operation_proc.customer
        # current_operator = kwargs['operator']

        # 创建新的服务作业进程
        proc = sys_create_process(**kwargs)

        return proc
    
    def create_batch_process(**kwargs):
        def _get_schedule_times(form_data, **kwargs):
            def _get_basetime():
                '''
                返回最近整点时间
                '''
                # 获取当前时间
                now = timezone.now()                    
                # 获取当前小时数并加1
                next_hour = now.hour + 1
                # 如果当前小时数为23时，将小时数设置为0，并增加一天
                if next_hour == 24:
                    next_hour = 0
                    now += timezone.timedelta(days=1)
                # 使用replace()方法设置新的小时数，并重置分钟、秒和微秒为0
                nearest_hour = now.replace(hour=next_hour, minute=0, second=0, microsecond=0)
                return nearest_hour

            # 获取基准时间
            base_time = _get_basetime()
            
            # 从对应字段提取参数信息，生成计划时间列表
            if type(form_data) == dict:
                form_item = form_data
            else:
                form_item = form_data[0]

            period_number = int(re.search(r'(\d+)', form_item.get(kwargs['hssc_duration']['field_name'], '0')).group(1))
            frequency = int(re.search(r'(\d+)', form_item.get(kwargs['hssc_frequency']['field_name'], '0')).group(1))

            schedule_times = []
            for day_x in range(period_number):
                for batch in range(frequency):
                    schedule_times.append(base_time + timedelta(hours=batch*4))
                base_time = base_time + timedelta(days=1)
            return schedule_times

        # 准备新的服务作业进程参数
        proc = kwargs['operation_proc']
        service = kwargs['next_service']

        params = {}
        params['service'] = service  # 进程所属服务
        params['customer'] = proc.customer  # 客户
        params['creater'] = kwargs['operator']   # 创建者  
        params['operator'] = None  # 未分配服务作业人员
        params['priority_operator'] = kwargs['priority_operator'] # 优先操作者
        params['state'] = 0  # or 根据服务作业权限判断
        params['parent_proc'] = proc  # 当前进程是被创建进程的父进程
        params['contract_service_proc'] = proc.contract_service_proc  # 所属合约服务进程
        params['passing_data'] = kwargs['passing_data']
        params['form_data'] = kwargs['form_data']  # 表单数据
        params['apply_to_group'] = kwargs.get('apply_to_group')  # 分组标识
        params['coroutine_result'] = kwargs.get('coroutine_result', None)  # 协程结果


        # 获取服务表单的API字段
        api_fields = proc.service.buessiness_forms.all()[0].api_fields
        if api_fields:
            operators = []
            hssc_operator = api_fields.get('hssc_operator', None)
            if hssc_operator:
                # 获取服务作业人员列表
                _operators = kwargs['form_data'].get(hssc_operator['field_name'], None)
                # 如果_operators不是列表，转化为列表
                if type(_operators) == list or isinstance(_operators, models.QuerySet):
                    operators = _operators
                else:
                    operators = [_operators]
            
            schedule_times = []
            hssc_duration = api_fields.get('hssc_duration', None)
            hssc_frequency = api_fields.get('hssc_frequency', None)
            if hssc_duration and hssc_frequency:
                # 解析表单内容，生成计划时间列表
                schedule_times = _get_schedule_times(kwargs['form_data'], **{'hssc_duration': hssc_duration, 'hssc_frequency': hssc_frequency})

        # 如果有服务作业人员列表，按服务作业人员生成服务作业进程
        if operators:
            for operator in operators:
                if isinstance(operator, VirtualStaff):
                    params['operator'] = operator.staff.customer
                elif isinstance(operator, Staff):
                    params['operator'] = operator.customer
                elif isinstance(operator, Customer):
                    params['operator'] = operator
                if schedule_times:
                    for schedule_time in schedule_times:
                        # 估算计划执行时间
                        params['scheduled_time'] = schedule_time            
                        # 创建新的服务作业进程
                        new_proc = create_service_proc(**params)
                else:
                    # 估算计划执行时间为当前时间加1小时
                    params['scheduled_time'] = timezone.now() + timedelta(hours=1)
                    new_proc = create_service_proc(**params)

            count_proc = len(operators)
        else:
            for schedule_time in schedule_times:
                # 估算计划执行时间
                params['scheduled_time'] = schedule_time            
                # 创建新的服务作业进程
                new_proc = create_service_proc(**params)

            count_proc = len(schedule_times)

        # 显示提示消息：开单成功
        messages.add_message(kwargs['request'], messages.INFO, f'{service.label}已开单{count_proc}份')
        return f'创建{count_proc}个服务作业进程: {new_proc}'

    def send_back(**kwargs):
        '''
        退单
        '''
        # 获取当前进程的父进程
        proc = kwargs['operation_proc']
        parent_proc = proc.parent_proc
        if parent_proc and parent_proc.service == kwargs['next_service']:  # 如果父进程服务是规则指定的下一个服务，执行退单
            parent_proc.return_form()
            print('退回表单 至:', parent_proc)

    SysCallMap = {
        'create_process': create_process,
        'create_batch_process': create_batch_process,
        'send_back': send_back,
    }

    # 加载器 loader 执行sop代码
    print("发生--", rule.service, rule.event, "执行->", rule.system_operand, rule.next_service)
    sys_call = rule.system_operand.sys_call
    SysCallMap[sys_call](**kwargs)

    return None

def preprocess_context(instance: Process, created: bool) -> dict:
    """预处理上下文"""
    pid_context = model_to_dict(instance)
    model_context = model_to_dict(instance.content_object) if instance.content_object else {}
    control_context = instance.control_context if instance.control_context else {}
    schedule_context = instance.schedule_context if instance.schedule_context else {}
    context = {**model_context, **pid_context, **control_context, **schedule_context}
    context.update({"instance": instance})
    context.update({"created": created, "timezone_now": timezone.now()})
    return context

@receiver(post_save, sender=Process, dispatch_uid="post_save_process")
def schedule_process_updating(sender, instance: Process, created: bool, **kwargs) -> None:
    """接收Process实例更新信号, 调度作业"""
    # 构造进程上下文
    context = preprocess_context(instance, created)

    rules = ServiceRule.objects.filter(service=instance.service)
    for rule in rules:
        # 向上下文添加业务规则附带的参数值
        # context.update(rule.parameter_values if rule.parameter_values else {})        
        print("检查服务规则：", rule)
        print("规则表达式：", rule.event.expression)
        print("上下文：", context)
        if eval(rule.event.expression, {}, context):
            schedule(rule, **context)

@receiver(ux_input_signal)
def schedule_ux_input(**kwargs):
    """接收人工指令调度"""
    """
    系统外部输入中断信号，需要即时响应
    优先级最高
    """
    pass

def schedule_timer(**kwargs):
    # 将Celery的定时任务信号转译为业务事件
    """接收定时信号调度"""
    """
    操作系统时钟中断信号，
    可检查各业务进程状态，启动提醒服务进程、分析报告服务进程等
    优先级最低
    """
    # ??? 每分钟执行一次，查询所有定时规则，检查是否满足条件，满足则执行SOP
    rules = ServiceRule.objects.filter(event__is_timer=True)
    print("timer_signal was received.", rules, kwargs)

    # Prepare instances for timer_signal
    instances = []
    
    # 构造服务进程上下文

    # Schedule in timer routine
    for rule in rules:
        pass

class SystemCall(Enum):
    """系统调用枚举类"""
    CreateService = auto()
    CallService = auto()

    def __str__(self):
        return self.name

class Scheduler:
    def __init__(self):
        self.job_handlers = {
            SystemCall.CreateService: self.create_service,
            SystemCall.CallService: self.call_service,
        }

    def schedule(self, sys_call, **kwargs):
        handler = self.job_handlers.get(sys_call)
        if handler:
            return handler(**kwargs)
        else:
            raise ValueError(f"Unhandled job type: {sys_call}")

    # Define job functions
    def create_service(self, **kwargs):
        print("Creating service...")
        # Actual implementation here

    def call_service(self, **kwargs):
        print("Call service...")
        # Actual implementation here

class TuringMachine:
    def __init__(self, program, initial_state):
        self.program = program  # 程序是一个字典，键为(状态, 读取的值)，值为(写入的值, 移动方向, 下一个状态)
        self.state = initial_state  # 图灵机的初始状态
        self.tape = [0] * 1000  # 初始化一个有1000个格的纸带，所有格初始化为0
        self.head = len(self.tape) // 2  # 读写头初始在纸带中间位置
        self.counter = 0  # 程序计数器

    def step(self):
        """执行图灵机的一个步骤"""
        key = (self.state, self.tape[self.head])
        if key in self.program:
            value, direction, next_state = self.program[key]
            self.tape[self.head] = value
            if direction == 'R':
                self.head += 1
            elif direction == 'L':
                self.head -= 1
            self.state = next_state
            self.counter += 1
        else:
            print("No valid instruction, machine halts.")
            return False
        return True

    def run(self):
        """运行图灵机，直到没有有效的指令为止"""
        while self.step():
            pass
        print("Machine halted after", self.counter, "steps.")
        print("Final tape state:", self.tape[self.head-10:self.head+10])

# # 示例用法
# program = {
#     (0, 0): (1, 'R', 1),
#     (1, 0): (1, 'L', 0),
#     (1, 1): (0, 'R', 0),
#     (0, 1): (1, 'L', 1),
# }
# tm = TuringMachine(program, 0)
# tm.run()
