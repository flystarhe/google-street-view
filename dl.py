import os
import json
import time
import codecs
import random
import requests
from PIL import Image
from io import BytesIO
from urllib.parse import urlencode
from urllib.request import urlretrieve


def save_logs(logs, file_path=None):
    if file_path is None:
        file_path = "logs/{}".format(time.strftime("%m%d.%H%M%S"))
    with codecs.open(file_path, "w", "utf-8") as writer:
        writer.write("\n".join(logs))
    return file_path


def request_metadata(**kwargs):
    parameters = urlencode(kwargs)
    url = "https://maps.googleapis.com/maps/api/streetview/metadata?"
    res = requests.get(url + parameters)
    return res.json()


def request_imagery(**kwargs):
    #response = requests.get(url + parameters)
    #image = Image.open(BytesIO(response.content))
    #suffix = response.headers["Content-Type"].split("/")[-1]
    #image.save("{}.{}".format(kwargs["location"], suffix))
    parameters = urlencode(kwargs)
    url = "https://maps.googleapis.com/maps/api/streetview?"
    res = urlretrieve(url + parameters, "images/{},{}".format(kwargs["location"], time.strftime("%m%d%H%M%S.jpg")))
    return res[0]


def main(locations, api_keys, log_file=None, kwargs={"size":"400x400", "heading":"0", "fov":"90", "pitch":"0", "radius":"50"}):
    os.makedirs("images", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    logs = []
    api_key = random.choice(api_keys)
    try:
        for location in locations:
            while True:
                res = request_metadata(key=api_key, location=location)
                if res["status"] == "REQUEST_DENIED":
                    api_keys.remove(api_key)
                    api_key = random.choice(api_keys)
                elif res["status"] == "OVER_QUERY_LIMIT":
                    api_key = random.choice(api_keys)
                elif res["status"] == "UNKNOWN_ERROR":
                    continue
                else:
                    break
            if res["status"] == "OK":
                name = request_imagery(location=location, key=api_key, **kwargs)
                logs.append(":[{}],{}".format(name, json.dumps(res)))
            else:
                logs.append("![{}],{}".format(location, res["status"]))
            print(res)
    except Exception as err:
        logs.append(str(err))
    return save_logs(logs, log_file), api_keys


if __name__ == "__main__":
    api_keys = ['AIzaSyCTmknsR-_37_vewUFVNkQGnyaNDrYgf1M', 'AIzaSyDHIA8eWXDVkV9b-S19Yb9KxZWVr9c4HrU', 'AIzaSyBuJUlt9rO00c_X3-kdNe2103T6nIXNiqM', 'AIzaSyBcNb4sGU0lYyGLgkI8z5ZXtJhLmuLuXCU', 'AIzaSyBkab-vITkWMnuzINdvGpE_mj-RoNXvocc', 'AIzaSyDO-m0_wded_rnirygrSq_laCD7brWcTL0', 'AIzaSyBh8zm6ncRxzISVtgt4X7NuPrdXT95_QU8', 'AIzaSyAasUQSKuaQaqwWdFQUAEJuwILLOCawDMY', 'AIzaSyCOfN5Tv-qcFGsvn23O4M7KkmysDUXxAU8', 'AIzaSyCqhfGgU-dSdNLShQNu00SVi6rMSFQMYIM', 'AIzaSyD325R23qW7PqEuAEM0nwn7IL7I_KXX0tA', 'AIzaSyD6gDl3Bl8WrCjxV0AN7coWHTPnh44wjzg', 'AIzaSyBSfx_5J034ZUWw522GQVnRoKpq8mr0HuY', 'AIzaSyBQ5YJg8avLmuyljyrMX5yjlhAk2_3wahs', 'AIzaSyBYM3oTYVr1ReaCLi_0BuI8ME0MmWpuUl0']
    locations = ["46.414382,10.013988"]
    print(main(locations, api_keys, None)[0])