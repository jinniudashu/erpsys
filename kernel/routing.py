from django.urls import path

from kernel.consumers import PrivateTaskListConsumer, PublicTaskListConsumer, EntityTaskListConsumer

ws_urlpatterns = [
    path('entity_task_list/<str:entity_id>/', EntityTaskListConsumer.as_asgi()),
    path('private_task_list/', PrivateTaskListConsumer.as_asgi()),
    path('public_task_list/', PublicTaskListConsumer.as_asgi()),
]