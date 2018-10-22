import sys
import time
import math
import json
import codecs
import functools
import multiprocessing
import numpy as np
from streetview import request_metadata


def get_metadata(api_key, secret, location):
    res = request_metadata(key=api_key, secret=secret, location=location)
    res["query_params"] = {"location": location}
    if res["status"] == "OK":
        return ":{}".format(json.dumps(res))
    return "!{}".format(json.dumps(res))


def get_locations(lat1, lat2, lng1, lng2, step=1000):
    locations = []
    R = 6377.830 * 1000
    lat_step = 1 / (R * np.pi / 180) * step
    for lat in np.arange(lat1, lat2, lat_step):
        lng_step = 1 / (R * np.pi / 180 * math.cos(lat)) * step
        for lng in np.arange(lng1, lng2, lng_step):
            locations.append("{:.6f},{:.6f}".format(lat, lng))
    return locations


def get_locations_pano(api_key, secret, locations):
    func = functools.partial(get_metadata, api_key, secret)
    with multiprocessing.Pool(processes=16) as pool:
        result = pool.map(func, locations)
    return result


def save_logs(logs, log_file):
    with codecs.open(log_file, "w", "utf-8") as writer:
        counta = len([True for i in logs if i.startswith(":")])
        countb = len([True for i in logs if i.startswith("!")])
        countc = len([True for i in logs if i.startswith("?")])
        writer.write(time.strftime("#%Y-%m-%d %H:%M:%S [{}/{}/{}]\n".format(counta, countb, countc)))
        writer.write("\n".join(logs))
        writer.write("\n")
    return log_file


if __name__ == "__main__":
    api_key = "AIzaSyCw5exiqqFXVSQoNEdf4M43Jr0LlLcL4zY"
    secret = "Hkk3M1Z8gyEQ17YPwi5iit-ZHI0="
    lat1 = 30.488286
    lat2 = 30.7620646
    lng1 = 103.921107
    lng2 = 104.2523822
    step = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    print(time.strftime("#%Y-%m-%d %H:%M:%S"))
    locations = get_locations(lat1, lat2, lng1, lng2, step)
    print(time.strftime("#%Y-%m-%d %H:%M:%S"))
    logs = get_locations_pano(api_key, secret, locations)
    print(time.strftime("#%Y-%m-%d %H:%M:%S"))
    print(save_logs(logs, "logs.locations.{}".format(step)))
