import os
import shutil
import django
from dotenv import load_dotenv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django-erp-os-framework.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

def create_superuser(username, email, password):
    # 创建管理员
    print("创建管理员")
    # 检查用户是否已经存在
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"Superuser {username} created successfully!")
        print('Username: %s' % username, 'Password: %s' % password)
    else:
        print(f"Superuser {username} already exists!")

# 从项目根目录获取所有app目录
app_dirs = [d for d in os.listdir() if os.path.isdir(d) and not d.startswith('.')]

for app_dir in app_dirs:
    migration_dir = os.path.join(app_dir, 'migrations')
    
    # 检查migrations目录是否存在
    if os.path.exists(migration_dir):
        # 遍历migrations目录中的所有文件和目录
        for item in os.listdir(migration_dir):
            item_path = os.path.join(migration_dir, item)
            
            # 如果item是文件且不是__init__.py，删除它
            if os.path.isfile(item_path) and item != "__init__.py":
                os.remove(item_path)
                print(f"Deleted: {item_path}")
            
            # 如果item是__pycache__目录，删除整个目录
            if os.path.isdir(item_path) and item == "__pycache__":
                shutil.rmtree(item_path)
                print(f"Deleted directory: {item_path}")
    else:
        print(f"No migrations directory found in {app_dir}.")

# 检查db.sqlite3文件是否存在
if os.path.exists("db.sqlite3"):
    os.remove("db.sqlite3")
    print(f"Deleted: db.sqlite3")
else:
    print("No db.sqlite3 found. Skipping deletion.")

# 生成migrations文件
print("生成migrations文件")
os.system("python manage.py makemigrations")
# 生成数据库
print("生成数据库")
os.system("python manage.py migrate")

# loaddata
print("初始化系统配置 loaddata")
os.system(f"python manage.py loaddata backup.json")

# 创建管理员
load_dotenv() 
create_superuser('admin', 'admin@example.com', os.getenv('DJANGO_ADMIN_PASSWORD'))
