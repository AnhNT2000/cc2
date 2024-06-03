from PyQt5.QtCore import QThread
from queue import Queue
import time
import numpy as np
import torch
from ...util.tracking_dll import Tracking
from ..object_person.tracking_object import Object_ID
from ..object_person.manager_tracking_object import ManagerTrackingObject
import cv2
from ...util.tools import is_in_polygon, polygon_to_points
from PyQt5.QtCore import pyqtSignal
from ...model.count_result import CountResult
from ...model.camera import Camera
from ...model.polygon import Polygon
from queue import Queue
from threading import Thread
from ...yolov5.setup import read_model_config_file
from ...config import TIME_SEND_TOTAL_COUNT
from ...model.time_acess import TimeAcess
from ...util.tool_time import get_max_time
from .api.check_time_has_changed import CheckTimeHasChanged
import datetime

palette = (2 ** 11 - 1, 2 ** 15 - 1, 2 ** 20 - 1)
def compute_color_for_labels(label):
    color = [int(int(p * (label ** 2 - label + 1)) % 255) for p in palette]
    return tuple(color)

class ThreadTracking(QThread):
    sig_num_person = pyqtSignal(int)
    sig_rs = pyqtSignal(CountResult)
    def __init__(self, in_buffer:Queue, camera:Camera):
        super().__init__()
        self.__camera = camera
        self.__in_buffer = in_buffer
        self.__thread_active = False
        self.list_id = []
        self.count = 0
        self.dict_result = {}
        self.frame = None

        self.__polygon_count = []
        self.__except_polygon = []
        self.__tracker = Tracking()
        self.__manager_tracking_object = ManagerTrackingObject(self.__camera)
        self.count = self.__manager_tracking_object._count
        self.old_time = time.time()
        self.__output_stream = Queue()
        self.__allow_time = True
        self.__old_time_check = time.time()


    @property
    def output_stream(self):
        return self.__output_stream
    
    def __setup_model(self):
        weights, classes, conf, imgsz, device, data, path_lib = read_model_config_file("count_all")
        self.__tracker.setup_model(weights, path_lib, conf)

    def convert_to_xy(self, polygon):
        x1 = min(polygon, key=lambda x: x[0])[0]
        y1 = min(polygon, key=lambda x: x[1])[1]
        x2 = max(polygon, key=lambda x: x[0])[0]
        y2 = max(polygon, key=lambda x: x[1])[1]
        return int(x1), int(y1), int(x2), int(y2)

    def check_bbox(self, bbox):
        x1, y1, x2, y2 = bbox
        if (x2-x1)/(y2-y1) >= 2 or (y2-y1)/(x2-x1) >= 2:
            return True

    def get_center_object(self, bbox):
        x1, y1, x2, y2 = bbox
        return (x1+x2)//2, (y1+y2)//2
    
    def get_center_polygon(self, polygon):
        x1, y1, x2, y2 = self.convert_to_xy(polygon)
        return (x1+x2)//2, (y1+y2)//2
    

    @torch.no_grad()
    def tracker(self, origin_img):
        id_dict = {}
        rs = self.__tracker.track(origin_img)
        W, H = origin_img.shape[1], origin_img.shape[0]
        self.__polygon_count, list_point = Polygon.convert_to_point_format(self.__camera.polygon.area_active, W, H)
        # print('polygon count', self.__polygon_count)
        for ids, bbox in rs.items():
            x1, y1, x2, y2, cls = bbox
            object_id = self.__manager_tracking_object.find_object(ids)
            if is_in_polygon([x1,y1,x2,y2], self.__polygon_count):
                if self.check_bbox([x1,y1,x2,y2]):
                    # print('check bbox')
                    continue
                center_obj = self.get_center_object([x1,y1,x2,y2])
                center_polygon = self.get_center_polygon(list_point)
                if object_id is None and center_obj[1] < center_polygon[1]-30:
                    object_id = Object_ID(ids)
                    object_id.update_time()
                    
                    self.__manager_tracking_object.add_object(object_id)
                if object_id is not None:
                    object_id.update_location([x1,y1,x2,y2])
                    object_id.update_center([x1,y1,x2,y2])
                    object_id.last_time_in_polygon = time.time()
                    object_id.time_direction = time.time()
                    id_dict[ids] = (x1, y1, x2, y2, cls)
                    self.draw_bbox(origin_img, id_dict)
        return origin_img
                    
            
    def draw_bbox(self, origin_img, id_dict):
        for id, bbox in id_dict.items():
            x1, y1, x2, y2, cls = bbox
            color = compute_color_for_labels(id)
            cv2.rectangle(origin_img, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(origin_img, f"{id}", (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 0.6, cv2.LINE_AA)

        
    def run(self):
        self.__thread_active = True
        self.__setup_model()
        while self.__thread_active:
            if not self.__in_buffer.empty():
                frame = self.__in_buffer.get()
                # if time.time() - self.__old_time_check > 10:
                #     self.__old_time_check = time.time()
                #     self.__allow_time = self.check_time_range()

                    # print('------------------------', self.__allow_time)
                # if self.__allow_time:
                frame = self.tracker(frame)
                count = self.__manager_tracking_object._count
                if time.time() - self.old_time > TIME_SEND_TOTAL_COUNT:
                    rs = CountResult()
                    rs.people_count = count
                    rs.device_id = self.__camera.id #add
                    rs.comp_id = self.__camera.id_company
                    rs.in_out = 1
                    rs.area_id = self.__camera.area_id
                    self.sig_rs.emit(rs)
                    self.old_time = time.time()
                cv2.putText(frame, f"Number Person: {count}", (600,50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 2, cv2.LINE_AA)
                cv2.polylines(frame, [self.__polygon_count], True, (0,0,255), 2)
                if self.__output_stream.qsize() < 10:
                    self.__output_stream.put(frame)
            self.msleep(5)

    def stop(self):
        self.__thread_active = False
            
