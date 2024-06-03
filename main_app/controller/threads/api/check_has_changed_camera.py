from PyQt5.QtCore import QThread, pyqtSignal
from ....service.camera_api import CameraApi
from ....service.polygon_api import PolygonApi
from ....model.camera import Camera
from ....model.polygon import Polygon
from typing import List
import os
from time import sleep


class CheckHasChange(QThread):
    signal_has_update_camera = pyqtSignal(Camera)
    
    def __init__(self, source_list):
        super().__init__()
        self.__thread_active = False
        self.__interval = 10
        self.__source_list: List[Camera] = source_list
        self.__incomming_data: List[Camera] = []
        # APIs
        self.__camera_api = CameraApi()
        self.__polygon_api = PolygonApi()
        self.camera = Camera()

    def check_has_change(self):
        self.__get_camera_data()
        if self.__source_list and self.__incomming_data:
            for e in self.__source_list:
                new_data = self.find_camera_by_id(e.id, self.__incomming_data)
                if new_data is not None:
                    e.merge_data(new_data)
                else:
                    self.__source_list.remove(e)
                    self.signal_has_update_camera.emit(e) # remove camera
                    
        for ie in self.__incomming_data:   # create new camera
            data = self.find_camera_by_id(ie.id, self.__source_list)
            if data is None:
                self.__source_list.append(ie)
                self.signal_has_update_camera.emit(ie)
        

    def __get_camera_data(self):
        try:
            self.__camera_api.get_access_token()
            data = self.__camera_api.find_all_camera()
            data = data["data"]

            self.__incomming_data.clear()
            for e in data:
                camera = Camera.deserialize(e)
                data_polygon = self.__polygon_api.find_polygon_by_id_camera(
                    camera.id)
                if len(data_polygon["data"]):
                    polygon = Polygon.deserialize(data_polygon["data"])
                    camera.polygon = polygon
                else:
                    polygon = Polygon.get_default_polygon(camera.id)
                    camera.polygon = polygon
                self.__incomming_data.append(camera)
        except Exception as e:
            print("Error get camera for update:  ", e)

    @staticmethod
    def find_camera_by_id(id_camera, list_camera: List[Camera]) -> Camera:
        if list_camera:
            for e in list_camera:
                if e.id == id_camera:
                    return e
        return None
    
    def change_video(self, camera):
        if camera is not None:
            return ("Camera not exist")
        

                   

    def run(self):
        self.__thread_active = True
        while self.__thread_active:
            self.check_has_change()
            sleep(self.__interval)

    def stop(self):
        self.__thread_active = False