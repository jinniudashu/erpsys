from design.specification import GLOBAL_INITIAL_STATES

ScriptFileHeader = {
    'models_file_head': f"""from django.db import models
from django.contrib.auth.models import User

from design.models import ERPSysBase
\n""",

    'Form_Reserved_body_script': """    config = models.JSONField(blank=True, null=True, verbose_name="配置")
""",

    'Service_Reserved_body_script': """    config = models.JSONField(blank=True, null=True, verbose_name="配置")
""",

    'admin_file_head': f"""from django.contrib import admin
from .models import *

class MaorSite(admin.AdminSite):
    site_header = '{GLOBAL_INITIAL_STATES['Organization']}'
    site_title = 'Maor'
    index_title = '工作台'
    enable_nav_sidebar = False
    index_template = 'admin/index_maor.html'
    site_url = None

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
        ]
        return my_urls + urls

    # 职员登录后的首页
    def index(self, request, extra_context=None):
        print('MaorSite index:', request.user, extra_context)
        # user = User.objects.get(username=request.user).customer
        return super().index(request, extra_context=extra_context)

maor_site = MaorSite(name = 'MaorSite')

# class ServiceAttributesInline(admin.TabularInline):
#     model = ServiceAttributes
#     extra = 0

# class ResourceDependencyInline(admin.TabularInline):
#     model = ResourceDependency
#     extra = 0

# class ServiceConsistsInline(admin.TabularInline):
#     model = ServiceConsists
#     fk_name = 'service'  # 指定使用的外键字段名
#     extra = 0
#     autocomplete_fields = ['service', 'sub_service']

# @admin.register(Service)
# class ServiceAdmin(admin.ModelAdmin):
#     list_display = ['label', 'name', 'form', 'subject', 'work_order', 'route_to', 'program', 'service_type', ]
#     list_display_links = ['label', 'name',]
#     inlines = [ServiceConsistsInline, ResourceDependencyInline, ServiceAttributesInline]
#     search_fields = ['label', 'name', 'pym']
#     autocomplete_fields = ['form', 'subject', 'work_order', 'route_to']

# class FormComponentsInline(admin.TabularInline):
#     model = FormComponents
#     extra = 0
#     autocomplete_fields = ['data_item']

# class FormComponentsConfigInline(admin.TabularInline):
#     model = FormComponentsConfig
#     extra = 0
#     autocomplete_fields = ['data_item']

# @admin.register(Form)
# class FormAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in Form._meta.fields]
#     list_display_links = ['label', 'name',]
#     inlines = [FormComponentsInline, FormComponentsConfigInline]
#     search_fields = ['label', 'name', 'pym']

# @admin.register(Event)
# class EventAdmin(admin.ModelAdmin):
#     list_display = ['id', 'label', 'name', 'pym', 'rule']
#     list_display_links = ['label', 'name',]
#     search_fields = ['label', 'name', 'pym']
\n\n""",

    'fields_type_head': '''app_types = ''',
}
