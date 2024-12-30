import os
import sys
import django
import json
from io import StringIO
from django.core.management import call_command
from datetime import datetime

# 设置Django的环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erpsys.settings')
django.setup()

# 获取命令行参数
mode = sys.argv[1] if len(sys.argv) > 1 else ''

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
        'applications',
        'kernel.process',  # 开发阶段不备份Process，以避免恢复时触发生成PERIODIC TASKS，导致恢复失败
        'kernel.processcontextsnapshot'
    ]
)

# 将输出的字符串转换回JSON对象
data = json.loads(output.getvalue())

# 根据模式决定备份文件的名称和路径
if mode == 'crontab':
    backup_dir = os.path.join(os.path.dirname(__file__), 'backup_data')
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f'backup_{timestamp}.json')
else:
    backup_file = 'backup.json'

# 写入修改后的数据到文件
with open(backup_file, 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=4)
    
# 如果导出成功，打印成功提示、
print(f'数据导出成功！备份文件保存在：{backup_file}')