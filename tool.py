import sys
import json
import codecs
import numpy as np
from streetview import request_metadata


def get_locations(api_key, secret, lat1, lat2, lng1, lng2, lat_step=0.0008983, lng_step=0.0058237):
    locations = []
    for lat in np.arange(lat1, lat2, lat_step):
        for lng in np.arange(lng1, lng2, lng_step):
            location = "{:.6f},{:.6f}".format(lat, lng)
            res = request_metadata(key=api_key, secret=secret, location=location)
            if res["status"] == "OK":
                res["query_params"] = {"location": location}
                locations.append(":{}".format(json.dumps(res)))
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
    pass
