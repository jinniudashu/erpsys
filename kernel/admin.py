from django.contrib import admin

from .models import *

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Process._meta.fields]
    list_display_links = ['pid', 'service',]
    search_fields = ['pid', 'service', 'status']
    list_filter = ['status', 'service']
    autocomplete_fields = ['service', 'parent']
    date_hierarchy = 'created_time'
    readonly_fields = ['pid', 'created_time', 'updated_time']
    fieldsets = (
        (None, {
            'fields': ('pid', 'service', 'parent', 'status', 'schedule_context', 'control_context', 'program', 'pcb', 'stack', 'heap', 'pc', 'content_type', 'object_id', 'content_object', 'start_time', 'end_time', 'updated_time', 'created_time')
        }),
    )
