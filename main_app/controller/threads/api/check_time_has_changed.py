from PyQt5.QtCore import QObject, QThread
from ....model.time_acess import TimeAcess
from ....model.camera import Camera
from ....service.camera_api import CameraApi

class CheckTimeHasChanged(QThread):

    def __init__(self, camera: Camera):
        super().__init__()
        self.__thread_active = False
        self.__camera_api = CameraApi()
        self.__camera = camera
        self.data_time_access = {}

    def __check_time_has_changed(self):
        self.__camera_api.get_access_token()
        print("check time has changed", self.__camera.timeSegId)
        self.data_time_access = self.__camera_api.get_accesstime_by_id(self.__camera.timeSegId)

    def run(self):
        self.__thread_active = True
        while self.__thread_active:
            self.__check_time_has_changed()
            self.msleep(10000)