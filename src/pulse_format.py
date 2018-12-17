import os
import json
import codecs


def log_imgs_to_json(log_file, check=True):
    root = os.path.dirname(log_file)
    root = os.path.realpath(root)

    names = ["image_path", "log_id"]

    data = []
    with open(log_file) as log_file:
        for l in log_file:
            if not l.startswith(":"):
                continue
            l = json.loads(l[1:])
            data.append([l[i] for i in names])

    if check:
        for i in data:
            i[0] = os.path.join(root, os.path.basename(i[0]))

    return data


def list_to_file(data, file_name, output_dir="."):
    output_dir = os.path.realpath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, file_name)
    with codecs.open(file_path, "w", "utf-8") as writer:
        for line in data:
            writer.write(" ".join(line))
            writer.write("\n")
    return file_path


if __name__ == "__main__":
    log_file = "/data1/tmps/images_pulse/log.imgs"
    data = log_imgs_to_json(log_file, check=True)
    res = list_to_file(data, "dataset.txt", "tmps")
    print(res)
