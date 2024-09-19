from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from .models import Operator, Service

# 获取员工列表，过滤掉操作员自己，用于排班
def get_employees(request):
    # operator = User.objects.get(username=request.user).customer.staff
    # shift_employees = []
    # for staff in Operator.objects.filter(role__isnull=False).distinct().exclude(id=operator.id):
    #     allowed_services = [service.id for service in Service.objects.filter(service_type__in=[1,2]) if set(service.role.all()).intersection(set(staff.role.all()))]
    #     shift_employees.append({'id': staff.customer.id, 'name': staff.name, 'allowed_services': allowed_services})
    # return JsonResponse(shift_employees, safe=False)
    return JsonResponse([{'id': '1', 'name': 'test', 'allowed_services': []}], safe=False)
