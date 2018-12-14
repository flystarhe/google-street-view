import requests
from urllib.parse import urlencode


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
    # (30.488286, 30.7620646), (103.921107, 104.2523822)
    api_key = "AIzaSyCw5exiqqFXVSQoNEdf4M43Jr0LlLcL4zY"
    print(get_location(language="zh-CN", key=api_key, address="中国四川省成都市龙泉驿区天平村")["results"][0])
    print(get_address(language="zh-CN", key=api_key, latlng="30.6488945,104.2523822")["results"][0])
    print(get_location(language="zh-CN", key=api_key, address="中国四川省成都市双流县麓山大道一段17号")["results"][0])
    print(get_address(language="zh-CN", key=api_key, latlng="30.488286,104.06852")["results"][0])
    print(get_location(language="zh-CN", key=api_key, address="中国四川省成都市青羊区文家场正街184号")["results"][0])
    print(get_address(language="zh-CN", key=api_key, latlng="30.697548,103.921107")["results"][0])
    print(get_location(language="zh-CN", key=api_key, address="中国四川省成都市金牛区北星大道一段")["results"][0])
    print(get_address(language="zh-CN", key=api_key, latlng="30.7620646,104.0758888")["results"][0])
