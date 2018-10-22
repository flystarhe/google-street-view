import sys
import time
import json
import codecs
from tool import seq_unique
from streetview import download3 as download

log_file = "logs.locations.100"
with codecs.open(log_file, "r", "utf-8") as readers:
    logs = [line for line in readers.readlines() if line.startswith(":")]
    locations = [json.loads(line[1:]) for line in logs]
locations = seq_unique(locations, "pano_id")
print("#locations:", len(locations))

root = sys.argv[1] if len(sys.argv) > 1 else "images"
api_key = "AIzaSyCw5exiqqFXVSQoNEdf4M43Jr0LlLcL4zY"
secret = "Hkk3M1Z8gyEQ17YPwi5iit-ZHI0="

print(time.strftime("#%Y-%m-%d %H:%M:%S"))
if len(sys.argv) > 2:
    x = sys.argv[2]
    download("{}/{}".format(root, x), locations, api_key, secret, size="600x400", radius="50", heading=x)
else:
    x = "x"
    download("{}/{}".format(root, x), locations, api_key, secret, size="600x400", radius="50")
print(time.strftime("#%Y-%m-%d %H:%M:%S"))
