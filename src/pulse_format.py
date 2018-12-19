import os
import json
import codecs


def log_imgs_to_dataset(log_file, years=None, check=True):
    root = os.path.dirname(log_file)
    root = os.path.realpath(root)

    if years is None:
        years = ["2013", "2014", "2015", "2016"]
    years = set(years)

    data = []
    with open(log_file) as file:
        for line in file:
            if not line.startswith(":"):
                continue
            try:
                vals = json.loads(line[1:])
                image_date = vals["date"].split("-")[0]
                if image_date in years:
                    data.append([vals["image_path"], vals["log_id"]])
            except:
                pass

    if check:
        for i in data:
            i[0] = os.path.join(root, os.path.basename(i[0]))

    return data


def dataset_to_file(data, file_name, output_dir="."):
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
    data = log_imgs_to_dataset(log_file, check=True)
    res = dataset_to_file(data, "dataset.txt", ".")
    print(res)
