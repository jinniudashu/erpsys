from django.contrib import admin
from .models import Field, Form, FormComponents, FormListComponents

@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Field._meta.fields]
    list_display_links = ['name',]

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
