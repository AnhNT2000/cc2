from PyQt5.QtCore import QThread
from queue import Queue
import time
import numpy as np
import torch
import torch.nn.functional as f
from ..yolov5.models.common import DetectMultiBackend
from ..yolov5.utils.augmentations import letterbox, classify_transforms
from ..yolov5.utils.general import (check_img_size, non_max_suppression, scale_coords)
from ..yolov5.utils.torch_utils import select_device
from ..yolov5.trackers.ocsort.ocsort import OCSort
# from ..trackers_2.multi_tracker_zoo import create_tracker
import cv2
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # yolov5 strongsort root directory
WEIGHTS = ROOT / 'weights'

print(WEIGHTS)

palette = (2 ** 11 - 1, 2 ** 15 - 1, 2 ** 20 - 1)
def compute_color_for_labels(label):
    color = [int(int(p * (label ** 2 - label + 1)) % 255) for p in palette]
    return tuple(color)

def relu(x):
    return max(0, int(x))

class Tracking:
    def __init__(self):
        self.model_file = ''
        self.data = ''
        self.imgsz = 640
        self.conf_thres = 0.4
        self.iou_thres = 0.45
        self.max_det = 1000
        self.device = '0'
        self.classes = 0
        self.agnostic_nms = True
        self.half = True
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
        
    def setup_model(self,model, classes, conf_thres, img_size, device, data_):
        self.conf_thres = conf_thres
        self.device = device
        self.imgsz = img_size
        self.model_file = model
        self.classes = classes
        self.device = select_device(self.device)
        self.model = DetectMultiBackend(self.model_file, device=self.device, data=data_, fp16=self.half)
        self.model.eval()
        self.stride, self.names, self.pt = self.model.stride, self.model.names, self.model.pt
        self.imgsz = check_img_size(self.imgsz, s=self.stride)  # check image size
        if self.half:
            self.model.half()  # to FP16
        self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
        
    def preprocess_img(self, origin_img):
        img = letterbox(origin_img, new_shape=self.imgsz, stride=self.stride, auto=self.pt)[0]
        img = np.ascontiguousarray(img[:, :, ::-1].transpose(2, 0, 1))
        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        return img
    
    @torch.no_grad()
    def track(self, processed_img, origin_img):
        id_dict = {}
        pred = self.model(processed_img)
        pred = non_max_suppression(pred, 
                                   self.conf_thres, 
                                   self.iou_thres, 
                                   self.classes,
                                   self.agnostic_nms, 
                                   max_det=self.max_det)
        
        for det in pred:
            if det is None:
                continue
            
            if not len(det):
                continue
            
            det = det.detach().cpu()
            det[:, :4] = scale_coords(processed_img.shape[2:], det[:, :4], origin_img.shape).round()
            outputs = self._tracker.update(det, origin_img)
            if len(outputs):
                for j, output in enumerate(outputs):
                    x1, y1, x2, y2 = list(map(relu, output[0:4]))
                    ids = output[4]
                    cls = output[5]
                    id_dict[ids] = [x1, y1, x2, y2, cls]

        return id_dict
        