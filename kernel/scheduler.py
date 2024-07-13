from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.forms.models import model_to_dict
from django.utils import timezone

from enum import Enum, auto

from kernel.signals import timer_signal, ux_input_signal
from kernel.models import Process, Service, ServiceRule

# 从两类四种Django信号解析业务事件
# 一、全局信号
# 1. 用户登录信号
# 2. 人工指令信号
# 3. 系统时钟信号
# 二、服务进程状态信号
# 4. Process实例状态变更信号

# 以业务事件为参数，查表ServiceRule，执行SOP

def regular_routine_scheduler(instance: Process, rules: list[ServiceRule], context: dict) -> None:
    """遍历规则，评估是否发生业务事件"""
    for rule in rules:
        # 向上下文添加业务规则附带的参数值
        context.update(rule.parameter_values if rule.parameter_values else {})
        context.update({"instance": instance})
        
        # 获取规则表达式
        expression = rule.event.expression

        print("")
        print("检查服务规则：", rule)
        print("规则表达式：", expression)
        print("上下文：", context)
        # 在给定的上下文中, 检测是否发生业务事件, 如果发生, 则执行SOP
        if eval(expression, {}, context):
            # 加载器 loader 执行sop代码
            exec(rule.sop.program_code, None, context)

def preprocess_context(instance: Process, created: bool) -> dict:
    """预处理上下文"""
    pid_context = model_to_dict(instance)
    model_context = model_to_dict(instance.content_object)
    control_context = instance.control_context if instance.control_context else {}
    schedule_context = instance.schedule_context if instance.schedule_context else {}
    context = {**model_context, **pid_context, **control_context, **schedule_context}
    context.update({"created": created, "timezone_now": timezone.now()})
    return context

@receiver(user_logged_in)
def on_user_login(sender, user, request, **kwargs):
    print(f"用户{user.username}登录。。。") 
    # 在Process表中创建一个新的Process实例, state=TERMINATED
    if request.path == '/applications/login/':  # 后台登录
        # 获得登陆作业进程参数
        # event_name = 'doctor_login'
        # login_service = Service.objects.get(name=event_name)
        # operator = user.operator
        print('职员登录', user)

        # 创建一个状态为“已完成”的职员/客户登录作业进程
        # new_proc=Process.objects.create(
        #     service=login_service,
        #     operator=operator,
        #     state="TERMINATED",
        # )

@receiver(post_save, sender=Process, dispatch_uid="post_save_pcb")
def schedule_process_updating(sender, instance: Process, created: bool, **kwargs) -> None:
    """接收Process实例更新信号, 调度作业"""
    # 获取PCB实例对应的Model实例
    model_instance = instance.content_object
    # loaddata时model_instance为None, 避免loaddata时调用
    if model_instance:
        # 构造进程上下文
        context = preprocess_context(instance, created)
        rules = []
        rules = ServiceRule.objects.filter(event__is_timer=False)

        # Schedule in regular routine
        regular_routine_scheduler(instance, rules, context)

@receiver(ux_input_signal)
def schedule_ux_input(**kwargs):
    """接收人工指令调度"""
    """
    系统外部输入中断信号，需要即时响应
    优先级最高
    """
    pass

@receiver(timer_signal)
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
