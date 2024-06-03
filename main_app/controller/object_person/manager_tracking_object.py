from collections import deque
from typing import List, Dict
from .tracking_object import Object_ID
from PyQt5.QtCore import pyqtSignal, QTimer, QObject
import time
import sqlite3
from datetime import datetime
from ...model.camera import Camera
from ...config import ROOT, TIME_LIVE, EXCEPTION_CAMERA_DIR_X
import os

class ManagerTrackingObject(QObject):
    ALLOW_TIME = 100 # seconds
    sig_count = pyqtSignal(int)
    def __init__(self, camera:Camera):
        super().__init__()
        self.__camera = camera
        self._count_in = 0
        self._count_out = 0
        self.TIME_LIVE = TIME_LIVE
        self._list_counted_id = deque(maxlen=500)
        self.__dict_object_tracking:Dict[int,Object_ID] = {}
        self.__dict_object_not_moving:Dict[int, Object_ID] = {}
        self.current_time = datetime.now().strftime("%d/%m/%Y")
        
        self.__check_current_time()
        self._count_in, self._count_out= self.get_buffer_count()
        
        self.__timer_check_current_time = QTimer()
        self.__timer_check_current_time.timeout.connect(self.__check_current_time)
        self.__timer_check_current_time.setInterval(1000)
        self.__timer_check_current_time.start()
        
        self.__timer_counting = QTimer()
        self.__timer_counting.timeout.connect(self._counting)
        self.__timer_counting.setInterval(100)
        self.__timer_counting.start()


    def __check_current_time(self):
        try:
            # Connect to the SQLite database (creates one if not exists)
            conn = sqlite3.connect(os.path.join(ROOT, "resources/database/database.db"))

            cursor = conn.cursor()

            query_by_id_camera = ''' SELECT * FROM count WHERE id_camera = ?; '''

            # The id_camera value you want to query
            id_camera_to_query = self.__camera.id  # Replace with the id_camera you want to search for

            # Execute the SQL query to select data by id_camera
            cursor.execute(query_by_id_camera, (id_camera_to_query,))

            # Fetch all matching rows
            rows = cursor.fetchall()
            if rows[0][4]!=self.current_time:
                self._count_in = 0
                self._count_out = 0
                self.current_time = rows[0][4]
                self.update_buffer_count()
                # self.sig_count.emit(self._count)
            else:
                pass
            # Close the connection
            conn.close()
        except Exception as e:
            print("Error query datetime: ", e)
            conn.rollback()
            
    def update_buffer_count(self):
        try:
            conn = sqlite3.connect(os.path.join(ROOT, "resources/database/database.db"))

            # Create a cursor object to interact with the database
            cursor = conn.cursor()

            # Define the SQL query to update the value by id_camera
            update_query = '''UPDATE count SET count_in = ?, count_out = ?, datetime=? WHERE id_camera = ?;'''

            # The new value you want to update
            buffer_count_in = self._count_in
            buffer_count_out = self._count_out
            date_time = datetime.now().strftime("%d/%m/%Y")
            cursor.execute(update_query, (buffer_count_in, buffer_count_out, date_time, self.__camera.id))
            conn.commit()
            conn.close()

        except Exception as e:
            print("Error update buffer count: ", e)
            conn.rollback()
            conn.close()
            
    def get_buffer_count(self):
        try:
            # Connect to the SQLite database (creates one if not exists)
            conn = sqlite3.connect(os.path.join(ROOT, "resources/database/database.db"))

            cursor = conn.cursor()

            query_by_id_camera = ''' SELECT * FROM count WHERE id_camera = ?; '''

            # The id_camera value you want to query
            id_camera_to_query = self.__camera.id  

            # Execute the SQL query to select data by id_camera
            cursor.execute(query_by_id_camera, (id_camera_to_query,))

            # Fetch all matching rows
            rows = cursor.fetchall()
            conn.close()
            print("rows: ", rows[0][2],rows[0][3],rows[0][4])
            return rows[0][2], rows[0][3]
        except Exception as e:
            print("Error query count: ", e)
            conn.rollback()
            return 0,0


    def add_object(self, a_object:Object_ID):
        if not self.check_id_not_exist(a_object.track_id):
            self.__dict_object_tracking[a_object.track_id] = a_object

    def find_object(self, a_id):
        if self.check_id_not_exist(a_id):
            return self.__dict_object_tracking[a_id]
        return None
    
    def _remove_object(self, a_id):
        if self.check_id_not_exist(a_id):
            del self.__dict_object_tracking[a_id]
    def _remove_object_not_moving(self, a_id):
        if a_id in self.__dict_object_not_moving:
                del self.__dict_object_not_moving[a_id]
    
    def check_id_not_exist(self, a_id):
        return a_id in self.__dict_object_tracking
    
    def _force_delete(self):
        for k in list(self.__dict_object_tracking.keys()):
            v = self.__dict_object_tracking[k]
            if time.time() - v.last_time_in_polygon > self.ALLOW_TIME:
                del self.__dict_object_tracking[k]
        
        for k in list(self.__dict_object_not_moving.keys()):
            v = self.__dict_object_not_moving[k]
            if time.time() - v.last_time_in_polygon > self.ALLOW_TIME:
                del self.__dict_object_not_moving[k]
    
    def _counting(self):
        try:
            if len(self.__dict_object_tracking):
                list_object = self.__dict_object_tracking.copy()
                for k,v in list_object.items():
                    # flag_counting = False
                    v.update_time()
                    v.check_moving()
                    #v.calculate_time_direction()
                    if int(self.__camera.id) in EXCEPTION_CAMERA_DIR_X:
                        v.calculate_time_direction_x()
                    else:
                        v.calculate_time_direction()
                    
                    if (v.moving is False)  and (v.track_id not in self._list_counted_id):
                        if v not in self.__dict_object_not_moving.values():
                            #print("add not moving: ", v.track_id)
                            self.__dict_object_not_moving[k] = v
                            # print("add not moving", v.track_id)
                            self._remove_object(v.track_id) 
                            
                    if self.__dict_object_not_moving is not None:
                        dict_not_moving = self.__dict_object_not_moving.copy()
                        for i, j in dict_not_moving.items():
                            if (j.track_id not in self._list_counted_id) and (v.live_time > self.TIME_LIVE):
                                if not j.is_in_polygon:
                                    if j.direction is not None:
                                        if j.direction=="in":
                                            self._count_in += 1
                                            self._list_counted_id.append(j.track_id)
                                            self._remove_object_not_moving(j.track_id)
                                            
                                        if j.direction=="out":
                                            self._count_out += 1
                                            self._list_counted_id.append(j.track_id)
                                            self._remove_object_not_moving(j.track_id)

                    condition = (v.track_id not in self._list_counted_id) \
                                    and (v.live_time > self.TIME_LIVE) \
                                       and v.moving and not v.is_in_polygon 
                                 
                    if condition :
                        if v.direction is not None:
                            if v.direction=="in":
                                self._count_in += 1
                                self._remove_object(v.track_id)
                                # print("moving in: ", v.track_id)
                                self._list_counted_id.append(v.track_id)
                            if v.direction=="out":
                                self._count_out += 1
                                # print("moving out: ", v.track_id)
                                self._remove_object(v.track_id)
                                self._list_counted_id.append(v.track_id)

            self._force_delete()
            self.update_buffer_count()
        except Exception as e:
            print(e)
    
    
    
                
                    
                
                
    
    
    
                    
        
    
        
        
            
    
    
  
        
        
    
        
        
    

