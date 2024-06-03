import numpy as np


class Polygon(object):
    def __init__(self):
        self.id_camera = None
        self.area_active = []

    @staticmethod
    def get_default_polygon(id_camera) -> "Polygon":
        polygon = Polygon()
        polygon.id_camera = id_camera
        polygon.area_active = [
            (0.0009, 0.0033), (0.0009, 0.9983), (1.0, 0.9983), (1.0, 0.0033)]
        return polygon

    @staticmethod
    def deserialize(data) -> "Polygon":
        try:
            polygon = Polygon()
            polygon.id_camera = data["id"]
            # print("data active area: ", data["active_area"])
            for e in data["active_area"]:
                x = e["x"]
                y = e["y"]
                polygon.area_active.append((x, y))
            return polygon
        except Exception as err:
            print("Error Polygon *********************************: ", err)
            return None

    @staticmethod
    def serialize(polygon: "Polygon") -> "dict":
        return {
            "id": polygon.id_camera,
            "active_area": polygon.area_active,
        }

    @staticmethod
    def convert_to_point_format(active_area, w, h):
        list_point = []
        for e in active_area:
            x = e[0] * w
            y = e[1] * h
            list_point.append((x, y))
        list_point = np.array(list_point, dtype=np.int32)
        detect_polygon = list_point.reshape((-1, 1, 2))
        return detect_polygon, list_point
