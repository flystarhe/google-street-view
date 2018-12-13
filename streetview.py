import os
import sys
import json
import time
import codecs
import requests
from urllib.parse import urlencode
from urllib.request import urlretrieve

# from PIL import Image
# from io import BytesIO
# response = requests.get(url)
# image = Image.open(BytesIO(response.content))
# suffix = response.headers["Content-Type"].split("/")[-1]
# image.save("{}.{}".format(time.strftime("%m%d%H%M%S"), suffix.lower()))

import hmac
import base64
import hashlib
from urllib.parse import urlparse


def sign_url(url, secret=None):
    if secret is None or secret == "":
        return url
    url = urlparse(url)
    # We only need to sign the path+query part of the string
    url_to_sign = url.path + "?" + url.query
    # Decode the private key into its binary format
    # We need to decode the URL-encoded private key
    decoded_key = base64.urlsafe_b64decode(secret)
    # Create a signature using the private key and the URL-encoded
    # string using HMAC SHA1. This signature will be binary.
    signature = hmac.new(decoded_key, url_to_sign.encode("utf8"), hashlib.sha1)
    # Encode the binary signature into base64 for use within a URL
    encoded_signature = base64.urlsafe_b64encode(signature.digest())
    original_url = url.scheme + "://" + url.netloc + url.path + "?" + url.query
    # Return signed URL
    return original_url + "&signature=" + encoded_signature.decode("utf8")


def save_logs(logs, log_file):
    with codecs.open(log_file, "w", "utf-8") as writer:
        counta = len([True for i in logs if i.startswith(":")])
        countb = len([True for i in logs if i.startswith("!")])
        countc = len([True for i in logs if i.startswith("?")])
        writer.write(time.strftime("#%Y-%m-%d %H:%M:%S [{}/{}/{}]\n".format(counta, countb, countc)))
        writer.write("\n".join(logs))
        writer.write("\n")
    return log_file


def request_metadata(secret, **kwargs):
    parameters = urlencode(kwargs)
    url = sign_url("https://maps.googleapis.com/maps/api/streetview/metadata?" + parameters, secret)
    res = requests.get(url)
    return res.json()


def request_imagery(root, secret, **kwargs):
    parameters = urlencode(kwargs)
    tag = kwargs["location"] if "location" in kwargs else kwargs["pano"]
    url = sign_url("https://maps.googleapis.com/maps/api/streetview?" + parameters, secret)
    res = urlretrieve(url, "{}/{},{}".format(root, tag, time.strftime("%m%d%H%M%S.jpg")))
    return os.path.abspath(res[0])


def download(root, locations, api_key, secret, **kwargs):
    """
    size: "600x400", fov: "90", pitch: "0", radius: "50", heading: "0"
    """
    logs = []
    total = len(locations)
    os.makedirs(root, exist_ok=True)
    for location in locations:
        if "pano" in kwargs:
            kwargs.pop("pano")
        kwargs["location"] = location
        res = request_metadata(key=api_key, secret=secret, **kwargs)
        if res["status"] == "OK":
            try:
                if "location" in kwargs:
                    kwargs.pop("location")
                kwargs["pano"] = res["pano_id"]
                res["image_path"] = request_imagery(root, key=api_key, secret=secret, **kwargs)
                logs.append(":{}".format(json.dumps(res)))
            except Exception as err:
                res["err"] = str(err)
                logs.append("!{}".format(json.dumps(res)))
        else:
            res["query_params"] = {"location": location}
            logs.append("?{}".format(json.dumps(res)))
        pos = len(logs)
        if pos % 1000 == 0:
            print("[{}] download of {:.2f}%".format(time.strftime("%m%d %H:%M:%S"), pos / total))
    return save_logs(logs, "{}/0000".format(root))


def download1(root, locations, api_key, secret, **kwargs):
    """
    size: "600x400", fov: "90", pitch: "0", radius: "50", heading: "0"
    """
    logs = []
    total = len(locations)
    os.makedirs(root, exist_ok=True)
    for location in locations:
        res = {"location": location}
        try:
            kwargs["location"] = location
            res["image_path"] = request_imagery(root, key=api_key, secret=secret, **kwargs)
            logs.append(":{}".format(json.dumps(res)))
        except Exception as err:
            res["err"] = str(err)
            logs.append("!{}".format(json.dumps(res)))
        pos = len(logs)
        if pos % 1000 == 0:
            print("[{}] download of {:.2f}%".format(time.strftime("%m%d %H:%M:%S"), pos / total))
    return save_logs(logs, "{}/0000".format(root))


def download2(root, locations, api_key, secret, **kwargs):
    """
    size: "600x400", fov: "90", pitch: "0", radius: "50", heading: "0"
    """
    logs = []
    total = len(locations)
    os.makedirs(root, exist_ok=True)
    for location in locations:
        try:
            kwargs["pano"] = location["pano_id"]
            location["image_path"] = request_imagery(root, key=api_key, secret=secret, **kwargs)
            logs.append(":{}".format(json.dumps(location)))
        except Exception as err:
            location["err"] = str(err)
            logs.append("!{}".format(json.dumps(location)))
        pos = len(logs)
        if pos % 100 == 0:
            print("[{}] download of {:.2f}%".format(time.strftime("%m%d %H:%M:%S"), pos / total))
    return save_logs(logs, "{}/0000".format(root))


def download3(root, locations, api_key, secret, **kwargs):
    """
    size: "600x400", fov: "90", pitch: "0", radius: "50", heading: "0"
    """
    logs = []
    total = len(locations)
    os.makedirs(root, exist_ok=True)
    for location in locations:
        try:
            kwargs["location"] = "{:.6f},{:.6f}".format(location["location"]["lat"], location["location"]["lng"])
            location["image_path"] = request_imagery(root, key=api_key, secret=secret, **kwargs)
            logs.append(":{}".format(json.dumps(location)))
        except Exception as err:
            location["err"] = str(err)
            logs.append("!{}".format(json.dumps(location)))
        pos = len(logs)
        if pos % 100 == 0:
            print("[{}] download of {:.2f}%".format(time.strftime("%m%d %H:%M:%S"), pos / total))
    return save_logs(logs, "{}/0000".format(root))


if __name__ == "__main__":
    locations = [sys.argv[1] if len(sys.argv) == 2 else "30.657054,104.065665"]
    api_key = "AIzaSyCw5exiqqFXVSQoNEdf4M43Jr0LlLcL4zY"
    secret = "Hkk3M1Z8gyEQ17YPwi5iit-ZHI0="
    print(download("images", locations, api_key, secret, size="600x400", radius="500", heading="0"))
