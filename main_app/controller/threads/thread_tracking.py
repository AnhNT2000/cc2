from PyQt5.QtCore import QThread
from queue import Queue
import time
import numpy as np
import torch
from ...util.tracking import Tracking
from ..object_person.tracking_object import Object_ID, LocationObject
from ..object_person.manager_tracking_object import ManagerTrackingObject
import cv2
from ...util.tools import is_in_polygon, polygon_to_points
from PyQt5.QtCore import pyqtSignal
from datetime import datetime
from ...model.count_result import CountResult
from ...model.camera import Camera
from ...model.polygon import Polygon
from queue import Queue
from ...config import TIME_SEND_TOTAL_COUNT,EXCEPTION_CAMERA
from ...yolov5.setup import read_model_config_file

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
        self._new_polygon = []
        self.frame = None
        self.__tracker = Tracking()
        self.__manager_tracking_object = ManagerTrackingObject(self.__camera)

        self.old_time = time.time()
        self.__output_stream = Queue()
        
        self.__pre_count_in = 0
        self.__pre_count_out = 0

    @property
    def output_stream(self):
        return self.__output_stream
    
    def check_bbox(self, bbox):
        x1, y1, x2, y2 = bbox
        if (x2-x1)/(y2-y1) >= 2 or (y2-y1)/(x2-x1) >= 2:
            return True

    def get_center_object(self, bbox):
        x1, y1, x2, y2 = bbox
        return (x1+x2)//2, (y1+y2)//2
    
    def convert_to_xy(self, polygon):
        x1 = min(polygon, key=lambda x: x[0])[0]
        y1 = min(polygon, key=lambda x: x[1])[1]
        x2 = max(polygon, key=lambda x: x[0])[0]
        y2 = max(polygon, key=lambda x: x[1])[1]
        return int(x1), int(y1), int(x2), int(y2)
    
    def get_center_polygon(self, polygon):
        x1, y1, x2, y2 = self.convert_to_xy(polygon)
        return (x1+x2)//2, (y1+y2)//2
    
    def __setup_model(self):
        weights, classes, conf, imgsz, device, data, _ = read_model_config_file("count_all")
        self.__tracker.setup_model(weights, classes, conf, imgsz, device, data)

    @torch.no_grad()
    def tracker(self, origin_img):
        id_dict = {}
        processed_img = self.__tracker.preprocess_img(origin_img)
        rs = self.__tracker.track(processed_img, origin_img)
        W, H = origin_img.shape[1], origin_img.shape[0]
        self._new_polygon, list_point = Polygon.convert_to_point_format(self.__camera.polygon.area_active, W, H)
        for ids, bbox in rs.items():
            x1, y1, x2, y2, cls = bbox
            object_id = self.__manager_tracking_object.find_object(ids)
                
            if is_in_polygon([x1,y1,x2,y2], self._new_polygon):
                if self.check_bbox([x1,y1,x2,y2]):
                    continue
         
                if object_id is None:
                    object_id = Object_ID(ids)
                    object_id.update_time()
                    self.__manager_tracking_object.add_object(object_id)
                else:
                    object_id.update_location([x1,y1,x2,y2])
                    object_id.update_center([x1,y1,x2,y2])
                    object_id.last_time_in_polygon = time.time()
                    object_id.time_direction = time.time()
                    id_dict[ids] = (x1, y1, x2, y2, cls)
                    self.draw_bbox(origin_img, id_dict)
            else:
                if object_id is not None:
                   object_id.is_in_polygon = False
        return origin_img   
    
            
    def draw_bbox(self, origin_img, id_dict):
        for id, bbox in id_dict.items():
            x1, y1, x2, y2, cls = bbox
            color = compute_color_for_labels(id)
            cv2.rectangle(origin_img, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(origin_img, f"{id}", (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)

    def drawText(self, img, text_in, text_out, x, y, w, h):
        # First we crop the sub-rect from the image
        H, W = img.shape[:2]
        sub_img = img[y:y+h, x:x+w]
        white_rect = np.full(sub_img.shape, 255, dtype=np.uint8)
        res = cv2.addWeighted(sub_img, 1.0, white_rect, 1.0, 1.0)

        # Putting the image back to its position
        img[y:y+h, x:x+w] = res
        if int(H)==1080:
            cv2.putText(img, f"in  : {text_in}", (x+10, y+h-100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 3, cv2.LINE_AA)
            cv2.putText(img, f"out : {text_out}", (x+10, y+h-20), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 3, cv2.LINE_AA)
        else:
            cv2.putText(img, f"in  : {text_in}", (x+10, y+h-70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, cv2.LINE_AA)
            cv2.putText(img, f"out : {text_out}", (x+10, y+h-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)
        return img
        
    def run(self):
        self.__thread_active = True
        self.__setup_model()
        while self.__thread_active:
            if not self.__in_buffer.empty():
                frame = self.__in_buffer.get()
                image = self.tracker(frame)
                
                H, W = image.shape[:2]
                if EXCEPTION_CAMERA is not None:
                    if int(self.__camera.id) in EXCEPTION_CAMERA:
                        count_in = self.__manager_tracking_object._count_out
                        count_out = self.__manager_tracking_object._count_in
                    else:
                        count_in = self.__manager_tracking_object._count_in
                        count_out = self.__manager_tracking_object._count_out
                else:
                    count_in = self.__manager_tracking_object._count_in
                    count_out = self.__manager_tracking_object._count_out
                    
                if time.time() - self.old_time >= TIME_SEND_TOTAL_COUNT:
                    if (count_in != self.__pre_count_in) or (count_out != self.__pre_count_out):
                        rs = CountResult()
                        rs.people_count = count_in
                        rs.device_id = self.__camera.id #add
                        rs.comp_id = self.__camera.id_company
                        rs.in_out = 1
                        rs.area_id = self.__camera.area_id

                        rs_1 = CountResult()
                        rs_1.people_count = count_out
                        rs_1.device_id = self.__camera.id
                        rs_1.comp_id = self.__camera.id_company
                        rs_1.in_out = 2
                        rs_1.area_id = self.__camera.area_id
                        
                        self.sig_rs.emit(rs_1)
                        self.sig_rs.emit(rs)
                        self.__pre_count_out = count_out
                        self.__pre_count_in = count_in
                        self.old_time = time.time()
    
                #image = self.drawText(image, count_in, count_out, 0, H - 100, 200, 100)   #img, text_in, text_out, x, y, w, h
                image = self.drawText(image, count_in, count_out, 0, H - int(H/7), int(W/6), int(H/7))
                cv2.polylines(image, [polygon_to_points(self._new_polygon)], True, (0, 255, 0), 2)
                if self.__output_stream.qsize() < 10:
                    self.__output_stream.put(image)
            time.sleep(0.001)

    def stop(self):
        self.__thread_active = False
