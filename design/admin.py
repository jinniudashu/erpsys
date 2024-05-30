from django.contrib import admin
from .models import *


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Field._meta.fields]
    list_display_links = ['label', 'name',]

class DictionaryFieldsInline(admin.TabularInline):
    model = DictionaryFields
    extra = 0

@admin.register(Dictionary)
class DictionaryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Dictionary._meta.fields]
    list_display_links = ['name',]
    inlines = [DictionaryFieldsInline]

class FormComponentsInline(admin.TabularInline):
    model = FormComponents
    extra = 0

class FormListComponentsInline(admin.TabularInline):
    model = FormListComponents
    extra = 0

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Form._meta.fields]
    list_display_links = ['name',]
    inlines = [FormComponentsInline, FormListComponentsInline]

@admin.register(ResourceObject)
class ResourceObjectAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ResourceObject._meta.fields]
    list_display_links = ['name',]

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

class ResourceObjectDependencyInline(admin.TabularInline):
    model = ResourceObjectDependency
    extra = 0

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Service._meta.fields]
    list_display_links = ['name',]
    inlines = [ServiceDependencyInline, ResourceObjectDependencyInline]

@admin.register(Vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Vocabulary._meta.fields]
    list_display_links = ['name',]

    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
