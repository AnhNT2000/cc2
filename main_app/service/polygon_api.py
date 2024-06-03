from .base_api import BaseApi
import requests
from PyQt5.QtCore import QUuid
from ..config import WEB_HOST_POLYGON


class PolygonApi(object):
    
    def __init__(self):
        super().__init__()
        self.URL_UPDATE_POLYGON = f"{WEB_HOST_POLYGON}/api/polygon/updatePolygon"
        self.URL_GET_POLYGON_BY_ID_CAMERA = f"{WEB_HOST_POLYGON}/api/polygon/findPolygonByIdCamera"

    def update_polygon(self, json_data):
        try:
            resp_person = requests.post(self.URL_UPDATE_POLYGON,
                                        headers={
                                            "Content-Type": "application/json"},
                                        json=json_data, timeout=5)

            if resp_person.status_code == 200:
                return resp_person.json()
            elif resp_person.status_code == 400:
                print("Error 400 at polygon api")
                return {}
            elif resp_person.status_code == 500:
                print("Error 500 at polygon api")
                return {}

        except Exception as e:
            print(e)
            return {}

    def find_polygon_by_id_camera(self, id_camera: int) -> 'dict':
        payload = {"id": id_camera}
        try:
            resp_person = requests.get(self.URL_GET_POLYGON_BY_ID_CAMERA,
                                       headers={
                                           "Content-Type": "application/json"},
                                       json=payload,
                                       timeout=5)

            if resp_person.status_code == 200:
                return resp_person.json()
            elif resp_person.status_code == 400:
                print("Error 400 at polygon api, cannot get polygon")
                return {"data": {}}
            elif resp_person.status_code == 500:
                print("Error 500 at polygon api, cannot get polygon")
                return {"data": {}}
        except Exception as e:
            print(e)
            return {"data": {}}


if __name__ == "__main__":
    pea = PolygonApi()
    resp = pea.find_polygon_by_id_camera(177)
    print(resp)
