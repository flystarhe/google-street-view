import sys
import json
import time
import pandas as pd
from src.tool import Logger
from src.streetview import request_metadata, request_imagery

"""
http://pulse.media.mit.edu/data/

Place Pulse 2.0: A Global Map

import os
import sys

mylibs = ["/data/place_pulse_downloader"]
os.chdir(mylibs[0])
for mylib in mylibs:
    if mylib not in sys.path:
        sys.path.insert(0, mylib)

from place_pulse_dowloader import *

root = "images_pulse"
logger = Logger(root, "log.imgs")
csv_file = "/data/votes.csv"
api_key = "AIzaSyCw5exiqqFXVSQoNEdf4M43Jr0LlLcL4zY"
secret = "Hkk3M1Z8gyEQ17YPwi5iit-ZHI0="
print(download_images(root, logger, csv_file, api_key, secret, size="400x300"))
"""


def load_votes(csv_file):
    votes = pd.read_csv(csv_file, encoding="utf-8")
    return votes


def load_locations(csv_file):
    res = dict()
    votes = load_votes(csv_file)
    for i, vote in votes.iterrows():
        for j in ["left", "right"]:
            key = vote[j + "_id"]
            if key not in res:
                res[key] = "{:.6f},{:.6f}".format(vote[j + "_lat"], vote[j + "_long"])
    return res


def download_images(root, logger, csv_file, api_key, secret, **kwargs):
    locations = load_locations(csv_file)
    logger.log("[{}] size: {}".format(time.strftime("%Y-%m-%d %H:%M:%S"), len(locations)))
    for i, (key, location) in enumerate(locations.items(), 1):
        if "pano" in kwargs:
            kwargs.pop("pano")
        kwargs["location"] = location
        res = request_metadata(key=api_key, secret=secret, **kwargs)
        res["log_id"] = key
        res["log_line_num"] = i
        res["location"] = location
        if res["status"] == "OK":
            try:
                if "location" in kwargs:
                    kwargs.pop("location")
                kwargs["pano"] = res["pano_id"]
                res["image_path"] = request_imagery(root, key=api_key, secret=secret, **kwargs)
                logger.log(":{}".format(json.dumps(res)))
            except Exception as err:
                res["err"] = str(err)
                logger.log("!{}".format(json.dumps(res)))
        else:
            res["query_params"] = {"location": location}
            logger.log("?{}".format(json.dumps(res)))
    logger.log("[{}] end.".format(time.strftime("%Y-%m-%d %H:%M:%S")))
    logger.save("a")
    return logger.path


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "images_pulse"
    logger = Logger(root, "log.imgs")
    csv_file = "/data/votes.csv"
    api_key = "AIzaSyCw5exiqqFXVSQoNEdf4M43Jr0LlLcL4zY"
    secret = "Hkk3M1Z8gyEQ17YPwi5iit-ZHI0="
    print(download_images(root, logger, csv_file, api_key, secret, size="400x300"))
