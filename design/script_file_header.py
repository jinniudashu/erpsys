from design.specification import GLOBAL_INITIAL_STATES

ProjectName = 'Maor'

ScriptFileHeader = {
    'models_file_head': f"""from django.db import models
from django.contrib.auth.models import User
import uuid
import re
from pypinyin import Style, lazy_pinyin

from design.models import Service

class {ProjectName}Base(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    {ProjectName.lower()}_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.label)

    def save(self, *args, **kwargs):
        if self.{ProjectName.lower()}_id is None:
            self.{ProjectName.lower()}_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\u4e00-\u9fa5]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            # 使用正则表达式过滤掉label非汉字内容, 截取到8个汉字以内
            self.name = "_".join(lazy_pinyin(label[:8]))
            self.label = label
        super().save(*args, **kwargs)\n\n""",

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

maor_site = MaorSite(name = 'MaorSite')\n\n""",

    'fields_type_head': '''app_types = ''',
}
