import os

from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django import forms
from django.views.decorators.csrf import csrf_exempt
from RTDweb.utils.BootstrapForm import BootstrapModelForm
from RTDweb.utils.select_option import SelectOption
from RTDweb.utils.img_list import ImgList
from RTDweb import models
from Real_Time_DetectWEB import settings


class DetectSetModelForm(BootstrapModelForm):
    class Meta:
        model = models.DetectSet
        fields = ['folder_name', 'type']


def yolo_main(request):
    user_info = request.session.get('info')
    if request.method == 'GET':
        new_set_form = DetectSetModelForm()
        select_obj = SelectOption(request, 1, user_info['uid'])
        context = {
            'new_set_form': new_set_form,
            'user_info': user_info,
            'option_code': select_obj.html(),
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
        return JsonResponse({'status': True})

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


def yolo_add_img(request, sid):
    file_set = request.FILES.getlist('file')
    uid = str(request.session['info']['uid'])
    set_name = request.POST.get('set_name')
    folder_name = f'{uid}_{set_name}'
    folder_path = os.path.join(settings.MEDIA_ROOT, 'img_set', folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    for file_obj in file_set:
        db_file = os.path.join('/img_set', folder_name, file_obj.name)
        db_path = db_file.replace('\\', '/')
        if not models.OriginImg.objects.filter(name=file_obj.name, folder_name_id=sid).exists():
            models.OriginImg.objects.create(name=file_obj.name, img_path=db_path, folder_name_id=sid)
            file_path = os.path.join(folder_path, file_obj.name)
            with open(file_path, 'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)
            f.close()

    return redirect('/yolo/set/'+str(sid)+'/img/')

@csrf_exempt
def yolo_delete_img(request):
    delete_id_list = request.POST.getlist('delete_list[]')
    for delete_id in delete_id_list:
        img_path = models.OriginImg.objects.filter(id=delete_id).first().img_path
        # delete_path = os.path.join(settings.MEDIA_ROOT, img_path)
        if os.path.exists(delete_path):
            print(delete_path)
        # 删除图片
    return HttpResponse(status=204)