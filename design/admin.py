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
    list_display = ['id', 'label', 'name', 'pym', 'field_type', 'business_type', 'sub_class', 'implement_type', 'dependency_order', 'affiliated_to', 'default_value', 'init_content', 'is_multivalued']
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    list_filter = ['field_type', 'implement_type', 'business_type']
    inlines = [DataItemConsistsInline]
    autocomplete_fields = ['business_type', 'affiliated_to']

@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Operator._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Organization._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Role._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    filter_horizontal = ['services']

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Resource._meta.fields]
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

@admin.register(Capital)
class CapitalAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Capital._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Knowledge)
class KnowledgeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Knowledge._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

class ServiceConsistsInline(admin.TabularInline):
    model = ServiceConsists
    extra = 0
    autocomplete_fields = ['sub_service']
    fk_name = 'service'

class MaterialRequirementsInline(admin.TabularInline):
    model = MaterialRequirements
    extra = 0

class EquipmentRequirementsInline(admin.TabularInline):
    model = EquipmentRequirements
    extra = 0

class DeviceRequirementsInline(admin.TabularInline):
    model = DeviceRequirements
    extra = 0

class CapitalRequirementsInline(admin.TabularInline):
    model = CapitalRequirements
    extra = 0

class KnowledgeRequirementsInline(admin.TabularInline):
    model = KnowledgeRequirements
    extra = 0

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Service._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    inlines = [ServiceConsistsInline, MaterialRequirementsInline, EquipmentRequirementsInline, DeviceRequirementsInline, CapitalRequirementsInline, KnowledgeRequirementsInline]
    autocomplete_fields = ['subject']
    filter_horizontal = ['reference']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Event._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Instruction)
class InstructionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Instruction._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

class ServiceRuleInline(admin.TabularInline):
    model = ServiceRule
    autocomplete_fields = ['event', 'service', 'operand_service']
    extra = 0

@admin.register(ServiceProgram)
class ServiceProgramAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ServiceProgram._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    inlines = [ServiceRuleInline]

@admin.register(ServiceRule)
class ServiceRuleAdmin(admin.ModelAdmin):
    list_display = ['service_program', 'order', 'label', 'service', 'event', 'system_instruction', 'operand_service', 'entity_content_type', 'entity_object_id', 'parameter_values', 'id']
    list_display_links = ['order', 'label']
    search_fields = ['label', 'name', 'pym']

class WorkOrderFieldsInline(admin.TabularInline):
    model = WorkOrderFields
    extra = 0

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WorkOrder._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    inlines = [WorkOrderFieldsInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # 当保存主表单时，遍历相关联的 WorkOrderField 数据
        fields = WorkOrderFields.objects.filter(work_order=obj)
        
        # 构建新的配置JSON
        config_data = []
        for field in fields:
            config_data.append({
                'label': field.label,
                'name': field.name,
                'value_expression': field.value_expression,
                'visible': field.visible,
                'order': field.order
            })

        # 将生成的JSON写入 config 字段
        obj.config = config_data
        obj.save()

class FormFieldsInline(admin.TabularInline):
    model = FormFields
    extra = 0

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Form._meta.fields]
    list_display_links = ['id', 'label', 'name',]
    search_fields = ['label', 'name', 'pym']
    inlines = [FormFieldsInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # 当保存主表单时，遍历相关联的 FormFields 数据
        fields = FormFields.objects.filter(form=obj)
        
        # 构建新的配置JSON
        config_data = []
        for field in fields:
            config_data.append({
                'label': field.field.label,
                'name': field.field.name,
                'expand_data_item': field.expand_data_item,
                'default_value': field.default_value,
                'readonly': field.readonly,
                'is_required': field.is_required,
                'choice_type': field.choice_type,
                'is_aggregate': field.is_aggregate,
                'visible': field.visible,
                'order': field.order
            })
        
        # 将生成的JSON写入 config 字段
        obj.config = config_data
        obj.save()

class ApiFieldsInline(admin.TabularInline):
    model = ApiFields
    extra = 0

@admin.register(Api)
class ApiAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Api._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    inlines = [ApiFieldsInline]

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'path', 'form']
    list_filter = ['parent']
    search_fields = ['name', 'path']

    def get_form(self, request, obj=None, **kwargs):
        form = super(MenuItemAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['parent'].queryset = MenuItem.objects.filter(parent__isnull=True)
        return form

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
