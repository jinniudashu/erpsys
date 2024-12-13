from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.forms.models import model_to_dict
from django.utils import timezone
from django.conf import settings

from datetime import timedelta

from kernel.signals import process_terminated_signal, ux_input_signal
from kernel.models import Process, Service, ServiceRule, Operator
from kernel.types import ProcessState
from kernel.sys_lib import sys_call

@receiver(user_logged_in)
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

def preprocess_context(instance: Process, created: bool) -> dict:
    """预处理上下文"""
    process_context = model_to_dict(instance)
    model_context = model_to_dict(instance.form_content_object) if instance.form_content_object else {}
    # control_context = instance.control_context if instance.control_context else {}
    # schedule_context = instance.schedule_context if instance.schedule_context else {}
    # context = {**model_context, **process_context, **control_context, **schedule_context}
    context = {**model_context, **process_context}
    context.update({"instance": instance})
    context.update({"entity_content_object": instance.entity_content_object})
    context.update({"created": created, "timezone_now": timezone.now()})
    context.update({"parent": instance.parent})
    return context

@receiver(post_save, sender=Process, dispatch_uid="post_save_process")
def on_process_save(sender, instance: Process, created: bool, **kwargs):
    """
    处理进程保存信号
    构造业务上下文，根据业务规则评估业务状态，调度作业
    """
    # 构造进程上下文
    context = preprocess_context(instance, created)

    # 检查过程中调用的值

    # 检查服务相关规则
    rules = ServiceRule.objects.filter(service=instance.service)
    for rule in rules:
        # 向上下文添加业务规则附带的参数值
        # context.update(rule.parameter_values if rule.parameter_values else {})        
        print("检查服务规则：", rule)
        print("规则表达式：", rule.event.expression)
        print("上下文：", context)
        if eval(rule.event.expression, {}, context):
            print("发生--", rule.service, rule.event, "执行->", rule.system_instruction, rule.operand_service)
            sys_call_str = rule.system_instruction.sys_call
            context['sys_call_operand'] = rule.operand_service
            sys_call(sys_call_str, **context)

    # *************************************************
    # 检查表单内服务指令，立即执行/计划执行
    # *************************************************

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
