import os
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
    signature = hmac.new(decoded_key, url_to_sign, hashlib.sha1)
    # Encode the binary signature into base64 for use within a URL
    encoded_signature = base64.urlsafe_b64encode(signature.digest())
    original_url = url.scheme + "://" + url.netloc + url.path + "?" + url.query
    # Return signed URL
    return original_url + "&signature=" + encoded_signature


def save_logs(logs, log_file):
    with codecs.open(log_file, "w", "utf-8") as writer:
        writer.write("\n".join(logs))
    return log_file, len(logs)


def request_metadata(secret, **kwargs):
    parameters = urlencode(kwargs)
    url = sign_url("https://maps.googleapis.com/maps/api/streetview/metadata?" + parameters, secret)
    res = requests.get(url)
    return res.json()


def request_imagery(root, secret, **kwargs):
    parameters = urlencode(kwargs)
    url = sign_url("https://maps.googleapis.com/maps/api/streetview?" + parameters, secret)
    res = urlretrieve(url, "{}/{},{}".format(root, kwargs["location"], time.strftime("%m%d%H%M%S.jpg")))
    return res[0]


def download(root, locations, api_key, secret, **kwargs):
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
            res = request_metadata(key=api_key, secret=secret, location=location)
            if res["status"] == "OK":
                name = request_imagery(root, key=api_key, secret=secret, location=location, **kwargs)
                logs.append(":[{}],{}".format(name, json.dumps(res)))
            else:
                logs.append("![{}],{}".format(location, json.dumps(res)))
            pos = len(logs)
            if pos % 1000 == 0:
                print(">> download {:06d}, of {:.2f}%".format(pos, pos / total))
    except Exception as err:
        logs.append("?[{}]".format(str(err)))
    return save_logs(logs, "{}/logs{}".format(root, time.strftime("%m%d%H%M%S")))


if __name__ == "__main__":
    locations = ["{:.6f},{:.6f}".format(30.6457077, 104.2271417)]
    api_key = "AIzaSyACXZbBQQRqKxQ7o6MHQR9PGH8iPqDsjkg"
    secret = None
    print(download("images", locations, api_key, secret, size="600x400", heading="0"))
    print(download("images", locations, api_key, secret, size="600x400", heading="90"))
