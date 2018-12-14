import os
import math
import codecs
import pandas as pd
from tqdm import tqdm

"""
TrueSkill:

- https://trueskill.org
- http://www.cnblogs.com/baiting/p/5591614.html
"""


def fastupdate(mw, sw, ml, sl, beta):
    # miu and sigma of winner and loser
    sw2 = math.pow(sw, 2)
    sl2 = math.pow(sl, 2)
    t = mw - ml
    c = math.sqrt(34.72222 + sw2 + sl2)
    c2 = math.pow(c, 2)
    tc = t / c
    vtc = 0.79788 * 0.60653 ** math.pow(tc, 2) / math.erfc(-0.70711 * tc)
    wtc = vtc * (vtc + tc)
    mw += vtc * sw2 / c
    ml -= vtc * sl2 / c
    sw *= math.sqrt(1 - wtc * sw2 / c2)
    sl *= math.sqrt(1 - wtc * sl2 / c2)
    return mw, sw, ml, sl


class Role:
    def __init__(self, mu=25, sigma=25 / 3):
        self.mu = mu
        self.sigma = sigma

    def defeat(self, other, beta=25 / 3):
        mw, sw, ml, sl = fastupdate(self.mu, self.sigma, other.mu, other.sigma, beta)
        self.mu, self.sigma = mw, sw
        other.mu, other.sigma = ml, sl


def main(votes_file, label="safety", output_dir="tmps"):
    output_dir = os.path.realpath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    images = dict()
    for idx, row in tqdm(pd.read_csv(votes_file).iterrows()):
        if row["category"] != label:
            continue
        left = row["left_id"]
        right = row["right_id"]
        winner = row["winner"]
        if left not in images:
            images[left] = Role()
        if right not in images:
            images[right] = Role()
        if winner == "left":
            images[left].defeat(images[right])
        elif winner == "right":
            images[right].defeat(images[left])

    ms = 10000
    Ms = -10000
    for k, v in images.items():
        Ms = max(Ms, v.mu)
        ms = min(ms, v.mu)

    file_path = os.path.join(output_dir, "scores_{}.txt".format(label))
    with codecs.open(file_path, "w", "utf-8") as writer:
        for k, v in images.items():
            writer.write("{} {}\n".format(k, 10 * (v.mu - ms) / Ms))
    return file_path


if __name__ == "__main__":
    votes_file = "/data/votes.csv"
    for label in "safety,beautiful,lively,wealthy,boring,depressing".split(","):
        print(main(votes_file, label=label, output_dir="."))
