from django.db import models


# Create your models here.

class User(models.Model):
    name = models.CharField(verbose_name="用户名", max_length=32)
    pwd = models.CharField(verbose_name="密码", max_length=64)


class DetectSet(models.Model):
    type_choices = (
        (1, 'img'),
        (2, 'video'),
    )
    folder_name = models.CharField(verbose_name='集合名', max_length=64)
    type = models.SmallIntegerField(verbose_name='类别', choices=type_choices)
    to_user = models.ForeignKey(verbose_name='所属用户', to=User, on_delete=models.CASCADE)

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
