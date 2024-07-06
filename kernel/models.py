from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

import uuid

from kernel.types import ProcessState
from kernel.app_types import app_types
from design.models import Service
from maor.models import *

class SystemInstruction(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="名称")
    sys_call = models.CharField(max_length=255, verbose_name="系统调用")
    parameters = models.JSONField(blank=True, null=True, verbose_name="参数")

    class Meta:
        verbose_name = "系统指令"
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.name

class Process(models.Model):
    pid = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="进程id")
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True, related_name="child_instances", verbose_name="父进程")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="服务")
    state = models.CharField(max_length=50, choices=[(state.name, state.value) for state in ProcessState], default=ProcessState.NEW.name, verbose_name="状态")
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
    start_time = models.DateTimeField(blank=True, null=True, verbose_name="开始时间")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="结束时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "进程"
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return str(self.pid)

    def save(self, *args, **kwargs):
        if self.pid is None:
            self.pid = uuid.uuid1()

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

class WorkOrder(models.Model):
    process = models.ForeignKey(Process, on_delete=models.CASCADE, verbose_name="进程")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="服务")
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="操作员")
    scheduled_time = models.DateTimeField(blank=True, null=True, verbose_name="计划时间")

class Stacks(models.Model):
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