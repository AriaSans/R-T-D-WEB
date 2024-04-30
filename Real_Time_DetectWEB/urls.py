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
from RTDweb.views import accout, yolo, yoloImg, yoloVideo, yoloRealTime

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}, name='media'),
    path('admin/', admin.site.urls),

    # 用户登录
    path('user/login/', accout.user_login),
    path('user/register/', accout.user_register),
    path('user/logout/', accout.user_logout),

    # 首页
    path('yolo/main/', yolo.yolo_main),
    # 集合添加
    path('yolo/set/add/', yolo.yolo_set_add),
# 集合添加
    path('yolo/set/<int:sid>/delete/', yolo.yolo_set_delete),
    # 图片集
    path('yolo/set/<int:sid>/img/', yolo.yolo_set_img),
    # 图片增加
    path('yolo/add/<int:sid>/img/', yoloImg.yolo_add_img),
    # 图片删除
    path('yolo/delete/img/', yoloImg.yolo_delete_img),
    # 图片监测
    path('yolo/detect/<int:sid>/img/', yoloImg.yolo_detect_img),
    # 图片预测集
    path('yolo/set/<int:sid>/img/predicted/', yoloImg.yolo_set_img_predicted),

    # 视频监测模型更新
    path('yolo/update/<int:sid>/model/', yolo.yolo_update_model),
    # 视频监测模型上传
    path('yolo/upload/<int:sid>/model/', yolo.yolo_upload_model),
    # 视频集
    path('yolo/set/<int:sid>/video/', yolo.yolo_set_video),
    # 视频增加
    path('yolo/add/<int:sid>/video/', yoloVideo.yolo_add_video),
    # 视频删除
    path('yolo/delete/video/', yoloVideo.yolo_delete_video),
    # 视频预测集
    path('yolo/set/<int:sid>/video/predicted/', yoloVideo.yolo_set_video_predicted),

    # 实时监测任务
    path('yolo/set/<int:sid>/realtime/', yolo.yolo_set_realtime),
    # 实时监测任务模型更新
    path('yolo/update/<int:sid>/realtime/model/', yolo.yolo_update_realtime_model),
    # 实时监测任务设置更新
    path('yolo/update/<int:sid>/realtime/conf/', yoloRealTime.yolo_update_realtime_conf),

]
