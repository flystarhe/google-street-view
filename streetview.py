import os
import json
import time
import codecs
import requests
# from PIL import Image
# from io import BytesIO
from urllib.parse import urlencode
from urllib.request import urlretrieve


# response = requests.get(url)
# image = Image.open(BytesIO(response.content))
# suffix = response.headers["Content-Type"].split("/")[-1]
# image.save("{}.{}".format(time.strftime("%m%d%H%M%S"), suffix.lower()))


def save_logs(logs, log_file):
    with codecs.open(log_file, "w", "utf-8") as writer:
        writer.write("\n".join(logs))
    return log_file


def request_metadata(signature, **kwargs):
    parameters = urlencode(kwargs)
    url = "https://maps.googleapis.com/maps/api/streetview/metadata?" + parameters
    res = requests.get(url)
    return res.json()


def request_imagery(root, signature, **kwargs):
    parameters = urlencode(kwargs)
    url = "https://maps.googleapis.com/maps/api/streetview?" + parameters
    res = urlretrieve(url, "{}/{},{}".format(root, kwargs["location"], time.strftime("%m%d%H%M%S.jpg")))
    return res[0]


def download(root, api_key, signature, locations, **kwargs):
    """
    size: "600x400"
    fov: "90"
    pitch: "0"
    radius: "50"
    heading: "0"
    """
    logs = []
    os.makedirs(root, exist_ok=True)
    try:
        total = len(locations)
        for location in locations:
            res = request_metadata(key=api_key, signature=signature, location=location)
            if res["status"] == "OK":
                name = request_imagery(root, key=api_key, signature=signature, location=location, **kwargs)
                logs.append(":[{}],{}".format(name, json.dumps(res)))
            else:
                logs.append("![{}],{}".format(location, json.dumps(res)))
            pos = len(logs)
            if pos % 1000 == 0:
                print(">> download {:06d}, of {:.2f}%".format(pos, pos / total))
    except Exception as err:
        logs.append("?[{}]".format(str(err)))
    return save_logs(logs, "{}/logs.{}".format(root, time.strftime("%m%d%.H%M%S")))


if __name__ == "__main__":
    api_key = "AIzaSyACXZbBQQRqKxQ7o6MHQR9PGH8iPqDsjkg"
    signature = ""
    locations = ["{:.6f},{:.6f}".format(46.414382, 10.013988)]
    print(download("images", api_key, signature, locations, size="800x600", heading="0"))
    print(download("images", api_key, signature, locations, size="800x600", heading="90"))
