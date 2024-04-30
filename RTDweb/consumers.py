import base64
import json
import os
import random
from collections import defaultdict

import cv2
import numpy as np
import torch
from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from ultralytics import YOLO

from RTDweb import models
from RTDweb.views.yolo import COCO_CLASSES
from Real_Time_DetectWEB import settings

coco_classes = COCO_CLASSES


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Detections:
    # 监测信息集
    def __init__(self):
        self.detections = []

    def add(self, xyxy, confidence, class_id, tracker_id):
        self.detections.append((xyxy, confidence, class_id, tracker_id))


def line_direction(pt1, pt2, pt):
    # 获取pt点在pt1-pt2直线的哪一侧，返回1为一侧，-1为另一侧，0为在线上
    x1, y1 = pt1.x, pt1.y
    x2, y2 = pt2.x, pt2.y
    x, y = pt.x, pt.y
    return np.sign((x2 - x1) * (y - y1) - (y2 - y1) * (x - x1))


def detect_across_frame(detections: Detections, up_count, down_count, tracker_state, pre_tracker_state,
                        pt1, pt2):
    # 对穿线进行处理
    ## 0. 对每个物体进行处理
    for xyxy, _, _, tracker_id in detections.detections:
        ## 1. 获取监测数据
        x1, y1, x2, y2 = xyxy
        tracker_center = Point(x=(x1 + x2) / 2, y=(y1 + y2) / 2)
        tracker_state_new = line_direction(pt1, pt2, tracker_center) >= 0  # 返回True和False，代表哪一侧

        ## 2. 更新监测目标的当前信息:{'state': True/False, 'direction': 'up'/'down'/None}
        ### 如果是新目标或者当前目标是之前消失的目标
        if tracker_id not in tracker_state or tracker_state[tracker_id] is None:
            tracker_state[tracker_id] = {'state': tracker_state_new, 'direction': None}
            ### 如果在上一帧已存在这个目标 并且 上一帧这个目标信息不是为空 则继承信息
            if tracker_id in pre_tracker_state and pre_tracker_state[tracker_id] is not None:
                tracker_state[tracker_id]['direction'] = pre_tracker_state[tracker_id]['direction']

        ### 如果在线侧不变，则停止修改该监测数据，继续检查下一个
        elif tracker_state[tracker_id]['state'] == tracker_state_new:
            continue

        ### 如果在线侧改变，开始修改监测信息
        else:
            ### 如果物体原来在线上方，且新位置在线下方（从上往下）
            if tracker_state[tracker_id]['state'] and not tracker_state_new:
                ### 只有在之前的方向不是下的时候计数，防止重复计算
                if tracker_state[tracker_id]['direction'] != 'down':
                    down_count += 1
                tracker_state[tracker_id]['direction'] = 'down'

            ### 从下往上
            elif not tracker_state[tracker_id]['state'] and tracker_state_new:
                if tracker_state[tracker_id]['direction'] != 'up':
                    up_count += 1
                tracker_state[tracker_id]['direction'] = 'up'

            tracker_state[tracker_id]['state'] = tracker_state_new

    ## 3.保存已经消失的监测信息, 包括消失时的状态
    for tracker_id in list(tracker_state.keys()):
        if tracker_id not in [item[3] for item in detections.detections]:
            pre_tracker_state[tracker_id] = tracker_state[tracker_id]
            tracker_state[tracker_id] = None

    return up_count, down_count


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


