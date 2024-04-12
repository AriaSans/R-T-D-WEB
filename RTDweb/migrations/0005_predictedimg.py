# Generated by Django 4.1 on 2024-04-09 09:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('RTDweb', '0004_originimg_is_detect'),
    ]

    operations = [
        migrations.CreateModel(
            name='PredictedImg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='图片名')),
                ('img_path', models.CharField(max_length=256, verbose_name='图片地址')),
                ('detect_info', models.JSONField(verbose_name='监测信息')),
                ('folder_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RTDweb.detectset', verbose_name='集合名')),
                ('oring_img', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RTDweb.originimg', verbose_name='原图')),
            ],
        ),
    ]