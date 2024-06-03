from PyQt5.QtCore import QThread, pyqtSignal
import os 
from queue import Queue
import time
from ....model.count_result import CountResult
from ....service.api_event_count import CountEventApi
from threading import Thread
from requests.exceptions import ConnectTimeout
from typing import List
from ....util import get_logger
from ....config import ROOT
from datetime import datetime
api_logger = get_logger(file_name=os.path.join(ROOT, "resources/log/api_count.log"))

class CountApiThread(QThread):
    signal_is_posted_to_web_server = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.__thread_active = False
        self.__count_api = CountEventApi()
        self.__list_count_rs = Queue()
        self.__max_count_rs = 200
        self.__count_get_access_token = 0
        self.__list_thread:List[Thread] = []
        
    def append_to_list_count_result(self, rs:CountResult):
        # print('append_to_list_count_result')
        if self.__list_count_rs.qsize() < self.__max_count_rs:
            self.__list_count_rs.put(rs)
    
    def post_event(self, rs:CountResult):
        rs_serialize = CountResult.serialize(rs)
        # print("---------------------------", rs_serialize)
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        api_logger.info("{}--{}".format(dt, rs_serialize))
        try:
            resp = self.__count_api.post_count_event(rs_serialize)
            api_logger.info("{}--{}".format(dt, resp))

            # print('---------------------------------',resp)
        except ConnectTimeout as er:
            print(er)
            api_logger.info("{}--{}".format(dt, er))
            self.append_to_list_count_result(rs)

        except Exception as er:
            print(er)
            api_logger.info("{}--{}".format(dt, er))
            print("Error when post count event: {}".format(resp))
            
    def run(self):
        self.__thread_active = True
        pre_time = time.time()
        while self.__thread_active:
            if self.__list_count_rs.qsize() > 0:
                rs = self.__list_count_rs.get()
                
                if self.__count_get_access_token % 30 == 0 or ((time.time() - pre_time) > 300):
                    self.__count_api.get_access_token()
                    pre_time = time.time()
                
                new_thread = Thread(target=self.post_event, args=(rs,))
                new_thread.start()
                self.__list_thread.append(new_thread)
                self.__count_get_access_token += 1
                
                for e in self.__list_thread:
                    e.join()
                    if not e.is_alive():
                        self.__list_thread.remove(e)
            time.sleep(0.01)
   
    def stop(self):
        self.__thread_active = False
        
       