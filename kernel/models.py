from django.db import models, transaction
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import JSONField  # 使用PostgreSQL的JSONField

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
    active = models.BooleanField(default=False, verbose_name="启用")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='operator', verbose_name="用户")
    role = models.ManyToManyField(Role, blank=True, verbose_name="角色")
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="组织")
    related_staff = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True, verbose_name="关系人")
    context = models.JSONField(blank=True, null=True, verbose_name="上下文")
    processes = GenericRelation('Process', content_type_field='entity_content_type', object_id_field='entity_object_id', related_query_name='entity')

    class Meta:
        verbose_name = "人员"
        verbose_name_plural = verbose_name
        ordering = ['id']

    def allowed_services(self):
        return list(set(service for role in self.role.all() for service in role.services.all()))

    def get_task_list(self, state_set):
        return self.processes.filter(state__in=state_set)

    def switch_task(self, from_process, to_process):
        with ProcessExecutionContext(from_process, mode='write'):
            from_process.state = ProcessState.WAITING.name
            from_process.save()
        with ProcessExecutionContext(to_process, mode='read'):
            to_process.state = ProcessState.RUNNING.name
            to_process.operator = self
            to_process.save()

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

    def save(self, *args, **kwargs):
        if self.expression:
            # 将表达式中的进程相关字段替换为带前缀的形式
            process_fields = {
                'state': 'process_state',
                'name': 'process_name',
                'service': 'process_service',
                'priority': 'process_priority',
                'created_at': 'process_created_at',
            }
            
            expression = self.expression
            for old_key, new_key in process_fields.items():
                # 使用正则表达式确保只替换独立的字段名
                expression = re.sub(r'\b' + old_key + r'\b', new_key, expression)
            self.expression = expression
            
        super().save(*args, **kwargs)

class Instruction(ERPSysBase):
    sys_call = models.CharField(max_length=255, verbose_name="系统调用")
    parameters = models.JSONField(blank=True, null=True, verbose_name="参数")

    class Meta:
        verbose_name = "系统指令"
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.label

class ServiceLibrary(ERPSysBase):
    belongs_to_service = models.ForeignKey(Service, on_delete=models.CASCADE, blank=True, null=True, related_name='services_belong_to', verbose_name="隶属服务")
    order = models.SmallIntegerField(default=0, verbose_name="顺序")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="服务")
    event = models.ForeignKey(Event, on_delete=models.SET_NULL,  blank=True, null=True, verbose_name="事件")
    system_instruction = models.ForeignKey(Instruction, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='系统指令')
    operand_service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, related_name="kernel_ruled_as_next_service_func", verbose_name="后续服务")
    entity_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, related_name="kernel_service_func", verbose_name="实体类型")
    entity_object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="实体ID")
    entity_content_object = GenericForeignKey('entity_content_type', 'entity_object_id')
    parameter_values = models.JSONField(blank=True, null=True, verbose_name="参数值")

    class Meta:
        verbose_name = "服务函数库"
        verbose_name_plural = verbose_name
        ordering = ['belongs_to_service', 'order', 'service', 'event', 'id']

    def __str__(self):
        return self.label

class ServiceProgram(ERPSysBase):
    version = models.CharField(max_length=255, blank=True, null=True, verbose_name="版本")
    sys_default = models.BooleanField(default=False, verbose_name="系统默认")
    entity_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, related_name="as_entity_program", verbose_name="实体类型")
    entity_object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="实体ID")
    entity_content_object = GenericForeignKey('entity_content_type', 'entity_object_id')
    manual_start = models.BooleanField(default=True, verbose_name="手动启动")
    active = models.BooleanField(default=True, verbose_name="启用")
    creator = models.ForeignKey(Operator, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="创建者")
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "服务程序"
        verbose_name_plural = verbose_name
        ordering = ['id']

class ServiceRule(ERPSysBase):
    service_program = models.ForeignKey(ServiceProgram, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="服务程序")
    order = models.SmallIntegerField(default=0, verbose_name="顺序")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="服务")
    event = models.ForeignKey(Event, on_delete=models.SET_NULL,  blank=True, null=True, verbose_name="事件")
    system_instruction = models.ForeignKey(Instruction, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='系统指令')
    operand_service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, related_name="ruled_as_next_service", verbose_name="后续服务")
    entity_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, related_name="kernel_service_rule", verbose_name="实体类型")
    entity_object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="实体ID")
    entity_content_object = GenericForeignKey('entity_content_type', 'entity_object_id')
    parameter_values = models.JSONField(blank=True, null=True, verbose_name="参数值")

    class Meta:
        verbose_name = "服务规则"
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
    creator = models.ForeignKey(Operator, on_delete=models.SET_NULL, blank=True, null=True, related_name="as_creator_process", verbose_name="创建者")
    work_order = models.ForeignKey(WorkOrder, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="工单")
    form_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, verbose_name="表单类型")
    form_object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="表单ID")
    form_content_object = GenericForeignKey('form_content_type', 'form_object_id')
    form_url = models.CharField(max_length=512, blank=True, null=True, verbose_name="表单路径")
    start_time = models.DateTimeField(blank=True, null=True, verbose_name="开始时间")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="结束时间")
    program_entrypoint = models.CharField(max_length=255, blank=True, null=True, verbose_name="程序入口")
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")

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
        super().save(*args, **kwargs)

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

class ProcessContextSnapshot(models.Model):
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    process = models.ForeignKey('Process', on_delete=models.CASCADE, verbose_name="进程")
    version = models.PositiveIntegerField(default=1, verbose_name="版本号")
    context_data = models.JSONField(null=True, blank=True, verbose_name="上下文数据")
    context_hash = models.CharField(max_length=64, null=True, blank=True, verbose_name="上下文哈希")
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "进程上下文快照"
        verbose_name_plural = verbose_name
        ordering = ['-version']
        unique_together = ('process', 'version')

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = str(uuid.uuid1())
        super().save(*args, **kwargs)

class ResourceRequirement(ERPSysBase):
    resource_type = models.CharField(max_length=50, verbose_name="资源类型")
    capacity = models.PositiveIntegerField(default=1, verbose_name="容量")  # 表示该资源能同时支持多少个进程（如 1 表示独占，>1 表示可并发）

    class Meta:
        verbose_name = "资源需求"
        verbose_name_plural = verbose_name
        ordering = ['id']

class ResourceCalendar(ERPSysBase):
    resource = models.ForeignKey(ResourceRequirement, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="资源")
    start_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(verbose_name="结束时间")

    class Meta:
        verbose_name = "资源日历"
        verbose_name_plural = verbose_name
        ordering = ['id']

class ResourceStatus(ERPSysBase):
    capacity = models.PositiveIntegerField(default=1, verbose_name="容量")  # 表示该资源能同时支持多少个进程（如 1 表示独占，>1 表示可并发）
    current_usage = models.PositiveIntegerField(default=0, verbose_name="当前使用量")  # 表示当前已被多少进程占用
    busy_until = models.DateTimeField(null=True, blank=True, verbose_name="忙碌到期时间")  # 如果有时间限制，例如某资源会在某个时间之前保持忙碌

    class Meta:
        verbose_name = "资源状态"
        verbose_name_plural = verbose_name
        ordering = ['id']

class SysParams(ERPSysBase):
    config = models.JSONField(blank=True, null=True, verbose_name="配置")
    expires_in = models.PositiveIntegerField(default=8, verbose_name="过期时间")

    class Meta:
        verbose_name = "系统参数"
        verbose_name_plural = verbose_name
        ordering = ['id']
