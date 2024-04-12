import json
import os

from PIL import Image
from RTDweb import models
from Real_Time_DetectWEB import settings
from ultralytics import YOLO


class ImgPredict(object):
    def __init__(self, set_id):
        print('开始监测初始化')
        # yolo参数
        self.coco_classes = [
            "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat", "traffic light",
            "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow",
            "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
            "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard",
            "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
            "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
            "potted plant", "bed", "dining table", "toilet", "TV", "laptop", "mouse", "remote", "keyboard",
            "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase",
            "scissors", "teddy bear", "hair drier", "toothbrush"
        ]  # coco数据集
        self.model = YOLO('yolov8s.pt')
        # 集合名
        self.set_id = set_id
        # 集合的文件地址
        set_obj = models.DetectSet.objects.filter(pk=self.set_id).first()
        self.folder_name = set_obj.get_user_folder_name()  # 图片的完整文件名
        self.predict_folder = os.path.join(settings.MEDIA_ROOT, 'img_set', self.folder_name, 'predicted')  # 预测集路径
        if not os.path.exists(self.predict_folder):
            os.makedirs(self.predict_folder)
        # 原图集化为字典数列[{id, 地址},{},...]
        self.ori_img_dict_list = []
        ori_img_obj_list = models.OriginImg.objects.filter(folder_name=self.set_id, is_detect=0)
        for obj in ori_img_obj_list:
            print(obj.id, obj.name, obj.img_path)
            self.ori_img_dict_list.append({'id': obj.id, 'name': obj.name, 'img_path': obj.img_path})
        print('监测初始化结束，开始监测')

    def start_predict(self):
        for ori_img_dict in self.ori_img_dict_list:
            print(ori_img_dict['id'], ori_img_dict['name'], ori_img_dict['img_path'])
            ori_id = ori_img_dict['id']
            name = ori_img_dict['name']
            orin_img_path = ori_img_dict['img_path']
            ori_source = os.path.join(settings.MEDIA_ROOT, orin_img_path)
            ori_source = ori_source.replace('\\', '/')
            print(ori_source)
            results = self.model(ori_source)
            for i, r in enumerate(results):
                # 保存预测图片
                im_bgr = r.plot()
                im_bgr = Image.fromarray(im_bgr[:, :, ::-1])
                predict_path = os.path.join(self.predict_folder, name)
                predict_path = predict_path.replace('\\', '/')
                r.save(filename=predict_path)
                # 保存到数据库
                xyxy = r.boxes.xyxy
                cls = r.boxes.cls
                print(cls)
                info_dict = {}
                info_list = []
                info_count = {}
                db_path = os.path.join('img_set', self.folder_name, 'predicted', name)
                db_path = db_path.replace('\\', '/')
                for num, cl in enumerate(cls):
                    info_temp = {}
                    xy_list = []
                    cls_name = self.coco_classes[int(cl)]
                    if cls_name in info_count:
                        info_count[cls_name] += 1
                    else:
                        info_count[cls_name] = 1
                    for j in range(4):
                        xy_list.append(int(xyxy[num][j]))
                    info_temp['name'] = cls_name
                    info_temp['xyxy'] = xy_list
                    info_list.append(info_temp)
                print(info_list)
                info_dict = {'info_count': info_count, 'info_list': info_list}
                creat_dict = {
                    'name': name,
                    'img_path': db_path,
                    'detect_info': json.dumps(info_dict),
                    'folder_name_id': self.set_id,
                    'oring_img_id': ori_id,
                }
                models.PredictedImg.objects.create(**creat_dict)
                models.OriginImg.objects.filter(id=ori_id).update(is_detect=1)

        return True
