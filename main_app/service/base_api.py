import requests
import json
import logging
from ..config import WEB_HOST, USER_NAME, PASSWORD
import time

class BaseApi(object):  
    URL_API_TOKEN = f"{WEB_HOST}/Service/api/token/auth" 
    def __init__(self):
        super().__init__()
        self._token = None
        self.compId = 1
        self.get_access_token()
        self._flag = False
        
        
    
    def get_access_token(self):
        self._flag = True
        old_time = time.time()
        while self._flag:
            if time.time() - old_time < 900:
                    self.sleep(1)
                    continue
            else:      
                try:
                        data_login = {
                                        "client_id": "IAC_Cloud",
                                        "client_secret": "1a82f1d60ba6353bb64a8fb4b05e4bc4",
                                        "grant_type": "password",
                                        "username": USER_NAME,
                                        "password": PASSWORD
                                        }
                        r = requests.post(self.URL_API_TOKEN, json=data_login)
                        r = r.json()
                        self._token = r['access_token']
                        self.compId = r['compId']
                        return True
                except Exception as e:
                        return False
        old_time = time.time()
        