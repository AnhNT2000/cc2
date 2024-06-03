# from ..threads.thread_inference import ThreadInference
from ..threads.thread_inference import ThreadInference
from ..threads.thread_capture import ThreadCapture
from ..threads.thread_streaming import ThreadStreaming
from ..threads.api.thread_api_count import CountApiThread
from ...model.camera import Camera
from PyQt5.QtWidgets import QMainWindow, QWidget

class WgCameraDetect(QWidget):

    def __init__(self, camera_config: Camera):
        super().__init__()

        self.camera: Camera = camera_config
        self.__list_thread = []

        self._init_thread(self.camera)
    
    def _init_thread(self, camera):

        self.thread_capture = ThreadCapture(camera)
        self.thread_detect = ThreadInference(self.thread_capture.buffer_cap, camera)
        self.thread_streaming = ThreadStreaming(self.thread_detect.output_stream,camera)
        self.thread_api = CountApiThread()
        self.__list_thread.append(self.thread_capture)
        self.__list_thread.append(self.thread_detect)
        self.__list_thread.append(self.thread_streaming)
        self.__list_thread.append(self.thread_api)

        self._connect_signal()

    def _connect_signal(self):
        self.thread_detect.sig_rs.connect(self.thread_api.append_to_list_count_result)

    def start(self):
        for thread in self.__list_thread:
            thread.start()

    def stop(self):
        for thread in self.__list_thread:
            thread.stop()
        self.__list_thread.clear()
