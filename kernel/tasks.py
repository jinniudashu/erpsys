from celery import shared_task
from django_celery_beat.models import PeriodicTask

from abc import ABC, abstractmethod
from typing import Optional
import subprocess

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
        """
        执行系统调用。kwargs 里应包含所需的关键参数，如 process, operand_service, operator, context 等。
        返回 SysCallResult。
        进一步可做：
        - 遇到业务错误（如参数非法）可以抛自定义异常，再由上层捕获并写日志到上下文
        """
        pass

class StartOneServiceCall(SysCallInterface):
    """
    启动一个新的服务进程
    """
    def execute(self, **kwargs) -> SysCallResult:
        """
        必需参数：
            - process: 当前过程
            - operand_service: 要启动的新服务
            - operator: 操作员 (可选，但多数情况下需要)
            - entity_content_object: 新进程的关联业务实体，多数情况下为父进程关联的业务实体
            - ...
        """
        # 1. 参数校验
        if "service_rule" not in kwargs:
            return SysCallResult(
                success=False,
                message="Missing service_rule for start_one_service",
            )
        service_rule = kwargs.get("service_rule")
        operand_service = service_rule.operand_service
        if not isinstance(operand_service, Service):
            return SysCallResult(False, "operand_service is not a valid Service object")
        
        # 2. 业务逻辑：创建新的Process
        parent_process = kwargs.get("process")
        operator = parent_process.operator
        entity_content_object = parent_process.entity_content_object

        params = {
            "parent": parent_process,
            "service_rule": service_rule,
            "service": operand_service,
            "operator": operator,
            "entity_content_object": entity_content_object,
            "name": f"{operand_service.label}",
            "parent_frame": kwargs.get("parent_frame", None),
        }
        print('执行系统调用 start_one_service：', kwargs)
        print('新服务进程创建参数：', params)

        # 3. 创建新的进程
        creator = ProcessCreator()
        # 获取当前进程的父帧
        proc = creator.create_process(params)

        print(f"新服务进程 created: {proc}")

        # 4. 返回成功信息
        return SysCallResult(
            success=True,
            message="Successfully started one service",
            data={"new_process_id": proc.id}
        )

class EndServiceProgramCall(SysCallInterface):
    def execute(self, **kwargs) -> SysCallResult:
        """
        标记当前服务程序结束，或做后续清理
        """
        process = kwargs.get("process")
        if not process:
            return SysCallResult(False, "No process provided")

        # 这里根据您的业务逻辑判断结束条件
        # 示例：将 process 设置为 TERMINATED
        process.state = ProcessState.TERMINATED.name
        process.end_time = timezone.now()
        process.save()

        return SysCallResult(True, f"ServiceProgram ended for process {process.id}")

class StartBatchServiceCall(SysCallInterface):
    def execute(self, **kwargs) -> SysCallResult:
        """
        批量启动服务进程
        """
        pass

class CallServiceProgramCall(SysCallInterface):
    def execute(self, **kwargs) -> SysCallResult:
        """
        调用服务程序
        """
        pass

class ReturnCallingServiceCall(SysCallInterface):
    def execute(self, **kwargs) -> SysCallResult:
        """
        返回调用服务
        """
        pass

class UpdateResourceStateCall(SysCallInterface):
    def execute(self, **kwargs) -> SysCallResult:
        """
        更新资源状态
        """
        print('更新资源状态：', self, kwargs)

        return SysCallResult(
            success=True,
            message="Successfully updated resource state",
            data={"resource_id": kwargs.get("resource_id")}
        )            
        
CALL_REGISTRY = {
    "start_one_service": StartOneServiceCall,
    "start_batch_service": StartBatchServiceCall,
    "end_service_program": EndServiceProgramCall,
    "call_service_program": CallServiceProgramCall,
    "return_calling_service": ReturnCallingServiceCall,
    "update_resource_state": UpdateResourceStateCall,
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


@shared_task
def task_backup_data():
    subprocess.run(['python', 'backup.py', 'crontab'])

@shared_task
def execute_sys_call_task(sys_call_name: str, context: dict) -> dict:
    """仅作为异步执行入口"""
    print('执行异步任务：execute_sys_call_task')
    # 这里简化处理，直接将 context 传给 sys_call
    result = sys_call(sys_call_name, **context)  # 调用同步实现
    print('异步任务执行结果：', result)
    return {
        "success": result.success,
        "message": result.message,
        "data": result.data
    }

@shared_task
def timer_interrupt(task_name):
    # get timer.pid
    # get pid.stack
    # get pid.stack.pc
    # execute pid.stack.pc
    try:
        task = PeriodicTask.objects.get(name=task_name)
        print("Task arguments:", task.args)
    except PeriodicTask.DoesNotExist:
        print("Task not found")    
    return task

# 新建测试任务
# @shared_task
# def connection_test():
#     import redis
#     r = redis.Redis(host='127.0.0.1', port=6379, db=1)
#     return r.ping()
