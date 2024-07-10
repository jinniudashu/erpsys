from design.specification import GLOBAL_INITIAL_STATES

ScriptFileHeader = {
    'models_file_head': f"""from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

import uuid
import re
from pypinyin import Style, lazy_pinyin

from kernel.models import Operator, Process, Service
\n""",

    'class_base_fields': f"""
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, related_name='%(class)s_attributes', null=True, blank=True, verbose_name="隶属主体")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="隶属id")
    content_object = GenericForeignKey('content_type', 'object_id')
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
""",

    'Profile_Reserved_body_script': """    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="人员")
""",

    'admin_file_head': f"""from django.contrib import admin
from .models import *

class ApplicationsSite(admin.AdminSite):
    site_header = '{GLOBAL_INITIAL_STATES['Organization']}'
    site_title = '颜青诊所'
    index_title = '工作台'
    enable_nav_sidebar = False
    index_template = 'admin/index_applications.html'
    site_url = None

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
        ]
        return my_urls + urls

    # 职员登录后的首页
    def index(self, request, extra_context=None):
        print('ApplicationsSite index:', request.user, extra_context)
        # user = User.objects.get(username=request.user).customer
        return super().index(request, extra_context=extra_context)

applications_site = ApplicationsSite(name = 'ApplicationsSite')
""",

    'fields_type_head': '''app_types = ''',
}

def get_model_footer(verbose_name):
    return f'''
    class Meta:
        verbose_name = "{verbose_name}"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w\u4e00-\u9fa5]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    '''

def get_admin_script(class_name):
    return f'''
@admin.register({class_name})
class {class_name}Admin(admin.ModelAdmin):
    list_display = [field.name for field in {class_name}._meta.fields]
    list_display_links = ['id']
applications_site.register({class_name}, {class_name}Admin)
'''