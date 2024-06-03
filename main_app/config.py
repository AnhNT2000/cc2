import os
from os.path import dirname
import yaml


ROOT = dirname(dirname(os.path.abspath(__file__))) # pointer to outside of virtual_fence module

CONFIG_PATH = os.path.join(ROOT, "resources", "config", "config.yaml")

def read_yaml_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data

CONFIG_DATA = read_yaml_file(CONFIG_PATH)

TIME_LIVE = CONFIG_DATA["TIME_LIVE"]  # seconds
STD = CONFIG_DATA["STD"] # độ lệch chuẩn

TIME_LIVE: 1
LENGTH_LOCATION = CONFIG_DATA["LENGTH_LOCATION"] # độ dài của list lưu trữ
LENGTH_CENTER = CONFIG_DATA["LENGTH_CENTER"] # độ dài của list lưu trữ
TIME_OUT = CONFIG_DATA["TIME_OUT"] # thời gian chờ để xác định hướng

TIME_SENT_COUNT = CONFIG_DATA["TIME_SENT_COUNT"]

TIME_SEND_TOTAL_COUNT = CONFIG_DATA["TIME_SEND_TOTAL_COUNT"]

MODE_HALF = CONFIG_DATA["MODE_HALF"]


# config web

USER_NAME = CONFIG_DATA["USER_NAME"]
PASSWORD = CONFIG_DATA["PASSWORD"]
STREAM_SIZE = CONFIG_DATA["STREAM_SIZE"]

WEB_HOST = CONFIG_DATA["WEB_HOST"]
SERVER_NAME = CONFIG_DATA["SERVER_NAME"]
CONST_COMP_ID = CONFIG_DATA["CONST_COMP_ID"]
CONST_MEDIA_SERVER_HOST = CONFIG_DATA["CONST_MEDIA_SERVER_HOST"]
WEB_HOST_POLYGON = CONFIG_DATA["WEB_HOST_POLYGON"]
EXCEPTION_CAMERA = CONFIG_DATA["EXCEPTION_CAMERA"]
EXCEPTION_CAMERA_DIR_X = CONFIG_DATA["EXCEPTION_CAMERA_DIR_X"]

