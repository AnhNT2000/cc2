import time
from PyQt5 import QtCore
import cv2
import time
import numpy as np
from ...model.count_result import CountResult
from ...util.detect_yolov5 import Detection
from ...model.camera import Camera
from ...model.polygon import Polygon
from queue import Queue
from ...config import TIME_SENT_COUNT
from ...yolov5.setup import read_model_config_file

class ThreadInference(QtCore.QThread):
    
    sig_num_person = QtCore.pyqtSignal(str)
    sig_is_inference = QtCore.pyqtSignal()
    sig_graph = QtCore.pyqtSignal(list)
    sig_rs = QtCore.pyqtSignal(CountResult)
    
    def __init__(self, capture_queue:Queue, camera: Camera):
        super().__init__()
        self.__thread_active = False
        self.capture_queue = capture_queue
        self.frame = None
        self.__detection = Detection()
        self.camera = camera
        self._polygon = []
        self.__output_stream = Queue()
        self.old_time = time.time()
        
    @property
    def output_stream(self):
        return self.__output_stream

    def point_to_polygon(self, point):
        x1, y1, x2, y2 = point
        return [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
    
    def __setup_model(self):
        weights, classes, conf, imgsz, device, data, _ = read_model_config_file("count_polygon")
        self.__detection.setup_model(weights, classes, conf, imgsz, device, data)
    
    def drawText(self, img, text, x, y, w, h):
        # First we crop the sub-rect from the image
        sub_img = img[y:y+h, x:x+w]
        white_rect = np.full(sub_img.shape, 255, dtype=np.uint8)
        res = cv2.addWeighted(sub_img, 0.8, white_rect, 0.5, 1.0)

        # Putting the image back to its position
        img[y:y+h, x:x+w] = res
        cv2.putText(img, f"Person : {text}", (x+10, y+h-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0,0), 2, cv2.LINE_AA)
        return img
    
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
            self._polygon, _ = Polygon.convert_to_point_format(self.camera.polygon.area_active, W, H)
            result = self.__detection.detect(frame, self._polygon)
            num_person = len(result)
            if time.time() - self.old_time > TIME_SENT_COUNT:
                rs = CountResult()
                rs.people_count = num_person
                rs.device_id = self.camera.id
                rs.area_id = self.camera.area_id
                rs.comp_id = self.camera.id_company
                self.sig_num_person.emit(str(num_person))
                self.sig_rs.emit(rs)
                self.old_time = time.time()
            # cv2.putText(frame, f"Num person: {num_person}", (25, H - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (148, 100, 0), 2)
            frame = self.drawText(frame, num_person, 25, H - 70, 200, 70)
            cv2.polylines(frame, np.array([self._polygon]), True, (0, 255, 0), 2)
            if self.__output_stream.qsize() < 10:
                self.__output_stream.put(frame)
            self.msleep(1)
    
    def stop(self):
        self.__thread_active = False



            
        

        
