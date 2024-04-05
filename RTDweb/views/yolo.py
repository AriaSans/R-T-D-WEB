from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django import forms
from django.views.decorators.csrf import csrf_exempt
from RTDweb.utils.BootstrapForm import BootstrapModelForm
from RTDweb.utils.select_option import SelectOption
from RTDweb import models



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
        if models.DetectSet.objects.filter(folder_name=form.cleaned_data['folder_name'], to_user_id=to_user_id).exists():
            form.add_error('folder_name', '该集合已存在，请在上方选择或重新创建')
            return JsonResponse({'status': False, 'errors': form.errors})
        to_user = models.User.objects.get(pk=to_user_id)
        form.instance.to_user = to_user
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'errors': form.errors})
