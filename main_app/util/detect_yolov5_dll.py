import cv2
import numpy as np

import time
from ctypes import *
import numpy.ctypeslib as npct
from ..config import MODEL_PATH_DLL_DETECT, MODEL_PATH_LIB_DETECT

class Detection:
    
    def __init__(self):
        super().__init__()
        self.max_bbox = 1000
        self.num_classes = 1
        self.conf = 0.5

    def setup_model(self, path_dll, path_lib, conf=0.5):
        self.yolov5 = CDLL(path_lib)

        self.yolov5.Detect.argtypes = [c_void_p, c_int, c_int,POINTER(c_ubyte),
                                     npct.ndpointer(dtype=np.float32, ndim=2, shape=(self.max_bbox, 6),
                                                    flags="C_CONTIGUOUS")]
        self.yolov5.Init.restype = c_void_p

        self.c_point = self.yolov5.Init(bytes(path_dll, encoding='utf-8'))

        self.conf = conf
        
    def is_in_polygon(self, box, polygon):
        x1, y1, x2, y2 = box
        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
        points = np.array(polygon, np.int32)
        points = points.reshape((-1, 1, 2))
        return cv2.pointPolygonTest(points, (center_x, center_y), False) >= 0
    
    def predict(self,img, polygon):
        list_people = []
        rows, cols = img.shape[0], img.shape[1]
        res_arr = np.zeros((self.max_bbox,6),dtype=np.float32)
        self.yolov5.Detect(self.c_point,c_int(rows), c_int(cols),img.ctypes.data_as(POINTER(c_ubyte)),res_arr)
        bbox_array = res_arr[~(res_arr==0).all(1)]
        for temp in bbox_array:
            cls = int(temp[4])
            if cls == 0:
                if self.is_in_polygon([int(temp[0]),int(temp[1]),int(temp[0]+temp[2]),int(temp[1]+temp[3])], polygon):
                    cv2.rectangle(img,(int(temp[0]),int(temp[1])),(int(temp[0]+temp[2]),int(temp[1]+temp[3])), (0, 255, 0), 2)
                    list_people.append(temp)
        return list_people



            
        

        
