from datetime import datetime
from PyQt5.QtCore import QDateTime, QUuid

class CountResult(object):
    def __init__(self):
        super().__init__()
        self.dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.event_id = QUuid.createUuid().toString(QUuid.StringFormat.WithoutBraces)
        self.people_count = 0
        self.device_id = 256
        self.comp_id = 89
        self.in_out = 1
        self.area_id = 1

    @staticmethod
    def serialize(rs:"CountResult"):

        data = {
            "EventId": rs.event_id,
            "PeopleCount": rs.people_count,
            "AccessDate": rs.dt,
            "DeviceId": rs.device_id,
            "CompId": rs.comp_id,
            "InOut": rs.in_out,
            "AreaId": rs.area_id
        }

        return data