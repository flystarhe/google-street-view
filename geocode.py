import requests
from urllib.parse import urlencode

"""
R=6378.137
import math
import numpy as np
"lat: {:.6f} about 1 km, lng: {:.6f} about 1 km".format(1/(R*np.pi/180), 1/(R*np.pi/180*math.cos(30)))
## 'lat: 0.008983 about 1 km, lng: 0.058237 about 1 km'
## lat step: 0.004492 about 500 m
## lng step: 0.029119 about 500 m
## lat range: @google
## lng range: @google
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
    # (30.488286, 30.7620646), (103.924021, 104.2523822)
    api_key = "AIzaSyCw5exiqqFXVSQoNEdf4M43Jr0LlLcL4zY"
    print(get_location(language="zh-CN", key=api_key, address="中国成都市龙泉驿区天平村")["results"][0])
    print(get_address(language="zh-CN", key=api_key, latlng="30.6488945,104.2523822")["results"][0])
    print(get_location(language="zh-CN", key=api_key, address="中国四川省成都市双流县麓山大道一段17号")["results"][0])
    print(get_address(language="zh-CN", key=api_key, latlng="30.488286,104.06852")["results"][0])
    print(get_location(language="zh-CN", key=api_key, address="中国四川省成都市青羊区文家正街227号")["results"][0])
    print(get_address(language="zh-CN", key=api_key, latlng="30.6907126,103.924021")["results"][0])
    print(get_location(language="zh-CN", key=api_key, address="中国四川省成都市新都区北星大道一段")["results"][0])
    print(get_address(language="zh-CN", key=api_key, latlng="30.7620646,104.0758888")["results"][0])
