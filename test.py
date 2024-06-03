import os
import json

def read_json_data(fp):
    assert os.path.isfile(fp), "{} is not a file".format(fp)
    with open(fp, mode='r', encoding='utf-8') as f:
        dt = json.load(f)
        return dt

def write_json_data(fp, json_data:str):
    with open(fp, mode='w', encoding='utf8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)


data = read_json_data(r"/mnt/atin/vinhVT/tam-chuc-counting/resources/data/http_link.json")
print(data)
host = "192.1168.1.1"
port = 8080
data["1"] = [host, port]
write_json_data(r"/mnt/atin/vinhVT/tam-chuc-counting/resources/data/http_link.json", data)