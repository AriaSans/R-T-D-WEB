# Generated by Django 4.1 on 2024-04-07 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RTDweb', '0002_alter_originimg_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='originimg',
            name='img_path',
            field=models.CharField(max_length=256, verbose_name='图片地址'),
        ),
    ]
