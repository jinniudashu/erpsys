from django.conf import settings
from django_celery_beat.models import PeriodicTask, IntervalSchedule

import json
from typing import List, Dict, Any

from kernel.models import Service, Process
from kernel.types import ProcessState

"""
工作流引擎的实现思路
1. 工作流以状态机为基础，状态机以状态为节点，状态以业务事件驱动的服务项目为迁移单元。
2. 服务项目以服务实例为执行实例，服务实例是工作流引擎的执行单元，服务实例包含服务项目和业务上下文。
3. 业务上下文包含工作流引擎需要的所有业务信息，根据需要可灵活配置。
4. 工作流引擎根据业务程序内置的业务规则触发业务事件，创建人工任务服务实例或执行自动任务服务实例，或进入守候状态，直至工作流完成

一般工作流结构
1. 初始业务事件是登录，登录后进入守候状态，等待业务事件触发。
2. 业务事件包括：人工主动触发、系统定时触发、任务完成后由系统工作流引擎触发，没有业务事件时，工作流进入守候状态。
3. 业务状态持续由业务事件驱动的状态迁移，直至工作流完成。
"""

class 服务项目:
    """服务项目"""
    def __init__(self, name: str):
        self.name = name
        self.service_orm = Service.objects.get(label=name)
        self.config = self.service_orm.config
        return self

class 服务实例:
    """服务实例"""
    def __init__(self, service_item: 服务项目, biz_context: dict):
        self.service_item = service_item
        self.biz_context = biz_context
        self.pid = None
        self.result = None
        return self.create_process()

    def start(self):
        pass

    def complete(self):
        return self.result
    
    def create_record(self):
        model_name = self.service_item.config['subject']['name']
        params = {
            'label': self.service_item.label,
            'pid': self.pid,
            'master': self.biz_context.get('master', None)
        }
        return eval(model_name).objects.create(**params)

    def create_process(self):
        params = {
            'name': self.service_item.label,
            'parent': self.biz_context.get('master', None),
            'service': self.service_item.service_orm,
            'customer': self.biz_context.get('customer', None),
            'state': ProcessState.NEW.name,
            'priority': 0
        }
        proc = Process.objects.create(**params)
        self.pid = proc.pid
        self.result = self.create_record()
        proc.content_object = self.result
        proc.form_url = f'/{settings.CUSTOMER_SITE_NAME}/applications/{self.service_item.service_orm.config['subject']['name'].lower()}/{proc.id}/change/'
        proc.save()

        return proc

    def create_periodic_task(self, every: int, task_name: str):
        interval_schedule, created = IntervalSchedule.objects.get_or_create(
            every=every,
            period=IntervalSchedule.SECONDS,
        )
        periodic_task = PeriodicTask.objects.create(
            name=task_name,
            interval=interval_schedule,
            task='kernel.tasks.timer_interrupt',
            args=json.dumps([task_name]),  # 将任务名作为参数传递
            one_off=True
        )
        return periodic_task

class BizState:
    """业务状态"""
    def __init__(self, service_instance: 服务实例, biz_context: dict):
        self.state = service_instance
        self.biz_context = biz_context
        return self

class WorkflowEngine:
    预约登记 = 服务项目('预约登记')
    预约提醒 = 服务项目('预约提醒')
    提醒预约 = 服务项目('提醒预约')

    预约到诊确认 = 服务项目('预约到诊确认')
    维护客户档案 = 服务项目('维护客户档案')
    健康调查 = 服务项目('健康调查')

    面诊评估 = 服务项目('面诊评估')
    诊断及处理 = 服务项目('诊断及处理')

    收费 = 服务项目('收费')

    签署知情同意书 = 服务项目('签署知情同意书')
    专科治疗 = ['保妥适肉毒素', '黄金微针', '光子', '果酸', '水光针', '超声炮']
    治疗 = 服务项目(专科治疗)
    核销治疗项目 = 服务项目('核销治疗项目')
    术后注意事项提醒 = 服务项目('术后注意事项提醒')

    提醒随访 = 服务项目('提醒随访')
    随访 = 服务项目('随访')

    def __init__(self, program: list, initial_state:BizState, current_state: BizState, pid: str):
        self.program = program
        self.initial_state = initial_state
        self.current_state = current_state
        self.pid = pid

    def create_human_task(self, task: 服务实例, context: Dict[str, Any]):
        self.task_queue.put((task, context))

    def create_parallel_human_tasks(self, tasks: List[服务实例], context: Dict[str, Any]):
        for task in tasks:
            self.create_human_task(task, context)

    def run_auto_task(self, task: 服务实例, context: Dict[str, Any]):
        print(f"运行自动任务: {task.service_item.name}，执行动作：{task.service_item.config['action']['action_func_name']}")        

    def run_parallel_auto_tasks(self, tasks: List[服务实例], context: Dict[str, Any]):
        for task in tasks:
            self.run_auto_task(task, context)

    def eval_task_result(self, biz_context: dict):
        """
        评估任务结果：
        1. 根据表单结果，评估是否发生了预设的业务事件；
        2. 由局部到全局进行评估；
        3. 根据业务事件，确定是否需要创建新的任务；
        """
        pass

    def scheduler(self):
        pass

    def start(self):
        self.current_state = next(state for state in self.workflow['states'] if state['type'] == 'start')
        return self.execute_state()

    def execute_state(self) -> Dict[str, Any]:
        if self.current_state['type'] == 'end':
            return {'status': 'completed'}

        action = getattr(self, self.current_state.get('action', 'no_op'))
        result = action()

        next_state_name = self.current_state.get('next')
        if next_state_name:
            self.current_state = next(state for state in self.workflow['states'] if state['name'] == next_state_name)
        
        return {'status': 'in_progress', 'current_state': self.current_state['name'], 'result': result}

    def no_op(self):
        return "No operation performed"

    def run(self):
        while self.current_state['status'] != 'completed':
            print(f"执行状态: {self.current_state['current_state']}, 执行任务: {self.current_state['task']}")
            self.execute_state()

        print("工作流执行完成")

