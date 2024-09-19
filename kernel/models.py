from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

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
        verbose_name = "服务-组织"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Customer(ERPSysBase):
    class Meta:
        verbose_name = "服务-客户"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Role(ERPSysBase):
    service_items = models.ManyToManyField('Service', related_name='roles', blank=True, verbose_name="服务项目")
    class Meta:
        verbose_name = "服务-角色"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Operator(ERPSysBase):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="用户")
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="角色")
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="组织")

    class Meta:
        verbose_name = "服务-人员"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Resource(ERPSysBase):
    class Meta:
        verbose_name = "服务-资源"
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
        verbose_name = "服务-事件"
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

class ServiceRule(ERPSysBase):
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="服务")
    event = models.ForeignKey(Event, on_delete=models.SET_NULL,  blank=True, null=True, verbose_name="事件")
    system_operand = models.ForeignKey(Instruction, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='系统指令')
    next_service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, related_name="ruled_as_next_service", verbose_name="后续服务")
    parameter_values = models.JSONField(blank=True, null=True, verbose_name="参数值")
    order = models.SmallIntegerField(default=0, verbose_name="顺序")

    class Meta:
        verbose_name = "服务-规则"
        verbose_name_plural = verbose_name
        ordering = ['event', 'order']

    def __str__(self):
        return self.label

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
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="服务")
    state = models.CharField(max_length=50, choices=[(state.name, state.value) for state in ProcessState], default=ProcessState.NEW.name, verbose_name="状态")
    scheduled_time = models.DateTimeField(blank=True, null=True, verbose_name="计划时间")
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="操作员")
    program = models.JSONField(blank=True, null=True, verbose_name="程序")
    pc = models.PositiveIntegerField(blank=True, null=True, verbose_name="程序计数器")
    registers = models.JSONField(blank=True, null=True, verbose_name="寄存器")
    io_status = models.JSONField(blank=True, null=True, verbose_name="I/O状态")
    cpu_scheduling = models.JSONField(blank=True, null=True, verbose_name="CPU调度")
    accounting = models.JSONField(blank=True, null=True, verbose_name="帐务")
    sp = models.PositiveIntegerField(blank=True, null=True, verbose_name="栈指针")
    pcb = models.JSONField(blank=True, null=True, verbose_name="进程控制块")
    stack = models.JSONField(blank=True, null=True, verbose_name="栈")  # 存储局部变量、函数参数以及程序的控制流（例如，函数调用时的返回地址）
    heap = models.JSONField(blank=True, null=True, verbose_name="堆")
    schedule_context = models.JSONField(blank=True, null=True, verbose_name="调度上下文")  # 涉及到决定进程执行顺序、分配CPU时间等方面的信息
    control_context = models.JSONField(blank=True, null=True, verbose_name="控制上下文")  # 涉及到进程的状态管理、进程间通信、同步等方面的信息
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    url = models.URLField(blank=True, null=True, verbose_name="URL")
    start_time = models.DateTimeField(blank=True, null=True, verbose_name="开始时间")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="结束时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "服务-进程"
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

class WorkOrder(ERPSysBase):
    process = models.ForeignKey(Process, on_delete=models.CASCADE, verbose_name="进程")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="服务项目")
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="操作员")
    scheduled_time = models.DateTimeField(blank=True, null=True, verbose_name="计划时间")

    class Meta:
        verbose_name = "进程工单"
        verbose_name_plural = verbose_name
        ordering = ['id']

class SysParams(ERPSysBase):
    config = models.JSONField(blank=True, null=True, verbose_name="配置")
    expires_in = models.PositiveIntegerField(default=8, verbose_name="过期时间")

    class Meta:
        verbose_name = "系统参数"
        verbose_name_plural = verbose_name
        ordering = ['id']

"""
进程控制块 - ProcessControlBlock, 用于在多个语义层级上管理业务进程
每个层级是独立的语义空间, 都有各自的独立业务上下文, 有适宜本层语义空间的Assistants Manager对当前层次的进程依照本层级业务规则进行特定操作, 包括：业务事件、调度规则、现场调度控制、初始化进程
1. 跟踪合约进程的状态，确定特定会员的合约执行接下来要做什么？为其中的哪位客户进行哪个服务项目？输出一个服务序列
2. 跟踪服务进程的状态，确定特定客户的服务项目接下来要做什么，什么时候做，谁做？输出一个任务序列
3. 跟踪任务进程的状态，确定特定任务接下来的操作序列是什么？输出一个操作序列

schedule_context: 
进程的优先级
估计或测量的执行时间
截止日期或其他时间限制
资源需求（CPU、内存、I/O 等）
安全或访问控制信息
其他调度策略或参数

control_context:
进程标识和属性（例如 PID、父进程、用户 ID、组 ID）
进程状态（例如，运行、暂停、终止）
进程调度参数（例如，量子、优先级提升、抢占）
进程资源使用情况（例如 CPU 时间、内存、I/O）
进程通信通道（例如管道、套接字、共享内存）
处理安全和访问控制信息
其他过程控制参数或标志

process_program:
解释性语言（例如 Python、Ruby、JavaScript）的字节码文件
shell 或命令语言（例如 Bash、PowerShell、cmd）中的脚本文件

process_data:
程序中定义的全局或静态变量
在运行时分配的动态或堆变量
过程的输入或输出参数
进程使用的临时或中间数据
进程的配置或设置
进程的元数据或统计信息（例如创建时间、修改时间、访问时间）
与过程相关的其他数据或状态信息    
"""

