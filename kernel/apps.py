from django.apps import AppConfig

class KernelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kernel'

    def ready(self):
        import kernel.scheduler
        import kernel.models  # 添加这行以确保信号被注册
