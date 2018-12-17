import os
import codecs
import random
import torchvision.transforms as transforms


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


def get_transform(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225], mode="test"):
    if mode == "train":
        return transforms.Compose([
            transforms.Resize(256),
            transforms.RandomCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(mean, std)])
    else:
        return transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean, std)])
