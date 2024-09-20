ScriptFileHeader = {
    'models_file_head': f"""from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

import uuid
import re
from pypinyin import Style, lazy_pinyin

from kernel.models import Operator, Process, Service, Customer, Organization
\n""",

    'class_base_fields': f"""
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
""",

    'admin_file_head': f"""from django.contrib import admin
from django.contrib.auth.models import User
from django.urls import path

from .models import *
from .views import CustomTokenObtainPairView, CustomTokenRefreshView

def hide_fields(fields):
    exclude_fields = ['id', 'created_time', 'label', 'name', 'pym', 'erpsys_id', 'pid', 'updated_time']
    for field in exclude_fields:
        if field in fields:
            fields.remove(field)
    fields.extend(['created_time', 'id'])

admin.site.site_header = "..运营平台"
admin.site.site_title = ".."
admin.site.index_title = "工作台"

class ApplicationsSite(admin.AdminSite):
    site_header = '..运营平台'
    site_title = '..'
    index_title = '工作台'
    enable_nav_sidebar = False
    index_template = 'admin/index_applications.html'
    site_url = None

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
            path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
        ]
        return my_urls + urls

    # 职员登录后的首页
    def index(self, request, extra_context=None):
        # user = User.objects.get(username=request.user).customer
        return super().index(request, extra_context=extra_context)

applications_site = ApplicationsSite(name = 'ApplicationsSite')
""",

    'fields_type_head': '''app_types = ''',
}

def get_model_footer(verbose_name):
    return f"""
    class Meta:
        verbose_name = "{verbose_name}"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w\u4e00-\u9fa5]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    """

def get_master_field_script(data_item, master_class_name):
    return f"""    master = models.ForeignKey({master_class_name}, on_delete=models.SET_NULL, related_name='property_set_{data_item.name}', blank=True, null=True, verbose_name="{data_item.affiliated_to.label}")
"""

def get_admin_script(class_name, is_dict):
    if is_dict:
        hide_fields = ''
    else:
        hide_fields = f"""\n    hide_fields(list_display)"""

    return f"""
@admin.register({class_name})
class {class_name}Admin(admin.ModelAdmin):
    list_display = [field.name for field in {class_name}._meta.fields]{hide_fields}
    list_display_links = list_display
    list_filter = list_display
applications_site.register({class_name}, {class_name}Admin)
    """