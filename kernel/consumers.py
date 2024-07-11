from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

import json

from kernel.models import Operator
from kernel.sys_lib import update_unassigned_procs, update_staff_todo_list, update_customer_services_list

# 职员任务工作台待分配服务进程列表
class UnassignedProcsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('unassigned_procs', self.channel_name)
        await self.accept()
        print('from UnassignedProcsConsumer:', self.scope['user'])
        # 获取操作员，获取有操作权限的服务id列表，发送给客户端
        # operator = await sync_to_async(Operator.objects.get)(user=self.scope['user'])
        operator = await sync_to_async(Operator.objects.get)(name='SystemSchedler')
        # 初始化更新职员任务工作台待分配服务进程列表
        await sync_to_async(update_unassigned_procs)(operator)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('unassigned_procs', self.channel_name)
        self.close()

    async def send_unassigned_procs(self, event):
        new_data = event['data']
        await self.send(json.dumps(new_data))

# 职员任务工作台Consumer，实时更新职员任务列表
class StaffTodoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # operator = await sync_to_async(Operator.objects.get)(user=self.scope['user'])
        operator = await sync_to_async(Operator.objects.get)(name='SystemSchedler')
        await self.channel_layer.group_add(operator.erpsys_id, self.channel_name)
        await self.accept()
        
        # 初始化更新职员任务列表
        await sync_to_async(update_staff_todo_list)(operator)

    async def disconnect(self, close_code):
        # operator = await sync_to_async(Operator.objects.get)(user=self.scope['user'])
        operator = await sync_to_async(Operator.objects.get)(name='SystemSchedler')
        await self.channel_layer.group_discard(operator.erpsys_id, self.channel_name)
        self.close()

    async def send_staff_todo_list(self, event):
        new_data = event['data']
        await self.send(json.dumps(new_data))

class CustomerServicesListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        customer_id = self.scope['url_route']['kwargs']['customer_id']
        history_days = self.scope['url_route']['kwargs']['history_days']
        history_service_name = self.scope['url_route']['kwargs']['history_service_name']
        await self.channel_layer.group_add(f'customer_services_{customer_id}', self.channel_name)
        await self.accept()

        print('from CustomerServicesListConsumer:', self.scope['user'])
        # 初始化更新客户可选服务列表
        customer = await sync_to_async(Operator.objects.get)(id=customer_id)
        await sync_to_async(update_customer_services_list)(customer, history_days, history_service_name)

    async def disconnect(self, close_code):
        customer_id = self.scope['url_route']['kwargs']['customer_id']
        await self.channel_layer.group_discard(f'customer_services_{customer_id}', self.channel_name)
        self.close()

    async def send_customer_services_list(self, event):
        new_data = event['data']
        await self.send(json.dumps(new_data))
