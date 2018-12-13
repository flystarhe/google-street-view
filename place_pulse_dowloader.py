import sys
import json
import time
import pandas as pd
from tool import Logger
from streetview import request_metadata, request_imagery

"""
http://pulse.media.mit.edu/data/

Place Pulse 2.0: A Global Map

Download images
"""
csv_file = "/data2/tmps/src/data_set_without_pictures/votes.csv"


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
    for key, location in locations.items():
        kwargs["location"] = location
        res = request_metadata(key=api_key, secret=secret, **kwargs)
        if res["status"] == "OK":
            try:
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
    name = sys.argv[2] if len(sys.argv) > 2 else "log.imgs"
    logger = Logger(root, name)
    api_key = "AIzaSyCw5exiqqFXVSQoNEdf4M43Jr0LlLcL4zY"
    secret = "Hkk3M1Z8gyEQ17YPwi5iit-ZHI0="
    print(download_images(root, logger, csv_file, api_key, secret, size="400x300"))
