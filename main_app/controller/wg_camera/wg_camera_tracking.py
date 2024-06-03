# from ..threads.thread_tracking import ThreadTracking
from ..threads.thread_tracking import ThreadTracking
from ..threads.thread_capture import ThreadCapture
from ..threads.thread_streaming import ThreadStreaming
from ..threads.api.thread_api_count import CountApiThread
from ...model.camera import Camera
from PyQt5.QtWidgets import QMainWindow, QWidget
from ..threads.api.check_time_has_changed import CheckTimeHasChanged
class WgCameraTracking(QWidget):

    def __init__(self, camera: Camera):
        super().__init__()

        self.camera: Camera = camera
        self.__list_thread = []

        self._init_thread(self.camera)

    
    def _init_thread(self, camera):

        self.thread_capture = ThreadCapture(camera)
        self.thread_tracking = ThreadTracking(self.thread_capture.buffer_cap, camera)
        self.thread_streaming = ThreadStreaming(self.thread_tracking.output_stream, camera)
        self.thread_api = CountApiThread()
        self.__list_thread.append(self.thread_capture)
        self.__list_thread.append(self.thread_tracking)
        self.__list_thread.append(self.thread_streaming)
        self.__list_thread.append(self.thread_api)

        self._connect_signal()

    def _connect_signal(self):
        self.thread_tracking.sig_rs.connect(self.thread_api.append_to_list_count_result)

    def start(self):
        for thread in self.__list_thread:
            thread.start()

    def stop(self):
        for thread in self.__list_thread:
            thread.stop()
        self.__list_thread.clear()
