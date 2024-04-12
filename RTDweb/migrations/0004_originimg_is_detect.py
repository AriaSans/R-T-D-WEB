# Generated by Django 4.1 on 2024-04-08 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RTDweb', '0003_alter_originimg_img_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='originimg',
            name='is_detect',
            field=models.SmallIntegerField(choices=[(0, '未监测'), (1, '已监测')], default=0, verbose_name='是否监测'),
        ),
    ]