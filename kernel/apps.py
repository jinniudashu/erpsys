from django.apps import AppConfig

class KernelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kernel'

    def ready(self):
        import kernel.scheduler
