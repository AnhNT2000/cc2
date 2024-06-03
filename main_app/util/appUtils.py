import cv2
from PyQt5.QtCore import Qt
# from PyQt5.QtGui import QPixmap
# from PyQt5.QtWidgets import QLabel
# from PyQt5 import QtGui
import torchvision
import time
import torch
import base64
import cv2
import numpy as np
import json
import yaml
import os
from logging import Logger
import logging
from sympy import isprime
import os
from .file_utils import create_folder_on_another_computer



def get_logger(file_name, mode="w", name_logger='urbanGUI') -> Logger:
    create_folder_on_another_computer(os.path.dirname(file_name))
    if not os.path.exists(file_name):
        open(file_name, 'x').close()
    logging.basicConfig(filename=file_name,
                        filemode=mode,
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    fh = logging.FileHandler(file_name)
    fh.setLevel(logging.DEBUG)
    logger = logging.getLogger(name_logger)
    if (logger.hasHandlers()):
        logger.handlers.clear()
    logger.addHandler(fh)
    return logger


def is_in_polygon(box, polygon):
    x1, y1, x2, y2, _, _ = box
    center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
    return cv2.pointPolygonTest(polygon, (center_x, center_y), False) >= 0


def draw_transparent(image, polygon, alpha=0.5, color=(255, 0, 0)):
    """
    Draw a transparent polygon on the given image.
    :param image: image to draw on
    :param polygon: list of points. Ex: [(0, 0), (0, 100), (100, 100), (100, 0)]
    :param alpha: transparency level
    :param color: color of the polygon

    :return: image with polygon drawn
    """
    image_copy = image.copy()
    new_image = cv2.fillPoly(image, [np.array(polygon)], color)
    image_copy = cv2.addWeighted(image_copy, 1 - alpha, new_image, alpha, 0)
    return image_copy


def concate_image(images):
    bbox_locate_list = []
    bbox_dict = {"x": "", "y": "", "width": "", "height": ""}
    max_width = sorted(images, key=lambda x: x.shape[1], reverse=True)[
        0].shape[1]
    max_height = sorted(images, key=lambda x: x.shape[0], reverse=True)[
        0].shape[0]
    row, col = recommend_row_col(len(images))
    black_image = np.zeros((max_height * row, max_width * col, 3), np.uint8)
    if row == 1 and col == 1:
        return images[0]
    count = 0
    for i in range(row):
        for j in range(col):
            if count < len(images):
                image = images[count]
                black_image[i * max_height:i * max_height + image.shape[0],
                            j * max_width:j * max_width + image.shape[1]] = image
                bbox_dict["x"] = j * max_width
                bbox_dict["y"] = i * max_height
                bbox_dict["width"] = image.shape[1]
                bbox_dict["height"] = image.shape[0]
                bbox_locate_list.append(bbox_dict.copy())
                count += 1
    return (black_image, bbox_locate_list)

# def convert_cv_qtpixmap(cv_img, display_width, display_height):
#     """Convert from an opencv image to QPixmap"""
#     rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
#     h, w, ch = rgb_image.shape
#     bytes_per_line = ch * w
#     convert_to_qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
#     p = convert_to_qt_format.scaled(display_width, display_height, Qt.KeepAspectRatio)
#     return QPixmap.fromImage(p)

# def update_label(label:QLabel, images, widght, height):
#     qtpm =  convert_cv_qtpixmap(images, widght, height)
#     label.setPixmap(qtpm)



# def dial_numbers(numbers_list = ["+84349403820"]):
#     """Dials one or more phone numbers from a Twilio phone number."""
    
#     # Twilio phone number goes here. Grab one at https://twilio.com/try-twilio
#     # and use the E.164 format, for example: "+12025551234"
#     TWILIO_PHONE_NUMBER = "+12532317439"

#     # URL location of TwiML instructions for how to handle the phone call
#     TWIML_INSTRUCTIONS_URL = \
#     "http://static.fullstackpython.com/phone-calls-python.xml"

#     # replace the placeholder values with your Account SID and Auth Token
#     # found on the Twilio Console: https://www.twilio.com/console
#     client = Client("ACee0489cf3bc9070f4d72ff3441cd07b1", "efd3d9809a09a0566516bc3c14c9328e")
#     for number in numbers_list:
#         print("Dialing " + number)
#         # set the method to "GET" from default POST because Amazon S3 only
#         # serves GET requests on files. Typically POST would be used for apps
#         client.calls.create(to=number, from_=TWILIO_PHONE_NUMBER,
#                             url=TWIML_INSTRUCTIONS_URL, method="GET")

def check_number(text):
    try:
        float(text)
        return True
    except ValueError:
        return False


def convert_ratio_to_coordination(list_ratio, size):
    list_point = []
    w = size[0]
    h = size[1]
    for e in list_ratio:
        x = e[0]*w
        y = e[1]*h
        list_point.append((x, y))
    return list_point


def convert_coordination_to_ratio(list_points, size):
    list_ratio = []
    w = size[0]
    h = size[1]
    for e in list_points:
        r1 = e[0]/w
        r2 = e[1]/h
        list_ratio.append((r1, r2))
    return list_ratio


def recommend_row_col(n):
    if n > 2 and isprime(n):
        n += 1
    dictionary = {}
    for i in range(1, n + 1):
        if n % i == 0:
            dictionary[i + n // i] = [i, n // i]
    return dictionary[min(dictionary.keys())]


def base64_2_img(data) -> np.array:
    data = base64.b64decode(data.encode('utf-8'))
    array_px = np.frombuffer(data, np.uint8)
    f = cv2.imdecode(array_px, cv2.IMREAD_COLOR)
    return f

# def img_2_base64(data, param) -> np.array:
#     img_to_byte = cv2.imencode('.jpg', data, params=param)[1].tobytes()
#     byte_to_base64 = base64.b64encode(img_to_byte)
#     return byte_to_base64.decode('utf-8')


def img_2_base64(data):
    image_to_byte = cv2.imencode('.jpg', data)[1].tobytes()
    byte_to_base64 = base64.b64encode(image_to_byte)
    return byte_to_base64.decode('ascii')


def encoding_json_payload(data) -> np.array:
    data_json = json.dumps(data, indent=2, separators=(",", " : "))
    data_json = str(data_json)
    data_json_encode = data_json.encode('ascii')
    return data_json_encode


def str_2_dict(data):
    return json.loads(data)


def json_to_string(data):
    return json.dumps(data)


def convert_2_point_to_4_point(polygon):
    x1, y1, x2, y2 = polygon[0]
    points = np.array([[x1, y1], [x1, y2], [x2, y2], [x2, y1]], dtype=np.int32)
    points = points.reshape((-1, 1, 2))
    return points


def clip_coords(boxes, shape):
    # Clip bounding xyxy bounding boxes to image shape (height, width)
    if isinstance(boxes, torch.Tensor):  # faster individually
        boxes[:, 0].clamp_(0, shape[1])  # x1
        boxes[:, 1].clamp_(0, shape[0])  # y1
        boxes[:, 2].clamp_(0, shape[1])  # x2
        boxes[:, 3].clamp_(0, shape[0])  # y2
    else:  # np.array (faster grouped)
        boxes[:, [0, 2]] = boxes[:, [0, 2]].clip(0, shape[1])  # x1, x2
        boxes[:, [1, 3]] = boxes[:, [1, 3]].clip(0, shape[0])  # y1, y2


def scale_coords(img1_shape, coords, img0_shape, ratio_pad=None):
    # Rescale coords (xyxy) from img1_shape to img0_shape
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0],
                   img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (img1_shape[1] - img0_shape[1] * gain) / \
            2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]

    coords[:, [0, 2]] -= pad[0]  # x padding
    coords[:, [1, 3]] -= pad[1]  # y padding
    coords[:, :4] /= gain
    clip_coords(coords, img0_shape)
    return coords


