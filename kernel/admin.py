from django.contrib import admin
from django.contrib.sessions.models import Session

from .models import *

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'session_data', 'expire_date']

@admin.register(ERPSysRegistry)
class ERPSysRegistryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ERPSysRegistry._meta.fields]
    list_display_links = ['id', 'label', 'name',]

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Organization._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Customer._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Role._meta.fields]
    list_display_links = ['id', 'label', 'name',]

@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Operator._meta.fields]
    list_display_links = ['id', 'label', 'name',]

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Resource._meta.fields]
    list_display_links = ['id', 'label', 'name',]

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Service._meta.fields]
    list_display_links = ['id', 'label', 'name',]

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Event._meta.fields]
    list_display_links = ['id', 'label', 'name',]

@admin.register(Instruction)
class InstructionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Instruction._meta.fields]
    list_display_links = ['id', 'label', 'name',]

@admin.register(ServiceRule)
class ServiceRuleAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ServiceRule._meta.fields]
    list_display_links = ['id', 'label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WorkOrder._meta.fields]
    list_display_links = ['id', 'label', 'name',]

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Process._meta.fields]
    list_display_links = ['pid', 'name', 'service',]
    search_fields = ['pid', 'name', 'service', 'state']
    list_filter = ['state', 'service']
    # autocomplete_fields = ['service']
    readonly_fields = ['created_time', 'updated_time']

@admin.register(Stacks)
class StacksAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Stacks._meta.fields]
    list_display_links = ['id', 'process',]
    search_fields = ['id', 'process']
    list_filter = ['process']
    readonly_fields = ['id', 'created_time', 'updated_time']

@admin.register(SysParams)
class SysParamsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SysParams._meta.fields]
    list_display_links = ['id', 'label', 'name',]
    search_fields = ['label', 'name', 'pym']
