from PyQt5.QtWidgets import QMainWindow, QWidget
import time
import sqlite3
from sqlite3 import Error
from ..model.camera import Camera
from typing import List
from ..controller.threads.api.check_has_changed_camera import CheckHasChange
from ..service.camera_api import CameraApi
from ..service.polygon_api import PolygonApi
from ..model.polygon import Polygon
from .wg_camera import WgCameraTracking, WgCameraDetect
from ..service.camera_api import CameraApi
from PyQt5.QtCore import QTimer
from ..config import ROOT
import os

class MainController(QMainWindow):
    def __init__(self) :
        super().__init__()
        self.polygonApi = PolygonApi()
        self.config_camera = []
        self.list_camera = []
        self.__camera_api = CameraApi()
        self.conn = sqlite3.connect(os.path.join(ROOT,'resources/database/database.db'))
        self._init_camera()
        self.start_camera()
        self.check_has_changed_camera = CheckHasChange(source_list=self.config_camera)
        self.check_has_changed_camera.start()
        self.check_has_changed_camera.signal_has_update_camera.connect(self.__update_camera)
        self._put_status_camera()
        
    def _put_status_camera(self):
        self.__camera_api.get_access_token()
        data_camera = self.__camera_api.find_all_camera()
        data_camera = data_camera['data']

        # print('---------------------------',data_camera)
        for e in data_camera:
            self.__camera_api.put_status_camera(e['id'], 1)
        
    def _init_camera(self):
        self.config_camera = self._init_config_camera()
        self.__filter_by_function()
    
    def __filter_by_function(self):
        if self.config_camera:
            for e in self.config_camera:
                
                if int(e.function) == 4:
                    new_camera = WgCameraTracking(e)
                    self.list_camera.append(new_camera)
                elif int(e.function) == 3:
                    new_camera = WgCameraDetect(e)
                    self.list_camera.append(new_camera)

    def _init_config_camera(self):
        configs:List[Camera] = []
        self.__camera_api.get_access_token()
        data_json = self.__camera_api.find_all_camera()
        print('---------------------------',data_json)
        data_json = data_json['data']
        
        for e in data_json:
            new_cf = Camera.deserialize(e)
            self.insert_camera_to_datatbase(new_cf)
            data_polygon = self.polygonApi.find_polygon_by_id_camera(new_cf.id)
            if len(data_polygon['data']):
                new_cf.polygon = Polygon.deserialize(data_polygon['data'])
            else:
                new_cf.polygon = Polygon.get_default_polygon(new_cf.id)
            configs.append(new_cf)
        return configs
    
    def insert_camera_to_datatbase(self, camera: Camera):
        try:
            cursor = self.conn.cursor()
            data = (camera.id, 0, 0, time.strftime("%d/%m/%Y"))
            cursor.execute("INSERT INTO count (id_camera, count_in, count_out, datetime) VALUES (?, ?, ?, ?)", data)
            # Commit the changes to the database
            self.conn.commit()
            cursor.close()

        except Exception as e:
            # print("Error when insert camera: {}".format(e))
            self.conn.rollback()
    # def insert_camera_to_datatbase(self, camera: Camera):
    #     try:
    #         # cursor = self.conn.cursor()
    #         # data = (camera.id, 0, 0, time.strftime("%d/%m/%Y"))
    #         # cursor.execute("INSERT INTO count (id_camera, count_in, count_out, datetime) VALUES (?, ?, ?, ?)", data)
    #         # # Commit the changes to the database
    #         # self.conn.commit()
    #         # cursor.close()
            
    #         cursor = self.conn.cursor()
    #         cursor.execute("SELECT * FROM count WHERE id_camera = ?", (camera.id,))
    #         rows = cursor.fetchone()
    #         if rows is None:
    #             data = (camera.id, 0, 0, time.strftime("%d/%m/%Y"))
    #             cursor.execute("INSERT INTO count (id_camera, count_in, count_out, datetime) VALUES (?, ?, ?, ?)", data)
    #         else:
    #             data = (0, 0, time.strftime("%d/%m/%Y"), camera.id)
    #             cursor.execute("UPDATE count SET count_in = ?, count_out = ?, datetime = ? WHERE id_camera = ?", data)
    #         self.conn.commit()
    #         cursor.close()

    #     except Exception as e:
    #         print("Error when insert camera: {}".format(e))
    #         self.conn.rollback()
                  

    def start_camera(self):
        print('----------------------------len',len(self.list_camera))
        if len(self.list_camera):
            for camera in self.list_camera:
                camera.start()
                
    def stop_camera(self):
        if len(self.list_camera):
            for camera in self.list_camera:
                camera.stop()
        self.list_camera.clear()
        
               
    def __update_camera(self, camera: Camera):
        old_wg = self.__find_wg_by_camera(camera)
        old_cam = self.__find_camera_by_id(camera.id)
        
        ### camera is deleted in web
        if old_cam is None:
            old_wg.stop()
            time.sleep(2)
            self.list_camera.remove(old_wg)
            print("stop cam iss deleted")
            return

        ### new camera
        if old_wg is None:
            self.insert_camera_to_datatbase(camera)
            if int(camera.function) == 4:
                new_camera = WgCameraTracking(camera)
                self.list_camera.append(new_camera)
            elif int(camera.function) == 3:
                new_camera = WgCameraDetect(camera)
                self.list_camera.append(new_camera)
            new_camera.start()
            print("new camera")
            return
    
    def __find_wg_by_camera(self, camera:Camera):
        if self.list_camera:
            for e in self.list_camera:
                if e.camera == camera:
                    return e
        return None
                  
    
    def __find_camera_by_id(self, id_camera):
        if self.config_camera:
            for e in self.config_camera:
                if e.id == id_camera:
                    return e
        return None