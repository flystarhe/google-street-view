import os
import codecs
import random


def split_dataset(file_path, shuffle=True):
    data = []
    with open(file_path) as file:
        for line in file:
            line = line.strip()
            if line:
                data.append(line)

    if shuffle:
        random.shuffle(data)

    root = os.path.dirname(file_path)
    root = os.path.realpath(root)

    pos = int(len(data) * 0.2)

    file_path = os.path.join(root, "dataset_val.txt")
    with codecs.open(file_path, "w", "utf-8") as writer:
        writer.write("\n".join(data[:pos]))

    file_path = os.path.join(root, "dataset_train.txt")
    with codecs.open(file_path, "w", "utf-8") as writer:
        writer.write("\n".join(data[pos:]))

    return len(data), pos
