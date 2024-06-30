from design.specification import GLOBAL_INITIAL_STATES

ScriptFileHeader = {
    'models_file_head': '''from django.db import models
from django.contrib.auth.models import User\n\n''',

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
