"""Real_Time_DetectWEB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from django.conf import settings
from RTDweb.views import accout, yolo




urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}, name='media'),
    path('admin/', admin.site.urls),

    # 用户登录
    path('user/login/', accout.user_login),
    path('user/register/', accout.user_register),

    # 首页
    path('yolo/main/', yolo.yolo_main),
    # 集合添加
    path('yolo/set/add/', yolo.yolo_set_add),
    # 图片集
    path('yolo/set/<int:sid>/img/', yolo.yolo_set_img),
    # 图片增加
    path('yolo/add/<int:sid>/img/', yolo.yolo_add_img),
    # 图片删除
    path('yolo/delete/img/', yolo.yolo_delete_img),
    # 图片监测
    path('yolo/detect/<int:sid>/img/', yolo.yolo_detect_img),
    # 图片预测集
    path('yolo/set/<int:sid>/img/predicted/', yolo.yolo_set_img_predicted)
]
