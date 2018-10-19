import sys
import numpy as np
from streetview import download as download

locations = []
for lat in np.arange(30.488286, 30.7620646, 0.0008983):
    for lng in np.arange(103.924021, 104.2523822, 0.0058237):
        locations.append("{:.6f},{:.6f}".format(lat, lng))
print("locations size:", len(locations))

root = sys.argv[1] if len(sys.argv) > 1 else "downloads"
api_key = "AIzaSyCw5exiqqFXVSQoNEdf4M43Jr0LlLcL4zY"
secret = "Hkk3M1Z8gyEQ17YPwi5iit-ZHI0="

download("{}_{}".format(root, "x"), locations, api_key, secret, size="600x400", radius="50")
for x in range(0, 360, 45):
    download("{}_{}".format(root, x), locations, api_key, secret, size="600x400", radius="50", heading=str(x))
