from django.contrib import admin

from .models import *

@admin.register(ERPSysRegistry)
class ERPSysRegistryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ERPSysRegistry._meta.fields]
    list_display_links = ['id']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Role._meta.fields]
    list_display_links = ['id']

@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Operator._meta.fields]
    list_display_links = ['id']

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Resource._meta.fields]
    list_display_links = ['id']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Service._meta.fields]
    list_display_links = ['id']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Event._meta.fields]
    list_display_links = ['id']

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WorkOrder._meta.fields]
    list_display_links = ['id']

@admin.register(Instruction)
class SystemInstructionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'sys_call', 'parameters']
    list_display_links = ['id', 'name',]
    search_fields = ['name', 'pym']

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Process._meta.fields]
    list_display_links = ['pid', 'service',]
    search_fields = ['pid', 'service', 'state']
    list_filter = ['state', 'service']
    # autocomplete_fields = ['service', 'parent']
    readonly_fields = ['pid', 'created_time', 'updated_time']
    fieldsets = (
        (None, {
            'fields': ('pid', 'service', 'parent', 'state', 'schedule_context', 'control_context', 'program', 'pcb', 'stack', 'heap', 'pc', 'content_type', 'object_id', 'start_time', 'end_time', 'updated_time', 'created_time')
        }),
    )

@admin.register(Stacks)
class StacksAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Stacks._meta.fields]
    list_display_links = ['id', 'process',]
    search_fields = ['id', 'process']
    list_filter = ['process']
    readonly_fields = ['id', 'created_time', 'updated_time']
