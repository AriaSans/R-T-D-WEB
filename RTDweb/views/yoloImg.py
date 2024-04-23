import json
import os
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

def yolo_add_img(request, sid):
    file_set = request.FILES.getlist('file')
    # uid = str(request.session['info']['uid'])
    # set_name = request.POST.get('set_name')
    # folder_name = f'{uid}_{set_name}'
    folder_name = models.DetectSet.objects.get(pk=sid).get_user_folder_name()
    print(folder_name)
    folder_path = os.path.join(settings.MEDIA_ROOT, 'img_set', folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    for file_obj in file_set:
        db_file = os.path.join('img_set', folder_name, file_obj.name)
        db_path = db_file.replace('\\', '/')
        if not models.OriginImg.objects.filter(name=file_obj.name, folder_name_id=sid).exists():
            models.OriginImg.objects.create(name=file_obj.name, img_path=db_path, folder_name_id=sid)
            file_path = os.path.join(folder_path, file_obj.name)
            with open(file_path, 'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)
            f.close()

    return redirect('/yolo/set/' + str(sid) + '/img/')


@csrf_exempt
def yolo_delete_img(request):
    delete_id_list = request.POST.getlist('delete_list[]')
    for delete_id in delete_id_list:
        img_path = models.OriginImg.objects.filter(id=delete_id).first().img_path
        delete_path = os.path.join(settings.MEDIA_ROOT, img_path)
        if os.path.exists(delete_path):
            # 删除图片
            os.remove(delete_path)
            models.OriginImg.objects.filter(id=delete_id).delete()
            print(delete_path, '删除成功')
        else:
            return JsonResponse({'status': False})

    return JsonResponse({'status': True})


def yolo_detect_img(request, sid):
    img_predict = ImgPredict(sid)
    if img_predict.start_predict():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})


@csrf_exempt
def yolo_set_img_predicted(request, sid):
    all_pre = models.PredictedImg.objects.filter(folder_name_id=sid)
    # 获取查找的关键字列表，并查找到对应的原图列表输出到ori_query_set
    search_list = request.GET.getlist('type_list', [])
    print(search_list)
    if not search_list:
        ori_query_set = models.OriginImg.objects.filter(folder_name_id=sid)
    elif search_list == ['']:
        ori_query_set = models.OriginImg.objects.filter(folder_name_id=sid)
    else:
        search_list = [item.strip() for sublist in search_list for item in sublist.split(',')]
        search_id_list = []
        for obj in all_pre:
            obj_info_count = json.loads(obj.detect_info)['info_count']
            for index, k in enumerate(search_list):
                if k not in obj_info_count:
                    break
                if index + 1 == len(search_list):
                    search_id_list.append(obj.oring_img_id)
        ori_query_set = models.OriginImg.objects.filter(id__in=search_id_list)
    page_obj = Pagination(request, ori_query_set, 5, plus=2)
    queryset_list = page_obj.queryset_list
    ori_list = []
    info_count_list = []
    for i in range(5):
        if i >= len(queryset_list):
            obj = {'name': '0', 'img_path': '0'}
            ori_list.append(obj)
        else:
            obj = {'id': queryset_list[i].id, 'name': queryset_list[i].name, 'img_path': queryset_list[i].img_path,
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
                'info_count_list': {'name1': 0, 'name2': 0},
                'json_info_count_list': json_info_count_list,
                'json_info_list': json_info_list,
                'info_list': [{'name': '0', 'xyxy': '0'}],
            }
            predict_list.append(pre_data)
            continue
        pre_obj = models.PredictedImg.objects.filter(oring_img_id=ori['id']).first()
        info_dict = json.loads(pre_obj.detect_info)
        json_info_list = json.dumps(info_dict['info_list'])
        json_info_count_list = json.dumps(info_dict['info_count'])
        pre_data = {
            'id': pre_obj.id,
            'name': pre_obj.name,
            'img_path': pre_obj.img_path,
            'info_count_list': info_dict['info_count'],
            'json_info_count_list': json_info_count_list,
            'info_list': info_dict['info_list'],
            'json_info_list': json_info_list,
            'info_list_count': len(info_dict['info_list'])
        }
        predict_list.append(pre_data)

    # 获取监测总数据
    for obj in all_pre:
        info_count_one = json.loads(obj.detect_info)['info_count']
        info_count_list.append(info_count_one)
    result = defaultdict(int)
    for infoCount in info_count_list:
        for key, value in infoCount.items():
            if key in result:
                result[key] += value
            else:
                result[key] = value
    result_dict = dict(result)

    # 获取种类数和总监测数
    count_dict = [0, 0]
    for key, value in result_dict.items():
        count_dict[0] += 1
        count_dict[1] += value

    total_count_list = sorted(result_dict.items(), key=lambda x: x[1], reverse=True)
    json_total_count_dict = json.dumps(total_count_list)
    # 完成

    context = {
        'detect_set': detect_set,
        'ori_list': ori_list,
        'predict_list': predict_list,
        'page_code': page_obj.html(),
        'total_count_list': total_count_list,
        'json_total_count_dict': json_total_count_dict,
        'count_dict': count_dict,
    }
    return render(request, 'yolo_set_img_predicted.html', context)