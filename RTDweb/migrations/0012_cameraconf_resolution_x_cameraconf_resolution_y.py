# Generated by Django 5.0.4 on 2024-04-26 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RTDweb', '0011_cameraconf_remove_detectset_camera_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cameraconf',
            name='resolution_x',
            field=models.IntegerField(default=0, verbose_name='分辨率x'),
        ),
        migrations.AddField(
            model_name='cameraconf',
            name='resolution_y',
            field=models.IntegerField(default=0, verbose_name='分辨率y'),
        ),
    ]