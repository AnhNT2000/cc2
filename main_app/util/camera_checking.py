import os
import cv2
from urllib.parse import urlparse

ALLOW_LINK = ["rtsp", "rtmp"]

def ping_rtsp_host(link):
    parse = urlparse(link)
    host = parse.hostname
    command = "ping {}".format(host)
    resp = os.system(command)
    return resp == 0
  
def check_status_camera(link):
    # parse_uri = urlparse(link)
    # if parse_uri.scheme not in ALLOW_LINK:
    #     return False
    try:
        cap = cv2.VideoCapture(link)
        # cap.set(cv2.CAP_PROP_BUFFERSIZE, 10)
        # cap.set(cv2.CAP_PROP_XI_TIMEOUT, 100)
        ret, _ = cap.read()
        return ret
    except Exception as e:
        print(e)
        return False