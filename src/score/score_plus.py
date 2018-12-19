import os
import codecs
import numpy as np
import pandas as pd
from tqdm import tqdm
from trueskill import Rating, rate_1vs1

"""
TrueSkill

https://trueskill.org/
"""


def make_score_file(votes_file, label="safety", output_dir="tmps"):
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
            images[left] = Rating()

        if right not in images:
            images[right] = Rating()

        if winner == "left":
            r1 = images[left]
            r2 = images[right]
            new_r1, new_r2 = rate_1vs1(r1, r2)
            images[left] = new_r1
            images[right] = new_r2
        elif winner == "right":
            r1 = images[right]
            r2 = images[left]
            new_r1, new_r2 = rate_1vs1(r1, r2)
            images[right] = new_r1
            images[left] = new_r2
        elif winner == "equal":
            r1 = images[right]
            r2 = images[left]
            new_r1, new_r2 = rate_1vs1(r1, r2, drawn=True)
            images[right] = new_r1
            images[left] = new_r2

    max_mu = np.max([r.mu for uid, r in images.items()])
    res = ["{} {:.2f}".format(uid, r.mu / max_mu) for uid, r in images.items()]

    file_path = os.path.join(output_dir, "score_plus_{}.txt".format(label))
    with codecs.open(file_path, "w", "utf-8") as writer:
        writer.write("\n".join(res))
    return file_path, max_mu


if __name__ == "__main__":
    label_list = "safety,beautiful,lively,wealthy,boring,depressing".split(",")
    votes_file = "/data/votes.csv"
    output_dir = "."

    for label in label_list:
        print(make_score_file(votes_file, label, output_dir))

    for label in label_list:
        txt = os.path.join(output_dir, "score_plus_{}.txt".format(label))

        data = []
        with open(txt) as file:
            for line in file:
                line = line.strip()
                if line:
                    data.append(line.split()[-1])

        data = np.float32(data)
        print(label, len(data), data.min(), data.max())
