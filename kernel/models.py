from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db.models.signals import post_save
from django.dispatch import receiver

import uuid
import re
from pypinyin import Style, lazy_pinyin

from kernel.types import ProcessState, ChoiceType
from kernel.app_types import app_types

# ERPSys基类
class ERPSysBase(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")

    class Meta:
        abstract = True

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = str(uuid.uuid1())
        if self.label and self.name is None:
            label = re.sub(r'[^\w\u4e00-\u9fa5]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            # 使用正则表达式过滤掉label非汉字内容, 截取到10个汉字以内
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)

class ERPSysRegistry(ERPSysBase):
    sys_registry = models.JSONField(blank=True, null=True, verbose_name="系统注册表")
    class Meta:
        verbose_name = "系统注册表"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Organization(ERPSysBase):
    class Meta:
        verbose_name = "组织"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Role(ERPSysBase):
    services = models.ManyToManyField('Service', related_name='roles', blank=True, verbose_name="服务项目")
    class Meta:
        verbose_name = "角色"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Operator(ERPSysBase):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="用户")
    role = models.ManyToManyField(Role, blank=True, verbose_name="角色")
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="组织")
    related_staff = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True, verbose_name="关系人")
    context = models.JSONField(blank=True, null=True, verbose_name="上下文")
    processes = GenericRelation('Process', 
                               content_type_field='entity_content_type',
                               object_id_field='entity_object_id',
                               related_query_name='entity')

    class Meta:
        verbose_name = "人员"
        verbose_name_plural = verbose_name
        ordering = ['id']

    def allowed_services(self):
        return list(set(service for role in self.role.all() for service in role.services.all()))

    def get_task_list(self, state_set):
        return self.processes.filter(state__in=state_set)

class Resource(ERPSysBase):
    class Meta:
        verbose_name = "资源"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Service(ERPSysBase):
    config = models.JSONField(blank=True, null=True, verbose_name="配置")

    class Meta:
        verbose_name = "服务"
        verbose_name_plural = verbose_name
        ordering = ["id"]

    def __str__(self):
        return self.label

    def get_service_model_name(self):
        pinyin_list = lazy_pinyin(self.label)
        class_name = ''.join(word[0].upper() + word[1:] for word in pinyin_list)
        return class_name

class Event(ERPSysBase):
    description = models.TextField(max_length=255, blank=True, null=True, verbose_name="描述表达式")
    expression = models.CharField(max_length=255, blank=True, null=True, verbose_name="表达式")
    parameters = models.JSONField(blank=True, null=True, verbose_name="事件参数")

    class Meta:
        verbose_name = "事件"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Instruction(ERPSysBase):
    sys_call = models.CharField(max_length=255, verbose_name="系统调用")
    parameters = models.JSONField(blank=True, null=True, verbose_name="参数")

    class Meta:
        verbose_name = "系统指令"
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.label

class ServiceProgram(ERPSysBase):
    sys_default = models.BooleanField(default=False, verbose_name="系统默认")
    creator = models.ForeignKey(Operator, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="创建者")
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "服务程序"
        verbose_name_plural = verbose_name
        ordering = ['id']

class ServiceRule(ERPSysBase):
    service_program = models.ForeignKey(ServiceProgram, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="服务程序")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="服务")
    event = models.ForeignKey(Event, on_delete=models.SET_NULL,  blank=True, null=True, verbose_name="事件")
    system_instruction = models.ForeignKey(Instruction, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='系统指令')
    operand_service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, related_name="ruled_as_next_service", verbose_name="后续服务")
    parameter_values = models.JSONField(blank=True, null=True, verbose_name="参数值")
    order = models.SmallIntegerField(default=0, verbose_name="顺序")

    class Meta:
        verbose_name = "规则"
        verbose_name_plural = verbose_name
        ordering = ['order', 'service', 'event', 'id']

    def __str__(self):
        return self.label

class WorkOrder(ERPSysBase):
    config = models.JSONField(blank=True, null=True, verbose_name="配置")

    class Meta:
        verbose_name = "工单"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Form(ERPSysBase):
    is_list = models.BooleanField(default=False, verbose_name="列表")
    config = models.JSONField(blank=True, null=True, verbose_name="配置")

    class Meta:
        verbose_name = "表单"
        verbose_name_plural = verbose_name
        ordering = ['id']

class PidField(models.IntegerField):
    def pre_save(self, model_instance, add):
        if add:
            if Process.objects.all().count() == 0:
                pid = 1
            else:
                pid = Process.objects.all().last().pid + 1
            setattr(model_instance, self.attname, pid)
            return pid
        else:
            return super().pre_save(model_instance, add)

