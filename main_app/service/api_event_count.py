from .base_api import BaseApi
import requests
from PyQt5.QtCore import QUuid
from requests.exceptions import ConnectTimeout
from ..config import WEB_HOST

class CountEventApi(BaseApi):

    def __init__(self):
        super().__init__()
        self._URI_PERSON_EVENT = f"{WEB_HOST}/Service/api/synchronize/peopleCount"
        
    def post_count_event(self, json_data):
        try:
            resp_person = requests.post(self._URI_PERSON_EVENT,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {self._token}"},
                                 json=json_data, timeout=5)

            if resp_person.status_code == 200:
                return resp_person.json()
            elif resp_person.status_code == 400:
                return {}
            elif resp_person.status_code == 500:
                return {}
            else:
                self.get_access_token()
                resp_person = requests.post(self._URI_PERSON_EVENT,
                              headers={"Content-Type": "application/json",
                                       "Authorization": f"Bearer {self._token}"},
                              json=json_data, timeout=20)
                return resp_person.json()
        except ConnectTimeout:
            raise ConnectTimeout("Timeout when post person event")
        
        except Exception as e:
            print(e)
            return {}

if __name__ == "__main__":
    data = {
        "EventId" :QUuid.createUuid().toString(QUuid.StringFormat.WithoutBraces),
        "PeopleCount":10 , #int
        "AccessDate" :"2023-02-16 22:40:00",
        "DeviceId" :256 #int Veska: 256
    }
    
    pea = CountEventApi()
    resp = pea.post_count_event(data)
    print(resp)
