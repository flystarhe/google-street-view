import sys
import numpy as np
from streetview import download

locations = []
for lat in np.arange(30.488286, 30.6943841, 0.0008983):
    for lon in np.arange(103.9774526, 104.2271417, 0.0058237):
        locations.append("{:.6f},{:.6f}".format(lat, lon))

root = "images"
api_key = "AIzaSyACXZbBQQRqKxQ7o6MHQR9PGH8iPqDsjkg"
secret = sys.argv[1] if len(sys.argv) == 2 else None
for i in [0, 90, 180, 270]:
    download("{}_{}".format(root, i), locations, api_key, secret, size="600x400", heading=str(i))
