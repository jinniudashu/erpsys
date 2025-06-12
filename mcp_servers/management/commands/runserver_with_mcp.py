"""
Django Management Command: 同时启动Django开发服务器和MCP服务器
"""

import os
import signal
import subprocess
import sys
import threading
import time
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = '同时启动Django开发服务器和MCP服务器'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mcp_process = None
        self.django_process = None
        
    def add_arguments(self, parser):
        parser.add_argument(
            '--port',
            type=int,
            default=8000,
            help='Django服务器端口 (默认: 8000)'
        )
        parser.add_argument(
            '--host',
            type=str,
            default='127.0.0.1',
            help='Django服务器主机 (默认: 127.0.0.1)'
        )
        parser.add_argument(
            '--no-mcp',
            action='store_true',
            help='只启动Django服务器，不启动MCP服务器'
        )
        
    def handle(self, *args, **options):
        self.stdout.write("🚀 启动Django + MCP服务器...")
        
        # 禁用应用自动启动MCP，避免冲突
        import os
        os.environ['AUTO_START_MCP'] = 'false'
        
        # 设置信号处理器
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            if not options['no_mcp']:
                # 启动MCP服务器
                self.start_mcp_server()
                
            # 启动Django服务器
            self.start_django_server(options)
            
        except KeyboardInterrupt:
            self.stdout.write("\n⏹️  收到中断信号，正在关闭服务器...")
        except Exception as e:
            self.stdout.write(f"❌ 启动失败: {e}")
        finally:
            self.cleanup()
    
    def start_mcp_server(self):
        """启动MCP服务器"""
        self.stdout.write("📡 启动MCP服务器...")
        
        try:
            # 构建MCP服务器启动命令 - 修复路径问题
            import os
            from django.conf import settings
            
            # 获取正确的manage.py路径
            if os.path.exists('manage.py'):
                # 当前目录就有manage.py (在src目录下运行)
                manage_py_path = 'manage.py'
            elif os.path.exists('src/manage.py'):
                # 在项目根目录运行
                manage_py_path = 'src/manage.py'
            else:
                # 使用绝对路径
                manage_py_path = os.path.join(settings.BASE_DIR, 'src', 'manage.py')
            
            # 创建MCP日志文件
            mcp_log_file = os.path.join(os.getcwd(), 'mcp_server_dev.log')
            
            # 设置完整的环境变量
            env = os.environ.copy()
            env.update({
                'DJANGO_SETTINGS_MODULE': 'erpsys.settings',
                'DJANGO_ENV': 'dev',
                'DEBUG': 'True',
                'WECHAT_APP_ID': env.get('WECHAT_APP_ID', 'default_app_id'),
                'WECHAT_APP_SECRET': env.get('WECHAT_APP_SECRET', 'default_app_secret'),
                'WECHAT_MCH_ID': env.get('WECHAT_MCH_ID', 'default_mch_id'),
                'WECHAT_MCH_KEY': env.get('WECHAT_MCH_KEY', 'default_mch_key'),
                'WECHAT_NOTIFY_URL': env.get('WECHAT_NOTIFY_URL', 'http://localhost:8000/wechat/notify/'),
                'DB_HOST': env.get('DB_HOST', 'localhost'),
                'DB_NAME': env.get('DB_NAME', 'erp_db'),
                'DB_USER': env.get('DB_USER', 'root'),
                'DB_PASS': env.get('DB_PASS', 'password'),
            })
            
            mcp_cmd = [
                sys.executable,
                manage_py_path,
                'run_mcp_server'
            ]
            
            # 启动MCP服务器进程，重定向输出到文件避免STDIO冲突
            with open(mcp_log_file, 'w') as log_file:
                self.mcp_process = subprocess.Popen(
                    mcp_cmd,
                    env=env,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    text=True,
                    preexec_fn=os.setsid if hasattr(os, 'setsid') else None
                )
            
            # 等待MCP服务器启动
            time.sleep(3)
            
            if self.mcp_process.poll() is None:
                self.stdout.write(f"✅ MCP服务器启动成功 (PID: {self.mcp_process.pid})")
                self.stdout.write(f"📋 MCP日志文件: {mcp_log_file}")
                
                # 在后台线程中监控MCP服务器状态
                def monitor_mcp():
                    while self.mcp_process and self.mcp_process.poll() is None:
                        time.sleep(5)
                    
                    if self.mcp_process and self.mcp_process.returncode != 0:
                        self.stdout.write(f"⚠️  MCP服务器异常退出 (退出码: {self.mcp_process.returncode})")
                        self.stdout.write(f"📋 查看日志: cat {mcp_log_file}")
                
                mcp_thread = threading.Thread(target=monitor_mcp, daemon=True)
                mcp_thread.start()
                
            else:
                # 读取日志文件获取错误信息
                try:
                    with open(mcp_log_file, 'r') as f:
                        error_output = f.read()
                except:
                    error_output = "无法读取错误日志"
                raise Exception(f"MCP服务器启动失败: {error_output}")
                
        except Exception as e:
            self.stdout.write(f"❌ MCP服务器启动失败: {e}")
            raise
    
    def start_django_server(self, options):
        """启动Django开发服务器"""
        self.stdout.write("🌐 启动Django开发服务器...")
        
        host = options['host']
        port = options['port']
        
        self.stdout.write(f"Django服务器将在 http://{host}:{port}/ 启动")
        
        # 直接调用Django的runserver命令
        call_command('runserver', f'{host}:{port}', verbosity=1)
    
    def signal_handler(self, signum, frame):
        """处理中断信号"""
        self.stdout.write(f"\n🛑 收到信号 {signum}，正在关闭服务器...")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """清理进程"""
        if self.mcp_process:
            self.stdout.write("⏹️  关闭MCP服务器...")
            try:
                if hasattr(os, 'killpg'):
                    # Unix系统，杀死整个进程组
                    os.killpg(os.getpgid(self.mcp_process.pid), signal.SIGTERM)
                else:
                    # Windows系统
                    self.mcp_process.terminate()
                    
                # 等待进程结束
                self.mcp_process.wait(timeout=5)
                self.stdout.write("✅ MCP服务器已关闭")
            except subprocess.TimeoutExpired:
                self.stdout.write("⚠️  强制终止MCP服务器...")
                if hasattr(os, 'killpg'):
                    os.killpg(os.getpgid(self.mcp_process.pid), signal.SIGKILL)
                else:
                    self.mcp_process.kill()
            except Exception as e:
                self.stdout.write(f"⚠️  关闭MCP服务器时出错: {e}")
        
        self.stdout.write("🏁 所有服务器已关闭") 