import sys
import numpy as np
from streetview import download

root = "images"
api_key = "AIzaSyACXZbBQQRqKxQ7o6MHQR9PGH8iPqDsjkg"
signature = sys.argv[1]

locations = []
for lat in np.arange(30.488286, 30.6943841, 0.0008983):
    for lon in np.arange(103.9774526, 104.2271417, 0.0058237):
        locations.append("{:.6f},{:.6f}".format(lat, lon))

for i in [0, 90, 180, 270]:
    download("{}_{}".format(root, i), api_key, signature, locations, size="600x400", heading=str(i))
