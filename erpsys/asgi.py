import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erpsys.settings')
django.setup()  # 添加这行，确保Django完全初始化

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from kernel.routing import ws_urlpatterns


# application = get_asgi_application()
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(URLRouter(ws_urlpatterns)),
})
