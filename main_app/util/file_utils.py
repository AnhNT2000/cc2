import json
import os
import numpy as np
import subprocess
import yaml


def read_yaml_file(path):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return data

def write_yaml_file(path, data):
    with open(path, "w") as f:
        yaml.dump(data, f)

def create_folder_on_another_computer(path:str):
    if os.path.exists(path):
        return
    try:
        os.mkdir(path)
    except OSError:
        subprocess.call('net use {} /user:{} {}'.format(path, "www", 'Atin12345'), shell=True)
        create_folder_on_another_computer(path)
        
def create_folder(path:str):
    if os.path.exists(path):
        return
    os.mkdir(path)

def read_json_data(fp):
    assert os.path.isfile(fp), "{} is not a file".format(fp)
    with open(fp, mode='r', encoding='utf-8') as f:
        dt = json.load(f)
        return dt

def write_json_data(fp, json_data:str):
    with open(fp, mode='w', encoding='utf8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

def update_json_data(fp,camera_id, host, port):
    data = read_json_data(fp)
    data[camera_id] = [host, port]
    write_json_data(fp, data)
        
def convert_2_point_to_4_point(polygon):
    x1, y1, x2, y2 = polygon[0]
    points = np.array([[x1, y1], [x1, y2], [x2, y2], [x2, y1]], dtype=np.int32)
    points = points.reshape((-1, 1, 2))
    return points

     



