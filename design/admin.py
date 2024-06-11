from django.contrib import admin

from .models import *
from .utils import generate_source_code

@admin.action(description="刷新业务词汇表")
def refresh_vocabulary(modeladmin, request, queryset):
    modeladmin.model.objects.refresh()

@admin.register(Vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Vocabulary._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    actions = [refresh_vocabulary]

    def has_add_permission(self, request):
        return False
    
    # def has_delete_permission(self, request, obj=None):
    #     return False

@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Field._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    list_filter = ['field_type', 'is_entity']
    autocomplete_fields = ['self_vocab', 'related_dictionary']

class DictionaryFieldsInline(admin.TabularInline):
    model = DictionaryFields
    extra = 0
    autocomplete_fields = ['field']

@admin.register(Dictionary)
class DictionaryAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'name', 'pym', 'bind_system_object', 'erpsys_id', ]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    list_filter = ['bind_system_object']
    inlines = [DictionaryFieldsInline]

class FormComponentsInline(admin.TabularInline):
    model = FormComponents
    extra = 0
    autocomplete_fields = ['field']

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Form._meta.fields]
    list_display_links = ['label', 'name',]
    inlines = [FormComponentsInline, ]
    search_fields = ['label', 'name', 'pym']
    autocomplete_fields = ['self_vocab']

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Resource._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    autocomplete_fields = ['self_vocab']

class ServiceDependencyInline(admin.TabularInline):
    model = ServiceDependency
    fk_name = 'parent'  # 指定使用的外键字段名
    extra = 0

class ResourceDependencyInline(admin.TabularInline):
    model = ResourceDependency
    extra = 0

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Service._meta.fields]
    list_display_links = ['label', 'name',]
    inlines = [ServiceDependencyInline, ResourceDependencyInline]
    search_fields = ['label', 'name', 'pym']
    autocomplete_fields = ['self_vocab', 'form', 'work_order']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Project._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

    change_form_template = 'project_changeform.html'

    def response_change(self, request, obj):
        # 生成源码
        if '_generate_source_code' in request.POST:
            generate_source_code(obj)
        return super().response_change(request, obj)

@admin.register(SourceCode)
class SourceCodeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SourceCode._meta.fields]
    list_display_links = ['name', 'project',]
