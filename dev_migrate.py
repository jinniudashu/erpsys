import os

# 生成migrations文件
print("生成migrations文件")
os.system("python manage.py makemigrations")
# 生成数据库
print("生成数据库")
os.system("python manage.py migrate")
# 备份数据
print("备份数据")
os.system("python backup.py")
# 初始化项目
print("初始化项目")
os.system("python dev_initial.py")