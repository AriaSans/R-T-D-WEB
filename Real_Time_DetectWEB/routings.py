from django.urls import re_path

from RTDweb import consumers

websocket_urlpatterns = [
    re_path(r'ws/video/(?P<group>\w+)/$', consumers.VideoConsumer.as_asgi()),
]