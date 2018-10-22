import time
import json
import codecs
import numpy as np
from streetview import request_metadata


def get_locations(api_key, secret, lat1, lat2, lng1, lng2, lat_step, lng_step):
    locations = []
    start_time = time.time()
    for lat in np.arange(lat1, lat2, lat_step):
        for lng in np.arange(lng1, lng2, lng_step):
            location = "{:.6f},{:.6f}".format(lat, lng)
            res = request_metadata(key=api_key, secret=secret, location=location)
            if res["status"] == "OK":
                res["query_params"] = {"location": location}
                locations.append(":{}".format(json.dumps(res)))
            if int(time.time() - start_time) % 600 == 0:
                print("[{}]{:.4f}, {}".format(time.strftime("%H:%M"), (lat - lat1) / (lat2 - lat1), len(locations)))
    print("locations size:", len(locations))
    return locations


def save_logs(logs, log_file):
    with codecs.open(log_file, "w", "utf-8") as writer:
        counta = len([True for i in logs if i.startswith(":[")])
        countb = len([True for i in logs if i.startswith("![")])
        countc = len([True for i in logs if i.startswith("?[")])
        writer.write(time.strftime("#%Y-%m-%d %H:%M:%S [{}/{}/{}]\n".format(counta, countb, countc)))
        writer.write("\n".join(logs))
        writer.write("\n")
    return log_file


if __name__ == "__main__":
    api_key = "AIzaSyCw5exiqqFXVSQoNEdf4M43Jr0LlLcL4zY"
    secret = "Hkk3M1Z8gyEQ17YPwi5iit-ZHI0="
    lat1 = 30.488286
    lat2 = 30.7620646
    lng1 = 103.924021
    lng2 = 104.2523822
    lat_step = 0.00008983
    lng_step = 0.00058237
    logs = get_locations(api_key, secret, lat1, lat2, lng1, lng2, lat_step, lng_step)
    print(save_logs(logs, "logs.locations"))
