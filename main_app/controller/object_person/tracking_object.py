import time
from PyQt5.QtCore import pyqtSignal, QTimer, QObject
import statistics
import numpy as np
import math
from collections import deque, Counter
from ...config import STD, LENGTH_LOCATION, LENGTH_CENTER, TIME_OUT

class Object_ID(QObject):
    def __init__(self, track_id) -> None:
        super().__init__()

        self.in_time = time.time()
        self.last_time_in_polygon = time.time()
        self.live_time = 0
        self.track_id = track_id
        self._location_history_x = []
        self._location_history_y = []
        self._std = STD
        # self.directions = deque(maxlen=5) 
        self.direction = None
        self.moving = True
        self.length = LENGTH_LOCATION
        self.length_center = LENGTH_CENTER
        self.list_center = []
        self.time_direction = time.time()
        self.time_out = TIME_OUT
        self.is_in_polygon = True

    def set_time(self):
        self.in_time = time.time()

    def update_time(self):
        self.live_time = self.last_time_in_polygon-self.in_time

    
    def update_location(self, a_location):
        if len(self._location_history_x) >= self.length:
            self._location_history_x.pop(1)
            self._location_history_x.append(a_location[0])
        else:
            self._location_history_x.append(a_location[0]) 
           
        
        if len(self._location_history_y) >= self.length:
            self._location_history_y.pop(1)
            self._location_history_y.append(a_location[1])
        else:
            self._location_history_y.append(a_location[1])

    def update_center(self, location):
        center = (location[0] + location[2])//2, (location[1] + location[3])//2
        if len(self.list_center) >= self.length_center:
            self.list_center.pop(1)
            self.list_center.append(center)
        else:
            self.list_center.append(center)

    def check_moving(self):
        if len(self._location_history_x) > 1:
            xstd = statistics.stdev(self._location_history_x)
            ystd = statistics.stdev(self._location_history_y)
            #if len(self._location_history_x) >= self.length:
            if xstd < self._std and ystd < self._std and len(self._location_history_x) >= self.length:
                    self.moving = False
            else:
                    # print("1111111111111111111111111")
                    self.moving = True
   
    def calculate_time_direction(self):
            """
            Calculates the time direction based on the current time and the time the object entered.

            Returns:
                The direction of the object.
            """
            if self.time_direction - self.in_time > self.time_out:
               dY = self.list_center[-1][1] - self.list_center[0][1]
               if np.abs(dY) > 40:
                   self.direction = "in" if np.sign(dY) == 1 else "out"
                   
    def calculate_time_direction_x(self):
        if self.time_direction - self.in_time > self.time_out:
            dX = self.list_center[0][0] - self.list_center[-1][0]
            if np.abs(dX) > 40:
                self.direction = "out" if np.sign(dX)==1 else "in"
        
    
    # def get_direction(self):    
    #     dY = self.list_center[-1][1] - self.list_center[0][1]
    #     if np.abs(dY) > 15:
            
    #         return "in" if np.sign(dY) == 1 else "out"

    
            
                
    @staticmethod
    def find_direction(list_center):
        for i in range(1, len(list_center)):
            dY = list_center[-1][1] - list_center[i][1]
            if np.abs(dY) > 15:
                return True
        return False
    
    

class LocationObject:
    def __init__(self, a_location) -> None:
        self.location = a_location
        self.time = time.time()


