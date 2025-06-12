import os
import subprocess
import sys
import threading
import time
from django.apps import AppConfig
from django.conf import settings


from django.apps import AppConfig
import subprocess, sys, os

class McpappConfig(AppConfig):
    name = 'mcp_servers'
    verbose_name = "MCP Servers"

    def ready(self):
        # 确保仅启动一次，避免多进程环境重复启动
        if os.environ.get('RUN_MAIN') != 'true':  # 防止Django运行两次 [oai_citation:3‡cloud.tencent.com](https://cloud.tencent.com/developer/ask/sof/112663333#:~:text=if%20os,MydjangoappConfig)
            # 构造启动命令，假设mcp_server.py位于项目根目录
            python_exe = sys.executable
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mcp_server.py')
            # 启动MCP Server子进程
            proc = subprocess.Popen([python_exe, script_path])
            # 可选：保存proc以便后续管理，如赋给AppConfig的属性

# class McpServersConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'mcp_servers'
#     verbose_name = 'MCP Servers'
    
#     def __init__(self, app_name, app_module):
#         super().__init__(app_name, app_module)
#         self.mcp_process = None
    
#     def ready(self):
#         """Django应用启动完成时调用"""
#         # 默认不自动启动MCP服务器，避免与StatReloader冲突
#         # 建议使用: python manage.py runserver_with_mcp
#         pass
    
#     def should_start_mcp_server(self):
#         """判断是否应该启动MCP服务器"""
#         # 检查环境变量，只有明确设置为true才启动
#         auto_start = os.environ.get('AUTO_START_MCP', 'false').lower() == 'true'
        
#         if not auto_start:
#             return False
            
#         # 检查命令行参数
#         argv = sys.argv
        
#         # 如果使用runserver_with_mcp命令，则不自动启动（避免冲突）
#         is_runserver_with_mcp = len(argv) >= 2 and 'runserver_with_mcp' in argv[1]
#         if is_runserver_with_mcp:
#             return False
        
#         # 只在普通runserver时启动
#         is_runserver = len(argv) >= 2 and 'runserver' in argv[1]
        
#         # 检查是否在开发环境
#         is_debug = getattr(settings, 'DEBUG', False)
        
#         return is_runserver and is_debug
    
#     def start_mcp_server(self):
#         """在后台启动MCP服务器 - 已禁用，使用runserver_with_mcp命令代替"""
#         print("💡 MCP自动启动已禁用。请使用: python manage.py runserver_with_mcp")
    
#     def stop_mcp_server(self):
#         """停止MCP服务器"""
#         if self.mcp_process:
#             try:
#                 self.mcp_process.terminate()
#                 self.mcp_process.wait(timeout=5)
#                 print("✅ MCP服务器已停止")
#             except subprocess.TimeoutExpired:
#                 self.mcp_process.kill()
#                 print("⚠️  强制终止MCP服务器")
#             except Exception as e:
#                 print(f"⚠️  停止MCP服务器时出错: {e}")
#             finally:
#                 self.mcp_process = None
