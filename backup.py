import os
import django
from django.core.management import call_command

# 设置Django的环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erpsys.settings')
django.setup()

# 执行数据导出
with open('backup.json', 'w', encoding='utf-8') as file:
    call_command('dumpdata', stdout=file, indent=2, format='json', exclude=['auth.permission', 'admin.logentry', 'contenttypes'])

    # 如果导出成功，打印成功提示、
    print('数据导出成功！')
