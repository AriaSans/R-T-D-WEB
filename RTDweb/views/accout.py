from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django import forms
from django.views.decorators.csrf import csrf_exempt
from RTDweb.utils.BootstrapForm import BootstrapModelForm
from RTDweb import models

from RTDweb.utils.encrypt import md5


class User(BootstrapModelForm):
    class Meta:
        model = models.User
        fields = '__all__'
        widgets = {'pwd': forms.PasswordInput()}

    def clean_pwd(self):
        md5_pwd = md5(self.cleaned_data['pwd'])
        print(md5_pwd)
        return md5_pwd

class MakeUser(BootstrapModelForm):
    re_pwd = forms.CharField(label='确认密码', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = models.User
        fields = ['name', 'pwd', 're_pwd']
        widgets = {'pwd': forms.PasswordInput()}

    def clean_pwd(self):
        md5_pwd = md5(self.cleaned_data['pwd'])
        print(md5_pwd)
        return md5_pwd

    def clean_re_pwd(self):
        re_pwd = md5(self.cleaned_data['re_pwd'])
        if re_pwd != self.cleaned_data['pwd']:
            raise ValidationError("密码不一致")
        return re_pwd


def user_login(request):
    """ 用户登录 """
    if request.method == "GET":
        form = User()
        return render(request, 'user_login.html', {'form': form})

    form = User(data=request.POST)
    print(request.POST)
    if form.is_valid():
        user_obj = models.User.objects.filter(**form.cleaned_data).first()
        if user_obj is not None:
            request.session['info'] = {'uid': user_obj.id, 'name': user_obj.name}
            return redirect('/yolo/main/')
        form.add_error('name', '用户名或密码错误')
    return render(request, 'user_login.html', {'form': form})


@csrf_exempt
def user_register(request):
    """ 用户注册 """
    if request.method == "GET":
        form = MakeUser()
        return render(request, 'user_register.html', {'form': form})

    print("postle")
    form = MakeUser(data=request.POST)
    if form.is_valid():
        if not models.User.objects.filter(name=request.POST.get('name')).exists():
            form.save()
            return JsonResponse({'status': True})
        form.add_error('name', '用户已存在')
    return JsonResponse({'status': False, 'errors': form.errors})


def user_logout(request):
    request.session.pop('info')
    return redirect('/user/login/')