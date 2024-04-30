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


def get_ft(in_str):
    if in_str == 'true':
        return True
    else:
        return False


@csrf_exempt
def yolo_update_realtime_conf(request, sid):
    is_track = get_ft(request.POST.get('is_track'))
    is_line = get_ft(request.POST.get('is_line'))
    is_all = get_ft(request.POST.get('is_all'))
    camera_id = request.POST.get('camera_id')
    type_list = json.dumps(request.POST.getlist('type_list[]'))
    pt1_pt2 = json.dumps(request.POST.getlist('pt1_pt2[]'))
    rex = request.POST.get('resolution_x')
    rey = request.POST.get('resolution_y')
    new_conf_obj = models.CameraConf.objects.create(camera_id=camera_id, is_track=is_track, is_line=is_line,
                                                    is_all=is_all, resolution_x=rex, resolution_y=rey,
                                                    json_xyxy=pt1_pt2, json_type_list=type_list)
    models.DetectSet.objects.filter(pk=sid).update(to_camera_conf_id=new_conf_obj.pk)
    return JsonResponse({'status': True})

