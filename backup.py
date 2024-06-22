import os
import django
import json
from io import StringIO
from django.core.management import call_command

# 设置Django的环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erpsys.settings')
django.setup()


# 准备一个字符串IO对象来捕获dumpdata的输出
output = StringIO()

# 执行数据导出到字符串
call_command(
    'dumpdata',
    stdout=output,
    indent=4,
    format='json',
    exclude=[
        'auth.permission',
        'sessions.session',
        'admin.logentry',
        'contenttypes',
        'maor',
    ]
)

# 将输出的字符串转换回JSON对象
data = json.loads(output.getvalue())


# 写入修改后的数据到文件
with open('backup.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=4)
    
# 如果导出成功，打印成功提示、
print('数据导出成功！')