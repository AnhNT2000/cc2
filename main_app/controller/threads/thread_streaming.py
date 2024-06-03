import subprocess
import cv2
import time
import json
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from queue import Queue
from ...model.camera import Camera
from ...config import CONST_MEDIA_SERVER_HOST, STREAM_SIZE

class ThreadStreaming(QThread):
    def __init__(self, queue_stream: Queue, camera: Camera):
        super().__init__()
        self.CONST_MEDIA_SERVER_HOST = CONST_MEDIA_SERVER_HOST
        self._thread_activate = False
        self._stream_size = STREAM_SIZE
        self._camera_url = ""
        self._index = 0
        self.queue_stream = queue_stream
        self.__camera = camera
        self.__previous_rtmp = ""
        self.__ffmpeg_process: subprocess.Popen
        self.link_rtmp = ""

    def __set_args(self, rtmp_link):
        w, h = self._stream_size[0], self._stream_size[1]
        return (
            "ffmpeg -r 10 -re -stream_loop -1 -f rawvideo -vcodec rawvideo -pix_fmt "
            f"rgb24 -s {w}x{h} -i pipe:0 -pix_fmt yuv420p -c:v libx264 -preset veryfast -tune zerolatency -b:v 2048k "
            f"-f flv -flvflags no_duration_filesize {rtmp_link} -loglevel quiet "
        ).split()

    def __create_process(self, rtmp):
        args = self.__set_args(rtmp)
        return subprocess.Popen(args, stdin=subprocess.PIPE)

    def __create_uri_encode(self):
        return f"SVS_{self.__camera.id_company}/{self.__camera.area_code}$${self.__camera.code}.flv"

    def __create_rtmp_link(self):
        uri_encode = self.__create_uri_encode()
        return f"{self.CONST_MEDIA_SERVER_HOST}/{uri_encode}" 

    def run(self):
        print("start stream")
        self._thread_activate = True
        rtmp_link = self.__create_rtmp_link()
        print("Starting rtmp stream with rtmp: ", rtmp_link)
        self.__ffmpeg_process = self.__create_process(rtmp_link)
        self.__previous_rtmp = rtmp_link
        self.link_rtmp = rtmp_link
        while self._thread_activate:
            if self.queue_stream.empty():
                self.msleep(1)
                continue
            frame = self.queue_stream.get()
            try:
                frame = cv2.resize(frame, (self._stream_size[0], self._stream_size[1]))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                new_rtmp = self.__create_rtmp_link()
                if new_rtmp != self.__previous_rtmp:
                    self.__ffmpeg_process.stdin.close()
                    self.__ffmpeg_process.wait()
                    self.__ffmpeg_process = self.__create_process(new_rtmp)
                    self.__previous_rtmp = new_rtmp
                    self.link_rtmp = new_rtmp
                    continue
                self.__ffmpeg_process.stdin.write(frame.tobytes())
            except Exception as e:
                print(e)
                self.__ffmpeg_process.stdin.close()
                self.__ffmpeg_process.wait()
                self.__ffmpeg_process = self.__create_process(rtmp_link)

            self.msleep(1)

        self.__ffmpeg_process.stdin.close()
        self.__ffmpeg_process.wait()

    def stop(self):
        self._thread_activate = False

