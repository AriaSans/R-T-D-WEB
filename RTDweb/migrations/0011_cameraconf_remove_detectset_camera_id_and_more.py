# Generated by Django 5.0.4 on 2024-04-19 10:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RTDweb', '0010_detectset_camera_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='CameraConf',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('camera_id', models.SmallIntegerField(default=0, verbose_name='摄像头ID')),
                ('is_track', models.BooleanField(default=False, verbose_name='是否绘画轨迹')),
                ('is_line', models.BooleanField(default=False, verbose_name='是否绘画判定线')),
                ('is_all', models.BooleanField(default=False, verbose_name='是否检查全部')),
                ('json_type_list', models.JSONField(default=list, verbose_name='监测种类')),
                ('json_xyxy', models.JSONField(default=list, verbose_name='判定线端点坐标')),
            ],
        ),
        migrations.RemoveField(
            model_name='detectset',
            name='camera_id',
        ),
        migrations.AddField(
            model_name='detectset',
            name='to_camera_conf',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='RTDweb.cameraconf', verbose_name='摄像头设置'),
        ),
    ]