def box_area(box):
    return (box[2] - box[0]) * (box[3] - box[1])


def box_iou(box1, box2, eps=1e-7):
    # https://github.com/pytorch/vision/blob/master/torchvision/ops/boxes.py
    """
    Return intersection-over-union (Jaccard index) of boxes.
    Both sets of boxes are expected to be in (x1, y1, x2, y2) format.
    Arguments:
        box1 (Tensor[N, 4])
        box2 (Tensor[M, 4])
    Returns:
        iou (Tensor[N, M]): the NxM matrix containing the pairwise
            IoU values for every element in boxes1 and boxes2
    """

    # inter(N,M) = (rb(N,M,2) - lt(N,M,2)).clamp(0).prod(2)
    (a1, a2), (b1, b2) = box1[:, None].chunk(2, 2), box2.chunk(2, 1)
    inter = (torch.min(a2, b2) - torch.max(a1, b1)).clamp(0).prod(2)

    # IoU = inter / (area1 + area2 - inter)
    return inter / (box_area(box1.T)[:, None] + box_area(box2.T) - inter + eps)


def xywh2xyxy(x):
    # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
    y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
    y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
    y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
    return y


def non_max_suppression(
        prediction,
        conf_thres=0.25,
        iou_thres=0.45,
        classes=None,
        agnostic=False,
        multi_label=False,
        labels=(),
        max_det=300,
        nm=0,  # number of masks
):
    """Non-Maximum Suppression (NMS) on inference results to reject overlapping detections

    Returns:
         list of detections, on (n,6) tensor per image [xyxy, conf, cls]
    """

    # YOLOv5 model in validation model, output = (inference_out, loss_out)
    if isinstance(prediction, (list, tuple)):
        prediction = prediction[0]  # select only inference output

    device = prediction.device
    mps = 'mps' in device.type  # Apple MPS
    if mps:  # MPS not fully supported yet, convert tensors to CPU before NMS
        prediction = prediction.cpu()
    bs = prediction.shape[0]  # batch size
    nc = prediction.shape[2] - nm - 5  # number of classes
    xc = prediction[..., 4] > conf_thres  # candidates

    # Checks
    assert 0 <= conf_thres <= 1, f'Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0'
    assert 0 <= iou_thres <= 1, f'Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0'

    # Settings
    # min_wh = 2  # (pixels) minimum box width and height
    max_wh = 7680  # (pixels) maximum box width and height
    max_nms = 30000  # maximum number of boxes into torchvision.ops.nms()
    time_limit = 0.5 + 0.05 * bs  # seconds to quit after
    redundant = True  # require redundant detections
    multi_label &= nc > 1  # multiple labels per box (adds 0.5ms/img)
    merge = False  # use merge-NMS

    t = time.time()
    mi = 5 + nc  # mask start index
    output = [torch.zeros((0, 6 + nm), device=prediction.device)] * bs
    for xi, x in enumerate(prediction):  # image index, image inference
        # Apply constraints
        # x[((x[..., 2:4] < min_wh) | (x[..., 2:4] > max_wh)).any(1), 4] = 0  # width-height
        x = x[xc[xi]]  # confidence

        # Cat apriori labels if autolabelling
        if labels and len(labels[xi]):
            lb = labels[xi]
            v = torch.zeros((len(lb), nc + nm + 5), device=x.device)
            v[:, :4] = lb[:, 1:5]  # box
            v[:, 4] = 1.0  # conf
            v[range(len(lb)), lb[:, 0].long() + 5] = 1.0  # cls
            x = torch.cat((x, v), 0)

        # If none remain process next image
        if not x.shape[0]:
            continue

        # Compute conf
        x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf

        # Box/Mask
        # center_x, center_y, width, height) to (x1, y1, x2, y2)
        box = xywh2xyxy(x[:, :4])
        mask = x[:, mi:]  # zero columns if no masks

        # Detections matrix nx6 (xyxy, conf, cls)
        if multi_label:
            i, j = (x[:, 5:mi] > conf_thres).nonzero(as_tuple=False).T
            x = torch.cat((box[i], x[i, 5 + j, None],
                          j[:, None].float(), mask[i]), 1)
        else:  # best class only
            conf, j = x[:, 5:mi].max(1, keepdim=True)
            x = torch.cat((box, conf, j.float(), mask), 1)[
                conf.view(-1) > conf_thres]

        # Filter by class
        if classes is not None:
            x = x[(x[:, 5:6] == torch.tensor(classes, device=x.device)).any(1)]

        # Apply finite constraint
        # if not torch.isfinite(x).all():
        #     x = x[torch.isfinite(x).all(1)]

        # Check shape
        n = x.shape[0]  # number of boxes
        if not n:  # no boxes
            continue
        elif n > max_nms:  # excess boxes
            # sort by confidence
            x = x[x[:, 4].argsort(descending=True)[:max_nms]]
        else:
            x = x[x[:, 4].argsort(descending=True)]  # sort by confidence

        # Batched NMS
        c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
        # boxes (offset by class), scores
        boxes, scores = x[:, :4] + c, x[:, 4]
        i = torchvision.ops.nms(boxes, scores, iou_thres)  # NMS
        if i.shape[0] > max_det:  # limit detections
            i = i[:max_det]
        if merge and (1 < n < 3E3):  # Merge NMS (boxes merged using weighted mean)
            # update boxes as boxes(i,4) = weights(i,n) * boxes(n,4)
            iou = box_iou(boxes[i], boxes) > iou_thres  # iou matrix
            weights = iou * scores[None]  # box weights
            x[i, :4] = torch.mm(weights, x[:, :4]).float(
            ) / weights.sum(1, keepdim=True)  # merged boxes
            if redundant:
                i = i[iou.sum(1) > 1]  # require redundancy

        output[xi] = x[i]
        if mps:
            output[xi] = output[xi].to(device)
        if (time.time() - t) > time_limit:
            # LOGGER.warning(f'WARNING ⚠️ NMS time limit {time_limit:.3f}s exceeded')
            break  # time limit exceeded

    return output
