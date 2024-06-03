from django.contrib import admin
from .models import *


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Field._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    list_filter = ['field_type', 'related_dictionary', 'is_entity']
    autocomplete_fields = ['related_dictionary']

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

class FormListComponentsInline(admin.TabularInline):
    model = FormListComponents
    extra = 0
    autocomplete_fields = ['field']

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Form._meta.fields]
    list_display_links = ['label', 'name',]
    inlines = [FormComponentsInline, FormListComponentsInline]
    search_fields = ['label', 'name', 'pym']

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Resource._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name in ["definition",]:
    #         kwargs["queryset"] = Form.objects.filter(form_type="RESOURCE")
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # def get_form(self, request, obj=None, **kwargs):
    #     # 仅在编辑对象时运行
    #     request._obj_ = obj
    #     return super().get_form(request, obj, **kwargs)

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
    autocomplete_fields = ['form', 'work_order']

@admin.register(Vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Vocabulary._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