class Process(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = PidField(default=0, verbose_name="进程id")
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True, related_name="child_instances", verbose_name="父进程")
    previous = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True, related_name="next_instances", verbose_name="前一个进程")
    entity_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, related_name="as_entity_process")
    entity_object_id = models.PositiveIntegerField(null=True, blank=True)
    entity_content_object = GenericForeignKey('entity_content_type', 'entity_object_id')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="服务")
    state = models.CharField(max_length=50, choices=[(state.name, state.value) for state in ProcessState], default=ProcessState.NEW.name, verbose_name="状态")
    priority = models.PositiveSmallIntegerField(default=0, verbose_name="优先级")
    scheduled_time = models.DateTimeField(blank=True, null=True, verbose_name="计划时间")
    time_window = models.DurationField(blank=True, null=True, verbose_name='时间窗')
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, blank=True, null=True, related_name="as_operator_process", verbose_name="操作员")
    work_order = models.ForeignKey(WorkOrder, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="工单")
    form_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    form_object_id = models.PositiveIntegerField(null=True, blank=True)
    form_content_object = GenericForeignKey('form_content_type', 'form_object_id')
    form_url = models.CharField(max_length=512, blank=True, null=True, verbose_name="路径")
    start_time = models.DateTimeField(blank=True, null=True, verbose_name="开始时间")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="结束时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    accounting = models.JSONField(blank=True, null=True, verbose_name="帐务")
    schedule_context = models.JSONField(blank=True, null=True, verbose_name="调度上下文")  # 涉及到决定进程执行顺序、分配CPU时间等方面的信息
    control_context = models.JSONField(blank=True, null=True, verbose_name="控制上下文")  # 涉及到进程的状态管理、进程间通信、同步等方面的信息
    stack = models.JSONField(blank=True, null=True, verbose_name="栈")  # 存储局部变量、函数参数以及程序的控制流（例如，函数调用时的返回地址）
    program = models.JSONField(blank=True, null=True, verbose_name="程序")
    pc = models.PositiveIntegerField(blank=True, null=True, verbose_name="程序计数器")
    registers = models.JSONField(blank=True, null=True, verbose_name="寄存器")
    io_status = models.JSONField(blank=True, null=True, verbose_name="I/O状态")
    cpu_scheduling = models.JSONField(blank=True, null=True, verbose_name="CPU调度")
    sp = models.PositiveIntegerField(blank=True, null=True, verbose_name="栈指针")
    pcb = models.JSONField(blank=True, null=True, verbose_name="进程控制块")

    class Meta:
        verbose_name = "进程"
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.name if self.name else str(self.pid)

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = str(uuid.uuid1())
        if self.service and self.operator:
            self.name = f"{self.service} - {self.operator}"
        return super().save(*args, **kwargs)
    
    def get_all_children(self):
        children = []
        for child in self.child_instances.all():
            children.append(child)
            children += child.get_all_children()  # Recursively fetch child's children
        return children

    def get_all_siblings(self):
        if self.parent:
            return Process.objects.filter(parent=self.parent).exclude(id=self.id)
        else:
            return Process.objects.none()

    def receive_task(self, operator):
        # 获取作业任务
        self.operator = operator
        self.save()

    def rollback_task(self):
        # 作业任务回退
        self.operator = None
        self.state = ProcessState.NEW.name
        self.save()

    def cancel_task(self, operator):
        # 作业进程撤销
        self.operator = operator
        self.state = ProcessState.TERMINATED.name
        self.save()

    def suspend_or_resume_task(self):
        # 作业进程挂起或恢复
        if self.state == ProcessState.WAITING.name:
            self.state = ProcessState.READY.name
        else:
            self.state = ProcessState.WAITING.name
        self.save()

    def shift_task(self, operator):
        # 作业进程转移操作员
        self.operator = operator
        self.state = ProcessState.READY.name
        self.save()

class ProcessFrameState(ERPSysBase):
    """进程栈帧状态模型"""
    process = models.ForeignKey(Process, on_delete=models.CASCADE, verbose_name="进程")
    parent_frame = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="父栈帧")
    status = models.CharField(max_length=50, verbose_name="状态")
    local_vars = models.JSONField(null=True, blank=True, verbose_name="本地变量")
    inherited_context = models.JSONField(null=True, blank=True, verbose_name="继承上下文")
    return_value = models.JSONField(null=True, blank=True, verbose_name="返回值")
    timestamp = models.DateTimeField(auto_now=True, verbose_name="时间戳")

    class Meta:
        verbose_name = "进程栈帧状态"
        verbose_name_plural = verbose_name
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.process} - {self.status} ({self.timestamp})"

class SysParams(ERPSysBase):
    config = models.JSONField(blank=True, null=True, verbose_name="配置")
    expires_in = models.PositiveIntegerField(default=8, verbose_name="过期时间")

    class Meta:
        verbose_name = "系统参数"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Stacks(ERPSysBase):
    process = models.ForeignKey(Process, on_delete=models.CASCADE, verbose_name="进程")
    stack = models.JSONField(blank=True, null=True, verbose_name="栈")
    heap = models.JSONField(blank=True, null=True, verbose_name="堆")
    sp = models.PositiveIntegerField(blank=True, null=True, verbose_name="栈指针")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "进程栈"
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return str(self.process)