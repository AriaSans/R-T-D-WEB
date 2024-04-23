"""
ASGI config for Real_Time_DetectWEB project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from . import routings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Real_Time_DetectWEB.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),     # 自动找urls.py，找视图函数views.py  --> http
    "websocket": URLRouter(routings.websocket_urlpatterns)   # routing(urls) 、consumers (views)
})