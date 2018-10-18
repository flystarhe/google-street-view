from streetview import download

root = ""
api_key = ""
signature = ""

locations = []
for lat in range(1, 2, 0.004492):
    for lon in range(1, 2, 0.029119):
        locations.append("{:.6f},{:.6f}".format(lat, lon))

for i in [0, 90, 180, 270]:
    download("{}_{}".format(root, i), api_key, signature, locations, size="600x400", heading=str(i))
