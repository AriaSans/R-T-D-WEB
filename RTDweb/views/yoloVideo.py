import json
import os
import cv2
import random
from collections import defaultdict
from functools import reduce

from django.core.exceptions import ValidationError
from django.db.models import Count, Sum, Value, Q
from django.db.models.expressions import RawSQL
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django import forms
from django.views.decorators.csrf import csrf_exempt
from RTDweb.utils.BootstrapForm import BootstrapModelForm
from RTDweb.utils.select_option import SelectOption
from RTDweb.utils.img_list import ImgList
from RTDweb.utils.pagination import Pagination
from RTDweb import models
from Real_Time_DetectWEB import settings
from RTDweb.utils.img_predict import ImgPredict


# 保存第一帧为封面
def save_first_frame_as_image(video_path, output_path):
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file.")
        return False

    # 读取第一帧
    ret, frame = cap.read()
    if not ret:
        print("Error reading first frame.")
        return False

    # 保存第一帧为图像文件
    cv2.imwrite(output_path, frame)

    # 释放视频捕获对象
    cap.release()
    return True


def yolo_add_video(request, sid):
    file_set = request.FILES.getlist('file')
    folder_name = models.DetectSet.objects.get(pk=sid).get_user_folder_name()
    folder_path = os.path.join(settings.MEDIA_ROOT, 'video_set', folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    for file_obj in file_set:
        # 保存数据库
        db_file = os.path.join('video_set', folder_name, file_obj.name)
        db_path = db_file.replace('\\', '/')
        if not models.OriginVideo.objects.filter(name=file_obj.name, folder_name_id=sid).exists():
            models.OriginVideo.objects.create(name=file_obj.name, img_path=db_path, folder_name_id=sid)
            # 保存本地
            file_path = os.path.join(folder_path, file_obj.name)
            with open(file_path, 'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)
            f.close()
            # 获取封面
            cover_folder = os.path.join(folder_path, 'cover')
            if not os.path.exists(cover_folder):
                os.makedirs(cover_folder)
            random_name = ''.join(random.choices('0123456789', k=8)) + '.jpg'
            cover_path = os.path.join(cover_folder, random_name)
            if save_first_frame_as_image(file_path, cover_path):
                db_cover_path = os.path.join('video_set', folder_name, 'cover', random_name)
                db_cover_path = db_cover_path.replace('\\', '/')
                models.OriginVideo.objects.filter(name=file_obj.name, folder_name_id=sid).update(
                    cover_img_path=db_cover_path)

    return redirect('/yolo/set/' + str(sid) + '/video/')


@csrf_exempt
def yolo_delete_video(request):
    delete_id_list = request.POST.getlist('delete_list[]')
    for delete_id in delete_id_list:
        video_obj = models.OriginVideo.objects.filter(id=delete_id).first()
        video_path = video_obj.img_path
        cover_path = video_obj.cover_img_path
        delete_video_path = os.path.join(settings.MEDIA_ROOT, video_path)
        delete_cover_path = os.path.join(settings.MEDIA_ROOT, cover_path)
        if os.path.exists(delete_video_path):
            # 删除视频
            os.remove(delete_video_path)
            os.remove(delete_cover_path)
            models.OriginVideo.objects.filter(id=delete_id).delete()
            print(delete_video_path, delete_cover_path, '删除成功')
        else:
            return JsonResponse({'status': False})

    return JsonResponse({'status': True})


def yolo_set_video_predicted(request, sid):
    all_pre = models.PredictedVideo.objects.filter(folder_name_id=sid)
    ori_query_set = models.OriginVideo.objects.filter(folder_name_id=sid, is_detect=1)
    page_obj = Pagination(request, ori_query_set, 5, plus=2)
    queryset_list = page_obj.queryset_list
    ori_list = []
    for i in range(5):
        if i >= len(queryset_list):
            obj = {'name': '0', 'img_path': '0'}
            ori_list.append(obj)
        else:
            obj = {'id': queryset_list[i].id, 'name': queryset_list[i].name, 'img_path': queryset_list[i].img_path,
                   'cover_img_path': queryset_list[i].cover_img_path,
                   'folder_name_id': queryset_list[i].folder_name_id, 'is_detect': queryset_list[i].is_detect}
            ori_list.append(obj)
    print(ori_list)
    detect_set = models.DetectSet.objects.filter(pk=sid).first()
    predict_list = []
    for ori in ori_list:
        if ori['name'] == '0':
            json_info_list = json.dumps([{'name': '0', 'img_path': '0'}])
            json_info_count_list = json.dumps({'name1': 0, 'name2': 0})
            pre_data = {
                'id': 0,
                'name': '0',
                'img_path': '0',
                'cover_img_path': '0',
            }
            predict_list.append(pre_data)
            continue
        pre_obj = models.PredictedVideo.objects.filter(oring_video_id=ori['id']).first()
        pre_data = {
            'id': pre_obj.id,
            'name': pre_obj.name,
            'img_path': pre_obj.img_path,
            'cover_img_path': pre_obj.cover_img_path,
        }
        predict_list.append(pre_data)
    print(predict_list)

    # 完成

    context = {
        'detect_set': detect_set,
        'ori_list': ori_list,
        'predict_list': predict_list,
        'page_code': page_obj.html(),
    }
    return render(request, 'yolo_set_video_predicted.html', context)
