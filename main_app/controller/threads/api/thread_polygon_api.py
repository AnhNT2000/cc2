from PyQt5.QtCore import QThread, pyqtSignal
from ...model.camera import Camera
from ...service.polygon_api import PolygonApi
from ...object_person.polygon import Polygon


class PolygonApiThread(QThread):
    signal_polygon = pyqtSignal(Polygon)

    def __init__(self,camera: Camera):
        super().__init__()
        self.polygon_api = PolygonApi()
        self._camera = camera

    def run(self):
        resp = self.polygon_api.find_polygon_by_id_camera(self._camera.id)
        polygon = Polygon.deserialize(resp)
        self.signal_polygon.emit(polygon)
