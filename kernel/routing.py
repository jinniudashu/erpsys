from django.urls import path, re_path

from kernel.consumers import TaskListConsumer, ServiceListConsumer

print('routing.....')
ws_urlpatterns = [
    path('ws/task_list/', TaskListConsumer.as_asgi()),
    path('ws/service_list/<int:customer_id>/<int:history_days>/<str:history_service_name>/', ServiceListConsumer.as_asgi()),
]