import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import task_project.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            task_project.routing.websocket_urlpatterns
        )
    ),
})
