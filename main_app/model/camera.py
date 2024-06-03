from typing import List
from .polygon import Polygon
import cv2
import os
from urllib.parse import urlparse


class Camera(object):
    def __init__(self):
        super().__init__()
        self.id = None
        self.id_company = 1
        self.area_code = ""
        self.area_id = 7
        self.name = ""
        self.code = None
        self.link = None
        self.function = 1
        self.polygon: Polygon
        self.status = 0
        self.functions = "1"
        self.capture_fps = 40
        self.streaming_fps = 25
        self.record_fps = 15
        self.timeSegId = 196
        self.old_state = False
        self.server = None
        self.serverName = None
        self.longitude = None
        self.latitude = None
        self.registerTime = None
        self.registerBy = None
        self.updateTime = None
        self.updateBy = None
        self.deleteTime = None
        self.deleteBy = None
        self.direction = None
        self.isDelete = False
        self.featuresName = None
        self.featuresCode = None
        self.statusName = None
        self.featureId = None
        self.currentStatus = None
        self.syncDate = None
        self.currentStatusName = None
        self.morningFinish = None
        self.eveningBegin = None

    def merge_data(self, __o: "Camera"):
        self.id_company = __o.id_company
        self.capture_fps = __o.capture_fps
        self.area_code = __o.area_code
        self.name = __o.name
        self.code = __o.code
        self.link = __o.link
        self.function = __o.function
        self.polygon = __o.polygon
        self.server = __o.server
        self.serverName = __o.serverName
        self.longitude = __o.longitude
        self.latitude = __o.latitude
        self.registerTime = __o.registerTime
        self.registerBy = __o.registerBy
        self.updateTime = __o.updateTime
        self.updateBy = __o.updateBy
        self.deleteTime = __o.deleteTime
        self.deleteBy = __o.deleteBy
        self.direction = __o.direction
        self.isDelete = __o.isDelete
        self.featuresName = __o.featuresName
        self.featuresCode = __o.featuresCode
        self.statusName = __o.statusName
        self.featureId = __o.featureId
        self.currentStatus = __o.currentStatus
        self.syncDate = __o.syncDate
        self.currentStatusName = __o.currentStatusName
        self.morningFinish = __o.morningFinish
        self.eveningBegin = __o.eveningBegin

    def check_difference(self, __o: "Camera"):
        is_changed_area_code = self.area_code == __o.area_code
        is_changed_code = self.code == __o.code
        is_changed_link = self.link == __o.link
        is_changed_function = self.function == __o.function
        is_change_polygon = self.polygon == __o.polygon
        is_changed_serverName = self.serverName == __o.serverName
        is_changed_longitude = self.longitude == __o.longitude
        is_changed_latitude = self.latitude == __o.latitude
        # Add more checks for other new attributes here...

        return is_changed_area_code or is_changed_code \
            or is_changed_link or is_changed_function \
            or is_change_polygon or is_changed_serverName \
            or is_changed_longitude or is_changed_latitude

    @staticmethod
    def deserialize(data) -> "Camera":
        try:
            new_camera = Camera()
            new_camera.id = data["id"]
            new_camera.function = data["function"]
            new_camera.link = data["link"]
            new_camera.name = data["name"]
            new_camera.area_id = int(data["areaId"])
            new_camera.id_company = data["idComp"]
            new_camera.area_code = data["areaCode"]
            new_camera.code = data["code"]
            new_camera.server = data.get("server")
            new_camera.serverName = data.get("serverName")
            new_camera.longitude = data.get("longitude")
            new_camera.latitude = data.get("latitude")
            new_camera.registerTime = data.get("registerTime")
            new_camera.registerBy = data.get("registerBy")
            new_camera.updateTime = data.get("updateTime")
            new_camera.updateBy = data.get("updateBy")
            new_camera.deleteTime = data.get("deleteTime")
            new_camera.deleteBy = data.get("deleteBy")
            new_camera.direction = data.get("direction")
            new_camera.isDelete = data.get("isDelete")
            new_camera.featuresName = data.get("featuresName")
            new_camera.featuresCode = data.get("featuresCode")
            new_camera.statusName = data.get("statusName")
            new_camera.featureId = data.get("featureId")
            new_camera.currentStatus = data.get("currentStatus")
            new_camera.syncDate = data.get("syncDate")
            new_camera.currentStatusName = data.get("currentStatusName")
            new_camera.morningFinish = data.get("morningFinish")
            new_camera.eveningBegin = data.get("eveningBegin")
        except Exception as e:
            print(e)
        return new_camera

    @staticmethod
    def desirialize_list_data(list_data_dict: dict) -> List["Camera"]:
        list_camera: List[Camera] = []
        for e in list_data_dict:
            list_camera.append(Camera.deserialize(e))
        return list_camera

    def serialize(self):
        return {
            "id": self.id,
            "idComp": self.id_company,
            "areaCode": self.area_code,
            "areaId": self.area_id,
            "name": self.name,
            "code": self.code,
            "link": self.link,
            "function": self.function,
            "server": self.server,
            "serverName": self.serverName,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "registerTime": self.registerTime,
            "registerBy": self.registerBy,
            "updateTime": self.updateTime,
            "updateBy": self.updateBy,
            "deleteTime": self.deleteTime,
            "deleteBy": self.deleteBy,
            "direction": self.direction,
            "isDelete": self.isDelete,
            "featuresName": self.featuresName,
            "featuresCode": self.featuresCode,
            "statusName": self.statusName,
            "featureId": self.featureId,
            "currentStatus": self.currentStatus,
            "syncDate": self.syncDate,
            "currentStatusName": self.currentStatusName,
            "morningFinish": self.morningFinish,
            "eveningBegin": self.eveningBegin,
            # Add more attributes here...
        }

    def is_different_from(self, __o: 'Camera'):
        is_changed_ = (self.id_company != __o.id_company) \
            or (self.area_code != __o.area_code) \
            or (self.code != __o.code) \
            or (self.link != __o.link) \
            or (self.function != __o.function)
        # or self.polygon == __o.polygon
        return is_changed_

    @staticmethod
    def ping_to_rtsp_host(link):
        parse = urlparse(link)
        host = parse.hostname
        resp = os.system("ping " + host)
        return resp == 0

    @staticmethod
    def check_status_camera(link):
        cap = cv2.VideoCapture()
        flag = cap.open(link)
        return flag

    def __eq__(self, __o: 'Camera') -> bool:
        return self.id == __o.id

    def toString(self):
        return f"{self.id} {self.link} {self.code} {self.area_code}"
