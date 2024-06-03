from datetime import datetime
from PyQt5.QtCore import QDateTime, QUuid


class BaseResult(object):
    def __init__(self):
        self.dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.event_id =  QUuid.createUuid().toString(QUuid.StringFormat.WithoutBraces)
        self.people_count = 0
        self.device_id = 256