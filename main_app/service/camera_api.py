import requests
import json
from .base_api import BaseApi
from ..config import SERVER_NAME, WEB_HOST
# logging.basicConfig(level=logging.DEBUG)
class CameraApi(BaseApi):
    _URL_GET_LIST_DEVICE = f"{WEB_HOST}/Service/api/Device?"
    _URL_UPDATE_DEVICE = f"{WEB_HOST}/Service/api/device"
    _URL_UPDATE_STATUS_DEVICE = f"{WEB_HOST}/Service/api/device/status"
    
    
    def __init__(self):
        super().__init__()
        # self._function = 1 # 1 for vehicle and 2 for face
        # self._areaId = 67
        self._itemsPerPage = 999
        self._no_page = 1
        # &areaId={self._areaId}
        self._url_param = f"page={self._no_page}&itemsPerPage={self._itemsPerPage}&sortBy=id&sortDesc=true&compId={self.compId}&serverName={SERVER_NAME}"
        self._url_find_all_device = self._URL_GET_LIST_DEVICE + "?" + self._url_param
        self._url_get_accesstime_by_id = f"{WEB_HOST}/Service/api/accesstimeseg/"

    def find_all_camera(self):
        self.get_access_token()
        try:
            data = requests.get(self._url_find_all_device,
                                headers={"Content-Type": "application/json", 
                                         "Authorization": f"Bearer {self._token}"})
            data_str =  json.dumps(data.json(), indent=4, ensure_ascii=False)
            return json.loads(data_str)
        except Exception as e:
            print(e)
            return {}
        
    def get_accesstime_by_id(self, id):
        url = f"{self._url_get_accesstime_by_id}{id}"
        print(url)
        try:
            data = requests.get(url,
                                headers={"Content-Type": "application/json",
                                         "Authorization": f"Bearer {self._token}"})
            data_str = json.dumps(data.json(), indent=4, ensure_ascii=False)
            return json.loads(data_str)
        except Exception as e:
            print("error")
            return {}

    def put_status_camera(self, camera_id, status=1):
        url = self._URL_UPDATE_STATUS_DEVICE + "/{}/{}".format(camera_id, status)
        print(url)
        try: 
            resp = requests.put(url, 
                                headers={"Content-Type": "application/json", 
                                        "Authorization": f"Bearer {self._token}"})
            return resp.json()
        except Exception as er:
            print(er)
            return {}
        

if __name__ == "__main__":
    api = CameraApi()
    api.get_access_token()
    data = api.find_all_camera()
    print(data)