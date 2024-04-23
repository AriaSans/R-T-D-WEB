import json
import os
from collections import defaultdict

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from django.views.decorators.csrf import csrf_exempt
from RTDweb.utils.BootstrapForm import BootstrapModelForm
from RTDweb.utils.select_option import SelectOption
from RTDweb.utils.img_list import ImgList
from RTDweb.utils.video_list import VideoList
from RTDweb.utils.pagination import Pagination
from RTDweb import models
from Real_Time_DetectWEB import settings
from RTDweb.utils.img_predict import ImgPredict

COCO_CLASSES = [
    "Person", "Bicycle", "Car", "Motorcycle", "Airplane", "Bus", "Train", "Truck", "Boat", "Traffic light",
    "Fire hydrant", "Stop sign", "Parking meter", "Bench", "Bird", "Cat", "Dog", "Horse", "Sheep", "Cow",
    "Elephant", "Bear", "Tiger", "Lion", "Wolf", "Fox", "Raccoon", "Skunk", "Monkey", "Ape", "Gorilla",
    "Chimpanzee", "Orangutan", "Bonobo", "Hand", "Foot", "Leg", "Ear", "Eye", "Nose", "Mouth", "Tooth",
    "Tongue", "Face", "Forehead", "Hair", "Lip", "Feature", "Eyebrow", "Eyelid", "Eye shadow", "Eyeliner",
    "Eyelash", "Tears", "Drop", "Skin", "Cheek", "Cheekbone", "Chin", "Neck", "Shoulder", "Arm", "Elbow",
    "Wrist", "Hand", "Finger", "Thumb", "Index finger", "Middle finger", "Ring finger", "Pinky", "Nail",
    "Thumbnail", "Palm", "Back", "Waist"
]


class DetectSetModelForm(BootstrapModelForm):
    class Meta:
        model = models.DetectSet
        fields = ['folder_name', 'type']


def yolo_main(request):
    user_info = request.session.get('info')
    if request.method == 'GET':
        new_set_form = DetectSetModelForm()
        select_obj_img = SelectOption(request, 1, user_info['uid'])
        select_obj_video = SelectOption(request, 2, user_info['uid'])
        select_obj_rt = SelectOption(request, 3, user_info['uid'])
        # 监测模型
        select_obj_models = models.VideoModel.objects.all()
        context = {
            'new_set_form': new_set_form,
            'user_info': user_info,
            'option_code_img': select_obj_img.html(),
            'option_code_video': select_obj_video.html(),
            'option_code_rt': select_obj_rt.html(),
            'select_obj_models': select_obj_models,
            'coco_classes_list': COCO_CLASSES,
        }
        return render(request, 'yolo_main.html', context)


@csrf_exempt
def yolo_set_add(request):
    form = DetectSetModelForm(data=request.POST)
    print(request.POST)
    if form.is_valid():
        to_user_id = request.POST.get('to_user_id')
        if models.DetectSet.objects.filter(folder_name=form.cleaned_data['folder_name'],
                                           to_user_id=to_user_id).exists():
            form.add_error('folder_name', '该集合已存在，请在上方选择或重新创建')
            return JsonResponse({'status': False, 'errors': form.errors})
        to_user = models.User.objects.get(pk=to_user_id)
        form.instance.to_user = to_user
        form.save()
        new_set_id = models.DetectSet.objects.filter(folder_name=form.cleaned_data['folder_name'],
                                                     to_user_id=to_user_id).first().id
        return JsonResponse({'status': True, 'new_set_id': new_set_id})

    return JsonResponse({'status': False, 'errors': form.errors})


def yolo_set_img(request, sid):
    detect_set = models.DetectSet.objects.get(pk=sid)
    img_list_code = ''
    if models.OriginImg.objects.filter(folder_name_id=sid).exists():
        origin_img_set_dict = models.OriginImg.objects.filter(folder_name_id=sid)
        img_list_code_obj = ImgList(request, origin_img_set_dict)
        img_list_code = img_list_code_obj.html()
    else:
        origin_img_set_dict = {}
    if request.method == 'GET':
        context = {
            'detect_set': detect_set,
            'origin_img_set_dict': origin_img_set_dict,
            'img_list_code': img_list_code,
        }
        return render(request, 'yolo_set_img.html', context)


def yolo_update_model(request, sid):
    wid = request.GET.get('wid')
    models.DetectSet.objects.filter(pk=sid).update(to_model_id=wid)
    return redirect('/yolo/set/' + str(sid) + '/video/')


@csrf_exempt
def yolo_upload_model(request, sid):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        # 保存文件到本地
        weight_path = os.path.join(settings.MEDIA_ROOT, 'weights', uploaded_file.name)
        with open(weight_path, mode='wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        # 上传服务器
        db_path = 'weights/' + uploaded_file.name
        models.VideoModel.objects.create(name=uploaded_file.name, video_weight=db_path)
        new_model = models.VideoModel.objects.filter(name=uploaded_file.name).first()

        return JsonResponse({'status': True, 'message': 'File uploaded successfully.',
                             'new_model_id': new_model.id, 'new_model_name': new_model.name})
    else:
        return JsonResponse({'status': False, 'error': 'No file uploaded.'})


def yolo_set_video(request, sid):
    detect_set = models.DetectSet.objects.get(pk=sid)
    model_name = detect_set.to_model
    video_list_code = ''
    if models.OriginVideo.objects.filter(folder_name_id=sid).exists():
        origin_video_set_dict = models.OriginVideo.objects.filter(folder_name_id=sid)
        video_list_code_obj = VideoList(request, origin_video_set_dict)
        video_list_code = video_list_code_obj.html()
    else:
        origin_video_set_dict = {}
    if request.method == 'GET':
        context = {
            'detect_set': detect_set,
            'origin_video_set_dict': origin_video_set_dict,
            'video_list_code': video_list_code,
            'coco_classes_list': COCO_CLASSES,
            'model_name': model_name
        }
        return render(request, 'yolo_set_video.html', context)


def yolo_set_realtime(request, sid):
    detect_set = models.DetectSet.objects.get(pk=sid)
    model_name = detect_set.to_model
    video_list_code = ''
    if models.OriginVideo.objects.filter(folder_name_id=sid).exists():
        origin_video_set_dict = models.OriginVideo.objects.filter(folder_name_id=sid)
        video_list_code_obj = VideoList(request, origin_video_set_dict)
        video_list_code = video_list_code_obj.html()
    else:
        origin_video_set_dict = {}
    if request.method == 'GET':
        context = {
            'detect_set': detect_set,
            'origin_video_set_dict': origin_video_set_dict,
            'video_list_code': video_list_code,
            'coco_classes_list': COCO_CLASSES,
            'model_name': model_name
        }
        return render(request, 'yolo_set_realtime.html', context)


def yolo_update_realtime_model(request, sid):
    wid = request.GET.get('wid')
    models.DetectSet.objects.filter(pk=sid).update(to_model_id=wid)

    return JsonResponse({'status': True})
