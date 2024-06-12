from django.contrib import admin

from .models import *
from .utils import generate_source_code

@admin.action(description="刷新业务语汇表")
def refresh_vocabulary(modeladmin, request, queryset):
    modeladmin.model.objects.refresh()

@admin.register(DataItem)
class DataItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'name', 'pym', 'field_type', 'related_dictionary']
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    list_filter = ['field_type', 'is_entity']
    autocomplete_fields = ['related_dictionary']

class DataItemDictDetailInline(admin.TabularInline):
    model = DataItemDictDetail
    extra = 0
    autocomplete_fields = ['data_item']

@admin.register(DataItemDict)
class DataItemDictAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'name', 'pym', 'system_resource_type', 'bind_system_object', 'erpsys_id', ]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    list_filter = ['bind_system_object']
    inlines = [DataItemDictDetailInline]

@admin.register(BusinessObject)
class BusinessObjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'name', 'pym', 'data_item']
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    autocomplete_fields = ['data_item']

class ServiceDependencyInline(admin.TabularInline):
    model = ServiceDependency
    fk_name = 'parent'  # 指定使用的外键字段名
    extra = 0

class ResourceDependencyInline(admin.TabularInline):
    model = ResourceDependency
    extra = 0

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['label', 'name', 'form', 'subject', 'work_order', 'route_to', 'program', 'service_type', 'estimated_time', 'estimated_cost',]
    list_display_links = ['label', 'name',]
    inlines = [ServiceDependencyInline, ResourceDependencyInline]
    search_fields = ['label', 'name', 'pym']
    autocomplete_fields = ['form', 'subject', 'work_order', 'route_to']

class FormComponentsInline(admin.TabularInline):
    model = FormComponents
    extra = 0
    autocomplete_fields = ['data_item']

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Form._meta.fields]
    list_display_links = ['label', 'name',]
    inlines = [FormComponentsInline, ]
    search_fields = ['label', 'name', 'pym']

class SourceCodeInline(admin.TabularInline):
    model = SourceCode
    extra = 0

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Project._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    inlines = [SourceCodeInline, ]
    change_form_template = 'project_changeform.html'

    def response_change(self, request, obj):
        # 生成源码
        if '_generate_source_code' in request.POST:
            generate_source_code(obj)
        return super().response_change(request, obj)
