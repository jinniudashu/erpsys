from django.urls import path, re_path

from kernel.consumers import UnassignedProcsConsumer, StaffTodoConsumer, CustomerServicesListConsumer

print('routing.....')
ws_urlpatterns = [
    path('ws/unassigned_procs/', UnassignedProcsConsumer.as_asgi()),
    path('ws/staff_todos_list/', StaffTodoConsumer.as_asgi()),
    path('ws/customer_services_list/<int:customer_id>/<int:history_days>/<str:history_service_name>/', CustomerServicesListConsumer.as_asgi()),
]