"""
# 结合时间戳和序列号来生成一个唯一且有序的数字ID

import time
import threading

class TimestampIDGenerator:
    def __init__(self):
        self.last_timestamp = None
        self.sequence = 0
        # 用于确保线程安全
        self.lock = threading.Lock()
        # 序列号的最大值，这里假设每个时间戳下最多生成 1000 个唯一ID
        self.SEQUENCE_MASK = 999

    def _current_millis(self):
        # 返回当前时间的毫秒数
        return int(time.time() * 1000)

    def generate_id(self):
        # 生成一个基于时间戳的唯一ID
        with self.lock:
            current_timestamp = self._current_millis()

            if self.last_timestamp == current_timestamp:
                self.sequence = (self.sequence + 1) % (self.SEQUENCE_MASK + 1)
                if self.sequence == 0:
                    # 如果序列号超出范围，等待下一个时间戳
                    while current_timestamp <= self.last_timestamp:
                        current_timestamp = self._current_millis()
            else:
                # 如果当前时间戳与上一次不同，重置序列号
                self.sequence = 0

            self.last_timestamp = current_timestamp

            # 将时间戳和序列号结合生成ID
            id = (current_timestamp * 1000) + self.sequence
            return id

# 示例使用
generator = TimestampIDGenerator()
for _ in range(10):
    print(generator.generate_id())

"""

"""
1. 业务对象描述
2. 业务过程描述
3. 初始数据(initial_data.xlsx, Forms)

# Vocabulary
Organization
Customer
Contract

Service
- Operation
Process
Status
WorkOrder
Workpiece
Metrics
Event
Rule

Form
Field

Resource
- Staff
- Equipment
- Material
- Capital
- Knowledge

Guide
Instruction
Tutorial
Document
Sample

Schedule
Dashboard

Role
Membership
Account(充值记录，消费记录)
ServiceType(["光电类", "护肤品类", "化学焕肤", "手术类", "仪器类", "注射填充类"])
TreatmentRecord
InformedConsent
Precautions
Bill

LaborHours = GenerateTimeSlot([Staff], Calendar, {'Work-hourUnit': config})
EquipmentHours = GenerateTimeSlot([Equipment], Calendar, {'Work-hourUnit': config})

[('超声炮', 'EQUIPMENT'), ('肉毒素注射', 'KNOWLEDGE'), ('超声软组织理疗', 'KNOWLEDGE'), ('Q开关激光', 'KNOWLEDGE'), ('保妥适100单位', 'MATERIAL'), ('超声炮刀头', 'MATERIAL'), ('超声炮炮头', 'MATERIAL'), ('乔雅登极致0.8ml', 'MATERIAL'), ('医生', 'OPERATOR'), ('护士', 'OPERATOR'), ('客服', 'OPERATOR'), ('治疗', 'SKILL'), ('随访', 'SKILL'), ('预约', 'SKILL'), ('备料', 'SKILL')]

# CPU -> 总线 -> 内存、I/O设备...
# 总线提供I/O设备的虚拟化，负责注册、转发
# PCIE总线自带中断控制器
# PCIE总线 -> USB总线 -> USB设备

# 设备驱动程序除了读写, 还要处理配置, 非数据的设备功能依赖ioctl

# Linux命令 taskset => 把进程和特定的CPU绑定在一起
# 公平分享CPU资源 Round-Robin
# 医生每位患者面诊15分钟，是一种轮转调度算法
# 动态优先级调度算法 MLFQ(Multi-Level Feedback Queue)
# Linux调度算法 CFS(Completely Fair Scheduler)
# 调度参数：nice值，优先级（权重？），实时性，时间片大小，调度策略
# 不同岗位的操作员 => 异构处理器

Operating System Services Provide:
1. User Interface: CLI, GUI
2. Program Execution: Source code -> Compiler -> Object code -> Executor
3. I/O Operations
4. File System Manipulation
5. Communications: Inter-process communication, Networking
6. Error Detection: Hardware, Software
7. Resource Allocation: CPU, Memory, I/O devices
8. Accounting: Usage statistics, Billing information -- Which users use how much and what kinds of resources
9. Protection and Security: User authentication, File permissions, Encryption

Types of System Calls
1. Process Control
2. File Manipulation
3. Device Management
4. Information Maintenance
5. Communications

Types of System Programs
1. File Management
2. Status Information
3. File Modification
4. Programming Language Support
5. Program Loading and Execution
6. Communications

syscalls[num]():
SYS_fork
SYS_exit
SYS_wait
SYS_pipe
SYS_read
SYS_kill
SYS_exec
SYS_fstat
SYS_chdir
SYS_dup
SYS_getpid
SYS_sbrk
SYS_sleep
SYS_uptime
SYS_open
SYS_write
SYS_mknod
SYS_unlink
SYS_link
SYS_mkdir
SYS_close
"""
