from django.db import models


# Create your models here.

class User(models.Model):
    name = models.CharField(verbose_name="用户名", max_length=32)
    pwd = models.CharField(verbose_name="密码", max_length=64)


class VideoModel(models.Model):
    name = models.CharField(verbose_name="模型名", max_length=64)
    video_weight = models.CharField(verbose_name='文件地址', max_length=128)

    def __str__(self):
        return self.name


class CameraConf(models.Model):
    camera_id = models.SmallIntegerField(verbose_name="摄像头ID", default=0)
    is_track = models.BooleanField(verbose_name="是否绘画轨迹", default=False)
    is_line = models.BooleanField(verbose_name="是否绘画判定线", default=False)
    is_all = models.BooleanField(verbose_name="是否检查全部", default=False)
    json_type_list = models.JSONField(verbose_name="监测种类", default=list)
    json_xyxy = models.JSONField(verbose_name="判定线端点坐标", default=list)


class DetectSet(models.Model):
    type_choices = (
        (1, 'img'),
        (2, 'video'),
        (3, 'camera'),
    )
    folder_name = models.CharField(verbose_name='集合名', max_length=64)
    type = models.SmallIntegerField(verbose_name='类别', choices=type_choices)
    to_user = models.ForeignKey(verbose_name='所属用户', to=User, on_delete=models.CASCADE)
    to_model = models.ForeignKey(verbose_name='视频模型', to=VideoModel, on_delete=models.CASCADE, null=True,
                                 blank=True)
    to_camera_conf = models.ForeignKey(verbose_name='摄像头设置', to=CameraConf, on_delete=models.CASCADE, null=True,
                                       blank=True)

    def get_user_folder_name(self):
        return f"{self.to_user.id}_{self.folder_name}"


class OriginImg(models.Model):
    is_detect_choices = (
        (0, '未监测'),
        (1, '已监测'),
    )
    name = models.CharField(verbose_name='图片名', max_length=128)
    folder_name = models.ForeignKey(verbose_name='集合名', to=DetectSet, on_delete=models.CASCADE)
    img_path = models.CharField(verbose_name='图片地址', max_length=256)
    is_detect = models.SmallIntegerField(verbose_name='是否监测', choices=is_detect_choices, default=0)


class PredictedImg(models.Model):
    name = models.CharField(verbose_name='图片名', max_length=128)
    folder_name = models.ForeignKey(verbose_name='集合名', to=DetectSet, on_delete=models.CASCADE)
    img_path = models.CharField(verbose_name='图片地址', max_length=256)
    oring_img = models.ForeignKey(verbose_name='原图', to=OriginImg, on_delete=models.CASCADE)
    detect_info = models.JSONField(verbose_name='监测信息')


class OriginVideo(models.Model):
    is_detect_choices = (
        (0, '未监测'),
        (1, '已监测'),
    )
    name = models.CharField(verbose_name='视频名', max_length=128)
    folder_name = models.ForeignKey(verbose_name='集合名', to=DetectSet, on_delete=models.CASCADE)
    img_path = models.CharField(verbose_name='图片地址', max_length=256)
    cover_img_path = models.CharField(verbose_name='封面地址', max_length=256, null=True, blank=True)
    is_detect = models.SmallIntegerField(verbose_name='是否监测', choices=is_detect_choices, default=0)


class PredictedVideo(models.Model):
    name = models.CharField(verbose_name='视频名', max_length=128)
    folder_name = models.ForeignKey(verbose_name='集合名', to=DetectSet, on_delete=models.CASCADE)
    img_path = models.CharField(verbose_name='视频地址', max_length=256)
    cover_img_path = models.CharField(verbose_name='封面地址', max_length=256, null=True, blank=True)
    oring_video = models.ForeignKey(verbose_name='原视频', to=OriginVideo, on_delete=models.CASCADE)
