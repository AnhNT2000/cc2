import time
from PyQt5 import QtCore
import cv2
from PIL import Image
import numpy as np

import time
from PIL import Image
from ...model.count_result import CountResult
from ...model.camera import Camera
from ...util.detect_yolov5_dll import Detection
from queue import Queue
from ctypes import *
from ...model.polygon import Polygon
from ...config import TIME_SENT_COUNT
from ...yolov5.setup import read_model_config_file

class ThreadInference(QtCore.QThread):
    
    sig_num_person = QtCore.pyqtSignal(str)
    sig_is_inference = QtCore.pyqtSignal()
    sig_graph = QtCore.pyqtSignal(list)
    sig_rs = QtCore.pyqtSignal(CountResult)
    
    def __init__(self, capture_queue:Queue,camera: Camera):
        super().__init__()
        self.__thread_active = False
        self.camera = camera
        self.capture_queue = capture_queue
        self.detect = Detection()
        self.__output_stream = Queue()
        self.old_time = time.time()
        
    @property
    def output_stream(self):
        return self.__output_stream
    
    def __setup_model(self):
        weights, classes, conf, imgsz, device, data, path_lib = read_model_config_file("count_polygon")
        self.detect.setup_model(weights, path_lib, conf)
    
    def run(self):
        print("ThreadInference: Start")
        self.__thread_active = True
        self.__setup_model()
        num_person = 0
        while self.__thread_active:
            if self.capture_queue.empty():
                self.msleep(1)
                continue
            frame= self.capture_queue.get()
            W, H = frame.shape[1], frame.shape[0]
            polygon, _ = Polygon.convert_to_point_format(self.camera.polygon.area_active, W, H)
            result = self.detect.predict(frame, polygon)
            num_person = len(result)
            if time.time() - self.old_time > TIME_SENT_COUNT:
                rs = CountResult()
                rs.people_count = num_person
                rs.device_id = self.camera.id
                rs.area_id = self.camera.area_id
                self.sig_rs.emit(rs)
                self.old_time = time.time()
            cv2.putText(frame, f"Num person: {num_person}", (600, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
            cv2.polylines(frame, np.array([polygon]), True, (0, 255, 0), 2)
            if self.__output_stream.qsize() < 10:
                self.__output_stream.put(frame)
            self.msleep(5)
    
    def stop(self):
        self.__thread_active = False



            
        

        
