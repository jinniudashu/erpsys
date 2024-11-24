import os
import subprocess

def find_common_files(dir1, dir2):
    common_files = []
    for root, _, files in os.walk(dir1):
        for file in files:
            file_path1 = os.path.join(root, file)
            file_path2 = file_path1.replace(dir1, dir2, 1)  # 推导另一个项目的对应路径
            if os.path.exists(file_path2):
                common_files.append((file_path1, file_path2))
    return common_files

def compare_files(file_pairs):
    for file1, file2 in file_pairs:
        print(f"Comparing {file1} and {file2}...")
        subprocess.run(["git", "diff", "--no-index", file1, file2])

# 项目路径
project1_app_path = "/Users/miles/Documents/JiangNing/cxerp/src/cxerp"
project2_app_path = "/Users/miles/Documents/JiangNing/django-erp-os-framework/src/django-erp-os-framework"

# 找出同名文件
common_files = find_common_files(project1_app_path, project2_app_path)

# 比较同名文件
compare_files(common_files)