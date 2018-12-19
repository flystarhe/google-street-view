import os
import codecs
import random
import numpy as np
from PIL import Image
import torchvision.transforms as transforms


def make_score_file(score_path, labels=None):
    if labels is None:
        labels = ["beautiful", "boring", "depressing", "lively", "safety", "wealthy"]

    scores = {}
    for label in labels:
        score_file = os.path.join(score_path, "score_plus_{}.txt".format(label))
        with open(score_file) as file:
            for line in file:
                line = line.strip()
                if line:
                    uid, val = line.split()
                    scores.setdefault(uid, []).append(val)

    data = []
    val_size = len(labels)
    for uid in sorted(scores.keys()):
        val = scores[uid]
        if len(val) == val_size:
            data.append("{} {}".format(uid, " ".join(val)))

    file_path = os.path.join(score_path, "score_plus.txt")
    with codecs.open(file_path, "w", "utf-8") as writer:
        writer.write("\n".join(data))
    return file_path


def get_transform(mode="test"):
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    if mode == "train":
        return transforms.Compose(
            [transforms.Resize(256), transforms.RandomCrop(256), transforms.RandomHorizontalFlip(),
             transforms.ToTensor(), normalize])
    else:
        return transforms.Compose(
            [transforms.Resize(256), transforms.CenterCrop(256), transforms.ToTensor(), normalize])


def split_dataset(file_path, shuffle=True, keep=False):
    data = []
    with open(file_path) as file:
        for line in file:
            line = line.strip()
            if line:
                data.append(line)

    if shuffle:
        random.shuffle(data)

    pos = int(len(data) * 0.2)
    print("data size: {}, split pos: {}".format(len(data), pos))

    if keep:
        root = os.path.dirname(file_path)
        root = os.path.realpath(root)

        val_file = os.path.join(root, "dataset_val.txt")
        with codecs.open(val_file, "w", "utf-8") as writer:
            writer.write("\n".join(data[:pos]))

        train_file = os.path.join(root, "dataset_train.txt")
        with codecs.open(train_file, "w", "utf-8") as writer:
            writer.write("\n".join(data[pos:]))

        return val_file, train_file
    else:
        return data[:pos], data[pos:]


def get_dataset(dataset_file, score_file):
    data_val, data_train = split_dataset(dataset_file, shuffle=True, keep=False)
    train = Dataset(data_train, score_file, None, get_transform("train"))
    val = Dataset(data_val, score_file, None, get_transform("test"))
    return val, train


class Dataset(object):
    def __init__(self, data, score_file, labels=None, transform=None):
        if labels is None:
            labels = ["beautiful", "boring", "depressing", "lively", "safety", "wealthy"]

        scores = {}
        with open(score_file) as file:
            for line in file:
                line = line.strip()
                if line:
                    vals = line.split()
                    scores[vals[0]] = np.float32(vals[1:])

        image_list = []
        for line in data:
            line = line.strip()
            if line:
                image_path, uid = line.split()
                if uid in scores:
                    image_list.append([image_path, scores[uid]])
        self.image_list = image_list
        self.transform = transform
        self.labels = labels

    def __getitem__(self, index):
        image_path, y = self.image_list[index]

        image = Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert("RGB")

        if self.transform:
            image = self.transform(image)

        return image, y

    def __len__(self):
        return len(self.image_list)


if __name__ == "__main__":
    score_file = make_score_file(score_path="/home/hejian/PycharmProjects/google-street-view/src/score")
    print(score_file)

    data_file = "/home/hejian/PycharmProjects/google-street-view/src/dataset.txt"
    data_val, data_train = split_dataset(data_file, shuffle=True, keep=False)
    datasets = Dataset(data_val, score_file, None, get_transform("test"))
    print(len(datasets), datasets[0][0].shape, datasets[0][1])
