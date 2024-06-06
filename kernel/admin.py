from django.contrib import admin

from .models import *

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Process._meta.fields]
    list_display_links = ['pid', 'service',]
    search_fields = ['pid', 'service', 'state']
    list_filter = ['state', 'service']
    autocomplete_fields = ['service', 'parent']
    readonly_fields = ['pid', 'created_time', 'updated_time']
    fieldsets = (
        (None, {
            'fields': ('pid', 'service', 'parent', 'state', 'schedule_context', 'control_context', 'program', 'pcb', 'stack', 'heap', 'pc', 'content_type', 'object_id', 'start_time', 'end_time', 'updated_time', 'created_time')
        }),
    )
