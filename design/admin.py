from django.contrib import admin

from .models import *
from .utils import generate_source_code

class DataItemConsistsInline(admin.TabularInline):
    model = DataItemConsists
    fk_name = 'data_item'  # 指定使用的外键字段名
    extra = 0
    autocomplete_fields = ['data_item', 'sub_data_item']

@admin.register(DataItem)
class DataItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'name', 'pym', 'field_type', 'business_type', 'implement_type', 'dependency_order', 'bind_system_object', 'default_value', 'is_multivalued']
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    list_filter = ['field_type', 'implement_type', 'business_type']
    inlines = [DataItemConsistsInline]

@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Operator._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Material._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Equipment._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Device._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Space._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Capital)
class CapitalAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Capital._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'name', 'pym']
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'name', 'pym']
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

class FormComponentsConfigInline(admin.TabularInline):
    model = FormComponentsConfig
    extra = 0
    autocomplete_fields = ['data_item']

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Form._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    inlines = [FormComponentsConfigInline]

class ServiceConsistsInline(admin.TabularInline):
    model = ServiceConsists
    fk_name = 'service'
    extra = 0
    autocomplete_fields = ['service', 'sub_service']

class ResourceDependencyInline(admin.TabularInline):
    model = ResourceDependency
    extra = 0
    autocomplete_fields = ['service']

class ServiceAttributesInline(admin.TabularInline):
    model = ServiceAttributes
    extra = 0
    autocomplete_fields = ['attribute']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['label', 'name', 'form', 'subject', 'work_order', 'route_to', 'program', 'service_type', ]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    autocomplete_fields = ['form', 'subject', 'work_order', 'route_to']
    inlines = [ServiceConsistsInline, ResourceDependencyInline, ServiceAttributesInline]

class SourceCodeInline(admin.TabularInline):
    model = SourceCode
    extra = 0
    ordering = ['-create_time']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Project._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    inlines = [SourceCodeInline, ]
    # filter_horizontal = ['services',]
    change_form_template = 'project_changeform.html'

    def response_change(self, request, obj):
        # 生成源码
        if '_generate_source_code' in request.POST:
            generate_source_code(obj)
        return super().response_change(request, obj)
