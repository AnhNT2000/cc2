from PyQt5.QtCore import QThread
from queue import Queue
import time
import numpy as np
from ..yolov5.trackers.ocsort.ocsort_v2 import OCSort
import cv2
from ..util.tools import is_in_polygon, polygon_to_points
from PyQt5.QtCore import pyqtSignal
from pathlib import Path
from ctypes import *
import numpy.ctypeslib as npct

def relu(x):
    return max(0, int(x))

class Tracking:
    def __init__(self):
        self.max_bbox = 50
        self._tracker = OCSort(
                                det_thresh=0.4,
                                iou_threshold=0.2,
                                use_byte=False
                            )
        # self._tracker = None
        self.polygon = None
        self.list_id = []
        self.count = 0
        self.dict_result = {}
        self.frame = None
        self.old_time = time.time()
        self.conf = 0.5

    def setup_model(self, path_dll,path_lib, conf):
        self.yolov5 = CDLL(path_lib)
        self.yolov5.Detect.argtypes = [c_void_p, c_int, c_int,POINTER(c_ubyte),
                                     npct.ndpointer(dtype=np.float32, ndim=2, shape=(self.max_bbox, 6),
                                                    flags="C_CONTIGUOUS")]
        self.yolov5.Init.restype = c_void_p
        self.c_point = self.yolov5.Init(bytes(path_dll, encoding='utf-8'))
        self.conf = conf
        
    def predict(self,img):
        rows, cols = img.shape[0], img.shape[1]
        res_arr = np.zeros((self.max_bbox,6),dtype=np.float32)
        self.yolov5.Detect(self.c_point,c_int(rows), c_int(cols),img.ctypes.data_as(POINTER(c_ubyte)),res_arr)
        self.bbox_array = res_arr[~(res_arr==0).all(1)]
        return self.bbox_array
    
    def track(self,origin_img):
        id_dict = {}
        pred = self.predict(origin_img)
        
        dets_to_sort = np.empty((0, 6))
        for temp in pred:
            bbox = [temp[0],temp[1],temp[0]+temp[2],temp[1]+temp[3]]  #xywh
            clas = int(temp[4])
            score = temp[5]
            dets_to_sort = np.vstack(
                (dets_to_sort, np.array([bbox[0], bbox[1], bbox[2], bbox[3], score, clas])))
        tracked_det = self._tracker.update(dets_to_sort, origin_img)
        if len(tracked_det):
            bbox_xyxy = tracked_det[:, :4]
            indentities = tracked_det[:, 4]
            categories = tracked_det[:, 5]
            for i in range(len(bbox_xyxy)):
                x1, y1, x2, y2 = list(map(lambda x: max(0, int(x)), bbox_xyxy[i]))
                id_ = int(indentities[i])
                id_dict[id_] = [x1, y1, x2, y2, int(categories[i])]
        return id_dict
        