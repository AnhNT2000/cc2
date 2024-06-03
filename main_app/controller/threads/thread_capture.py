import os
from PyQt5.QtCore import QThread, QTimer
from queue import Queue
import cv2
from ...model.camera import Camera
import time
from ...config import ROOT
from ...util import read_json_data, write_json_data, update_json_data
from ...service.camera_api import CameraApi
import socket
from urllib.parse import urlparse

class ThreadCapture(QThread):
    def __init__(self, camera: Camera):
        super().__init__()
        self.__thread_active = False
        self.__buffer_cap = Queue()
        self.__max_buffer_size = 10
        self.__camera = camera
        self._previous_link = self.__camera.link
        self.http_link = os.path.join(ROOT, "resources/data", "http_link.json")

        self.__camera_api = CameraApi()
        
        self.timer_check_alive_camera = QTimer()
        self.timer_check_alive_camera.timeout.connect(self.timed_stats_check)
        self.timer_check_alive_camera.setInterval(60000)
        self.timer_check_alive_camera.start()
    
    def check(self, host, port, timeout=2):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # presumably
        sock.settimeout(timeout)
        try:
            sock.connect((host, port))
        except:
            return False
        else:
            sock.close()
            return True

    def timed_check(self, host, port, timeout=2):
        t0 = time.time()
        if self.check(host, port, timeout):
            return time.time()-t0  # a bit inexact but close enough


    def timed_stats_check(self):
        
        data = read_json_data(self.http_link)
        if str(self.__camera.id) in data:
            host, port = data[str(self.__camera.id)]
            t = self.timed_check(host, port, timeout=2)
            if t is None:
                self.put_status_camera(self.__camera.id, 2)
                print(f"Camera {self.__camera.id} is OFF")
            else:
                self.put_status_camera(self.__camera.id, 1)
                print(f"Camera {self.__camera.id} is ON")
        else:
            parsed_url = urlparse(self.__camera.link)
            host = parsed_url.hostname
            port = parsed_url.port
            data[str(self.__camera.id)] = [host, port]
            write_json_data(self.http_link, data)

    def put_status_camera(self, camera_id, status):
        self.__camera_api.get_access_token()
        self.__camera_api.put_status_camera(camera_id, status)
        
    def setup_cap(self):
        self._cap = cv2.VideoCapture(self.__camera.link)
        self._previous_link = self.__camera.link
        
    def __reconnect(self):
        self.setup_cap()
        
    @property
    def buffer_cap(self):
        return self.__buffer_cap

    def run(self):
        self.__thread_active = True
        self.setup_cap()
        while self.__thread_active:
            ret, frame = self._cap.read()
            if not ret:
                self.__reconnect()
                time.sleep(3)
                continue
            
            if self._previous_link != self.__camera.link:
                self.setup_cap()
                print("previous link: ", self._previous_link)
                print("new camera link: ", self.__camera.link)
                parsed_url = urlparse(self.__camera.link)
                host = parsed_url.hostname
                port = parsed_url.port
                update_json_data(self.http_link, str(self.__camera.id), host, port)
                continue
            
            if self.__buffer_cap.qsize() < self.__max_buffer_size:
                self.__buffer_cap.put(frame)
                
            self.msleep(30)
    
    def stop(self):
        self.__thread_active = False