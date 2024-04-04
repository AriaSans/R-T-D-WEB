# Generated by Django 4.1 on 2024-04-04 09:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DetectSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folder_name', models.CharField(max_length=64, verbose_name='集合名')),
                ('type', models.SmallIntegerField(choices=[(1, 'img'), (2, 'video')], verbose_name='类别')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='用户名')),
                ('pwd', models.CharField(max_length=64, verbose_name='密码')),
            ],
        ),
        migrations.CreateModel(
            name='OriginImg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='图片名')),
                ('img_path', models.CharField(max_length=128, verbose_name='图片地址')),
                ('folder_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RTDweb.detectset', verbose_name='集合名')),
            ],
        ),
        migrations.AddField(
            model_name='detectset',
            name='to_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RTDweb.user', verbose_name='所属用户'),
        ),
    ]