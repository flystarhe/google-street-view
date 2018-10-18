import requests
from urllib.parse import urlencode

"""
R=6378.137
import math
import numpy as np
"lat: {:.6f} about 1 km, lon: {:.6f} about 1 km".format(1/(R*np.pi/180), 1/(R*np.pi/180*math.cos(30)))
## 'lat: 0.008983 about 1 km, lon: 0.058237 about 1 km'
## lat step: 0.004492 about 500 m
## lon step: 0.029119 about 500 m
## lat range: @google
## lon range: @google
"""


def get_address(**kwargs):
    parameters = urlencode(kwargs)
    url = "https://maps.googleapis.com/maps/api/geocode/json?" + parameters
    res = requests.get(url)
    return res.json()


def get_location(**kwargs):
    parameters = urlencode(kwargs)
    url = "https://maps.googleapis.com/maps/api/geocode/json?" + parameters
    res = requests.get(url)
    return res.json()


if __name__ == "__main__":
    api_key = ""
    signature = ""
    print(get_address(language="zh-CN", key=api_key, signature=signature, latlng="40.714224,-73.961452"))
    print(get_location(language="zh-CN", key=api_key, signature=signature, address="中国四川省成都市龙泉驿区胜利路29"))
    ("四川省成都市龙泉驿区胜利路29", "四川省成都市天府新区麓山大道一段17号", "武侯区双星大道北一段武青北路9号", "四川省成都市金牛区站东路1号")
