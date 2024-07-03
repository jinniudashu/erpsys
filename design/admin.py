from django.contrib import admin

from .models import *
from .utils import generate_source_code

class DataItemConsistsInline(admin.TabularInline):
    model = DataItemConsists
    fk_name = 'data_item'  # 指定使用的外键字段名
    extra = 0
    autocomplete_fields = ['data_item', 'sub_data_item']

class DataItemTaxonomyInline(admin.TabularInline):
    model = DataItemTaxonomy
    fk_name = 'hypernymy'  # 指定使用的外键字段名
    extra = 0
    autocomplete_fields = ['hypernymy', 'hyponymy']

@admin.register(DataItem)
class DataItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'name', 'pym', 'field_type', 'business_type', 'inherit', 'bind_system_object', 'default_value', 'is_multivalued']
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    list_filter = ['field_type']
    inlines = [DataItemConsistsInline, DataItemTaxonomyInline]

class ServiceAttributesInline(admin.TabularInline):
    model = ServiceAttributes
    extra = 0

class ResourceDependencyInline(admin.TabularInline):
    model = ResourceDependency
    extra = 0

class ServiceConsistsInline(admin.TabularInline):
    model = ServiceConsists
    fk_name = 'service'  # 指定使用的外键字段名
    extra = 0
    autocomplete_fields = ['service', 'sub_service']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['label', 'name', 'form', 'subject', 'work_order', 'route_to', 'program', 'service_type', ]
    list_display_links = ['label', 'name',]
    inlines = [ServiceConsistsInline, ResourceDependencyInline, ServiceAttributesInline]
    search_fields = ['label', 'name', 'pym']
    autocomplete_fields = ['form', 'subject', 'work_order', 'route_to']

class FormComponentsInline(admin.TabularInline):
    model = FormComponents
    extra = 0
    autocomplete_fields = ['data_item']

class FormComponentsConfigInline(admin.TabularInline):
    model = FormComponentsConfig
    extra = 0
    autocomplete_fields = ['data_item']

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Form._meta.fields]
    list_display_links = ['label', 'name',]
    inlines = [FormComponentsInline, FormComponentsConfigInline]
    search_fields = ['label', 'name', 'pym']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'name', 'pym', 'rule']
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

# @admin.register(SystemInstruction)
# class SystemInstructionAdmin(admin.ModelAdmin):
#     list_display = ['id', 'label', 'name', 'pym', 'sys_call', 'parameters']
#     list_display_links = ['label', 'name',]
#     search_fields = ['label', 'name', 'pym']

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
    filter_horizontal = ['services',]
    change_form_template = 'project_changeform.html'

    def response_change(self, request, obj):
        # 生成源码
        if '_generate_source_code' in request.POST:
            generate_source_code(obj)
        return super().response_change(request, obj)
