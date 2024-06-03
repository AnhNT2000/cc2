import cv2
import numpy as np
import base64

def polygon_to_points(polygon):
    points = np.array(polygon, np.int32)
    points = points.reshape((-1, 1, 2))
    return points


def image_to_base64(image):
    img_to_byte = cv2.imencode('.jpg', image)[1].tobytes()
    byte_to_base64 = base64.b64encode(img_to_byte)
    return byte_to_base64.decode('ascii')  # chuyển về string


def is_in_polygon(box, polygon):
    x1, y1, x2, y2 = box
    #center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
    points = np.array(polygon, np.int32)
    points = points.reshape((-1, 1, 2))
    return cv2.pointPolygonTest(points, (x1, y2), False) >= 0