class VideoConsumer(WebsocketConsumer):
    def websocket_connect(self, message):
        print('connected')
        # 有客户端来向后端发送websocket连接的请求时，自动触发
        # 服务端允许和客户端创建连接
        self.accept()

    def websocket_receive(self, message):
        # 浏览器基于websocket向后端发送数据，自动出发接收消息
        dict_data = json.loads(message['text'])
        print(dict_data)

        # 初始化数据
        ori_video_id = dict_data['video_id']
        ori_video_obj = models.OriginVideo.objects.filter(pk=ori_video_id).first()
        # 如果已监测直接跳出
        if ori_video_obj.is_detect == 1:
            self.send('100')
            return
        folder_name = ori_video_obj.folder_name.get_user_folder_name()
        result_folder = os.path.join(settings.MEDIA_ROOT, 'video_set', folder_name, 'predicted')
        if not os.path.exists(result_folder):
            os.makedirs(result_folder)
        # result_name = ori_video_obj.name + '.mp4'
        random_code = ''.join(random.choices('0123456789', k=8))
        result_name = folder_name + '-' + random_code + '.mp4'
        model_path = os.path.join(settings.MEDIA_ROOT, dict_data['model_path'])
        video_path = os.path.join(settings.MEDIA_ROOT, ori_video_obj.img_path)
        result_path = os.path.join(result_folder, result_name)
        detect_list_str = dict_data['sel_type_list']
        pt1_pt2 = dict_data['pt1_pt2']
        is_track = dict_data['IS_TRACK']
        is_line = dict_data['IS_LINE']
        is_all = dict_data['IS_ALL']
        if self.go_detect(model_path, video_path, result_path, detect_list_str, pt1_pt2, is_track, is_line, is_all):
            # 数据库操作
            db_file = os.path.join('video_set', folder_name, 'predicted', result_name)
            db_path = db_file.replace('\\', '/')
            if not models.PredictedVideo.objects.filter(name=result_name,
                                                        folder_name_id=ori_video_obj.folder_name_id).exists():
                models.PredictedVideo.objects.create(name=result_name, folder_name_id=ori_video_obj.folder_name_id,
                                                     oring_video_id=ori_video_obj.id, img_path=db_path)
                models.OriginVideo.objects.filter(id=ori_video_obj.id).update(is_detect=1)
                # 获取封面并保存
                cover_folder = os.path.join(result_folder, 'cover')
                if not os.path.exists(cover_folder):
                    os.makedirs(cover_folder)
                random_name = folder_name + '-' + random_code + '.jpg'
                cover_path = os.path.join(cover_folder, random_name)
                if save_first_frame_as_image(video_path, cover_path):
                    db_cover_path = os.path.join('video_set', folder_name, 'cover', random_name)
                    db_cover_path = db_cover_path.replace('\\', '/')
                    models.PredictedVideo.objects.filter(name=result_name,
                                                         folder_name_id=ori_video_obj.folder_name_id).update(
                        cover_img_path=db_cover_path)

        self.close()

    def websocket_disconnect(self, message):
        # 客户端与服务端断开连接时，自动触发
        print("disconnected")
        raise StopConsumer()

    def go_detect(self, model_path, video_path, result_path, detect_list_str, pt1_pt2, is_track=False, is_line=False,
                  is_all=False):
        model = YOLO(model_path)
        cap = cv2.VideoCapture(video_path)
        # Initialize video capture to get video properties
        if not cap.isOpened():
            print("Error opening video file.")
            return False
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()

        # 初始化数据
        if is_line:
            pt1_x = int(((int(pt1_pt2[0]) / 100) * width) // 1)
            pt1_y = int((((100 - int(pt1_pt2[1])) / 100) * height) // 1)
            pt2_x = int(((int(pt1_pt2[2]) / 100) * width) // 1)
            pt2_y = int((((100 - int(pt1_pt2[3])) / 100) * height) // 1)
            print(pt1_x, pt1_y, pt2_x, pt2_y)
            print(type(pt1_x))
            pt1 = Point(pt1_x, pt1_y)
            pt2 = Point(pt2_x, pt2_y)
            up_count, down_count = 0, 0
        if not is_all:
            is_detect_id = [coco_classes.index(x) for x in detect_list_str if x in coco_classes]
            print(is_detect_id)

        pre_tracker_state = {}  # 上一帧的监测对象状态
        track_history = defaultdict(lambda: [])
        tracker_state = {}  # 当前的

        # 开始监测
        cap = cv2.VideoCapture(video_path)

        # 保存文件
        videoWriter = None
        fps = int(cap.get(5))
        print('fps:', fps)

        # 获取视频的总帧数
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # 计算每10%进度的帧数范围
        frame_range = total_frames // 10

        while cap.isOpened():
            success, frame = cap.read()
            if success:
                # 获取当前帧数
                current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

                # 检查是否达到了下一个固定进度的帧数范围
                if current_frame % frame_range == 0:
                    # 计算当前进度
                    progress = current_frame / total_frames * 100
                    print(f'当前进度：{progress:.1f}%')
                    progress = f'{progress:.1f}'
                    self.send(progress)

                # 运行追踪监测
                device = 0 if torch.cuda.is_available() else 'cpu'
                if is_all:
                    results = model.track(frame, persist=True, tracker='bytetrack.yaml', device=device)
                else:
                    results = model.track(frame, persist=True, tracker='bytetrack.yaml', classes=is_detect_id,
                                          device=device)

                # 获取全部监测信息
                detections = Detections()
                boxes = results[0].boxes.xywh.cpu()
                xyxy = results[0].boxes.xyxy.cpu()
                track_ids = results[0].boxes.id.int().cpu().tolist()

                # 绘制监测框
                annotated_frame = results[0].plot(line_width=2, conf=False)

                for track_id, box, xy in zip(track_ids, boxes, xyxy):
                    x, y, w, h = box
                    track = track_history[track_id]
                    track.append((float(x), float(y)))  # x, y center point
                    if len(track) > 30:  # retain 90 tracks for 90 frames
                        track.pop(0)
                    # 存储当前帧监测信息
                    x1, y1, x2, y2 = xy
                    detections.add((x1, y1, x2, y2), None, None, track_id)

                    # 绘制跟踪线
                    if is_track:
                        points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                        cv2.polylines(annotated_frame, [points], isClosed=False, color=(248, 75, 228), thickness=2)

                # 监测触线
                if is_line:
                    # 画线
                    cv2.line(annotated_frame, (pt1.x, pt1.y), (pt2.x, pt2.y), (0, 0, 255), thickness=2)

                    up_count, down_count = detect_across_frame(detections, up_count, down_count, tracker_state,
                                                               pre_tracker_state, pt1, pt2)
                    print(up_count, down_count)
                    text_draw = 'DOWN: ' + str(up_count) + ' , UP: ' + str(down_count)
                    annotated_frame = cv2.putText(img=annotated_frame, text=text_draw, org=(10, 50),
                                                  fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                                  fontScale=0.75, color=(0, 0, 255), thickness=2)

                # 保存文件
                if videoWriter is None:
                    fourcc = cv2.VideoWriter_fourcc(*'H264')
                    videoWriter = cv2.VideoWriter(
                        result_path, fourcc, fps, (annotated_frame.shape[1], annotated_frame.shape[0]))
                videoWriter.write(annotated_frame)

            else:
                # 视频结束退出循环
                break

        # 释放内存
        self.send('100')
        cap.release()
        return True


class RealTimeConsumer(WebsocketConsumer):
    def websocket_connect(self, message):
        self.accept()

        self.sid = self.scope['url_route']['kwargs'].get("group")
        detect_set = models.DetectSet.objects.filter(pk=self.sid).first()
        camera_conf = models.CameraConf.objects.filter(id=detect_set.to_camera_conf_id).first()

        # 加载模型与初始化数据
        model_file = os.path.join(settings.MEDIA_ROOT, detect_set.to_model.video_weight)
        self.model = YOLO(model_file)
        self.pre_tracker_state = {}  # 上一帧的监测对象状态
        self.track_history = defaultdict(lambda: [])
        self.tracker_state = {}  # 当前的

        # 获取摄像头数据
        self.is_track = camera_conf.is_track
        self.is_line = camera_conf.is_line
        self.is_all = camera_conf.is_all
        width = camera_conf.resolution_x
        height = camera_conf.resolution_y

        if not self.is_all:
            type_list = json.loads(camera_conf.json_type_list)
            self.is_detect_id = [coco_classes.index(x) for x in type_list if x in coco_classes]
            print(self.is_detect_id)
        if self.is_line:
            pt1_pt2 = json.loads(camera_conf.json_xyxy)
            pt1_x = int(((int(pt1_pt2[0]) / 100) * width) // 1)
            pt1_y = int((((100 - int(pt1_pt2[1])) / 100) * height) // 1)
            pt2_x = int(((int(pt1_pt2[2]) / 100) * width) // 1)
            pt2_y = int((((100 - int(pt1_pt2[3])) / 100) * height) // 1)
            self.pt1 = Point(pt1_x, pt1_y)
            self.pt2 = Point(pt2_x, pt2_y)
            self.up_count, self.down_count = 0, 0



        print(self.pt1, type(self.pt1))
        print(self.is_all, type(self.is_all))

        self.floor_count = 0

    def websocket_disconnect(self, message):

        pass

    def websocket_receive(self, text_data=None, bytes_data=None):
        # 接收到的数据是图像数据的字符串形式
        image_data = text_data['text']

        # 将图像数据解码成 NumPy 数组
        image_data = image_data.split(",")[1]  # 去掉 data URL 前缀部分
        image_data = base64.b64decode(image_data)

        # 将图像数据解码成 NumPy 数组
        nparr = np.frombuffer(image_data, np.uint8)
        frame_data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # OpenCV 处理：实时监测返回结果画面
        processed_frame_data = self.real_time_detect(frame_data)

        # 发送处理后的图像数据回客户端
        self.send_video_stream(processed_frame_data)
        pass

    def send_video_stream(self, detected_frame):
        # 将帧数据编码为 JPEG 格式
        _, buffer2 = cv2.imencode('.jpg', detected_frame)

        # 直接发送图像数据的字节
        self.send(bytes_data=buffer2.tobytes())

    def process_frame(self, frame_data):
        # 在这里进行 OpenCV 图像处理操作，示例中仅将图像编码为 base64 字符串
        return base64.b64encode(frame_data).decode("utf-8")

    def real_time_detect(self, frame):
        # Run YOLOv8 tracking on the frame, persisting tracks between frames
        device = 0 if torch.cuda.is_available() else 'cpu'
        if self.is_all:
            results = self.model.track(frame, persist=True, tracker='bytetrack.yaml', device=device)
        else:
            results = self.model.track(frame, persist=True, tracker='bytetrack.yaml', classes=self.is_detect_id,
                                  device=device)

        # 获取全部监测信息
        detections = Detections()
        boxes = results[0].boxes.xywh.cpu()
        xyxy = results[0].boxes.xyxy.cpu()
        print(results[0].boxes.id)
        if not results[0].boxes.id is None:
            print("No box detected")
            track_ids = results[0].boxes.id.int().cpu().tolist()
            cls_ids = results[0].boxes.cls.int().cpu().tolist()
            detected_name = {}

            # 绘画监测框
            annotated_frame = results[0].plot(line_width=1, conf=False, font_size=10)
            # 绘制跟踪线
            for track_id, box, xy, cls_id in zip(track_ids, boxes, xyxy, cls_ids):
                x, y, w, h = box
                # 发送单个数据
                if track_id not in self.track_history:
                    track_info = json.dumps({'track_id': track_id, 'name': COCO_CLASSES[cls_id]})
                    self.send(text_data=track_info)

                # 保存本次数据
                if COCO_CLASSES[cls_id] in detected_name:
                    detected_name[COCO_CLASSES[cls_id]] += 1
                else:
                    detected_name[COCO_CLASSES[cls_id]] = 1

                track = self.track_history[track_id]
                track.append((float(x), float(y)))  # x, y center point
                if len(track) > 30:  # retain 90 tracks for 90 frames
                    track.pop(0)
                # 存储当前帧监测信息
                x1, y1, x2, y2 = xy
                detections.add((x1, y1, x2, y2), None, None, track_id)

                # 绘制跟踪线
                if self.is_track:
                    points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                    cv2.polylines(annotated_frame, [points], isClosed=False, color=(248, 75, 228), thickness=2)

            # 发送本次数据
            self.send(text_data=json.dumps(detected_name))

            # 监测触线
            if self.is_line:
                # 画线
                cv2.line(annotated_frame, (self.pt1.x, self.pt1.y), (self.pt2.x, self.pt2.y), (0, 0, 255), thickness=2)

                self.up_count, self.down_count = detect_across_frame(detections, self.up_count, self.down_count, self.tracker_state,
                                                           self.pre_tracker_state, self.pt1, self.pt2)
                print(self.up_count, self.down_count)
                text_draw = 'DOWN: ' + str(self.up_count) + ' , UP: ' + str(self.down_count)
                annotated_frame = cv2.putText(img=annotated_frame, text=text_draw, org=(10, 50),
                                              fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                              fontScale=0.75, color=(0, 0, 255), thickness=2)

        else:
            return frame
        return annotated_frame
