from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

import json

from kernel.models import Operator
from kernel.sys_lib import update_task_list, update_entity_task_group_list

# 个人任务列表
class PrivateTaskListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        operator = await sync_to_async(Operator.objects.get)(user=self.scope['user'])
        await self.channel_layer.group_add(operator.erpsys_id, self.channel_name)
        await self.accept()

        # 更新个人任务列表
        await sync_to_async(update_task_list)(operator, False)

    async def disconnect(self, close_code):
        operator = await sync_to_async(Operator.objects.get)(user=self.scope['user'])
        await self.channel_layer.group_discard(operator.erpsys_id, self.channel_name)
        self.close()

    async def send_private_task_list(self, event):
        new_data = event['data']
        await self.send(json.dumps(new_data))

# 公共任务列表
class PublicTaskListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('public_task_list', self.channel_name)
        await self.accept()

        # 更新公共任务列表
        operator = await sync_to_async(Operator.objects.get)(user=self.scope['user'])
        await sync_to_async(update_task_list)(operator, True)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('public_task_list', self.channel_name)
        self.close()

    async def send_public_task_list(self, event):
        new_data = event['data']
        await self.send(json.dumps(new_data))

# 实体任务列表
class EntityTaskListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        entity_id = self.scope['url_route']['kwargs']['entity_id']
        await self.channel_layer.group_add(f'{entity_id}', self.channel_name)
        await self.accept()
        # 初始化更新实体服务列表
        entity = await sync_to_async(Operator.objects.get)(erpsys_id=entity_id)
        await sync_to_async(update_entity_task_group_list)(entity)

    async def disconnect(self, close_code):
        entity_id = self.scope['url_route']['kwargs']['entity_id']
        await self.channel_layer.group_discard(f'{entity_id}', self.channel_name)
        self.close()

    async def send_task_list(self, event):
        new_data = event['data']
        await self.send(json.dumps(new_data))
