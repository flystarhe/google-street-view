import os
import time
import argparse
import numpy as np
import torch
from torch.optim import lr_scheduler
from src.dnn import Logger
from src.dnn import str2list, str2bool
from src.dnn import print_network, print_options
from src.dnn.data import get_dataset
from src.dnn.model import Net


def get_scheduler(optimizer, lr_update_step, lr_update_gamma):
    return lr_scheduler.StepLR(optimizer, step_size=lr_update_step, gamma=lr_update_gamma)


def load_net(net, iters, checkpoints_dir, device):
    file_name = os.path.join(checkpoints_dir, "net_{:08d}.pth".format(iters))
    net.load_state_dict(torch.load(file_name, map_location=device))
    net.to(device)


def save_net(net, iters, checkpoints_dir):
    file_name = os.path.join(checkpoints_dir, "net_{:08d}.pth".format(iters))
    if isinstance(net, torch.nn.DataParallel):
        torch.save(net.module.state_dict(), file_name)
    else:
        torch.save(net.state_dict(), file_name)


def get_loader(dataset, batch_size, shuffle, workers):
    loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=workers)
    return loader


"""
import os
import sys

mylibs = ["/home/hejian/PycharmProjects/google-street-view"]
os.chdir(mylibs[0])
for mylib in mylibs:
    if mylib not in sys.path:
        sys.path.insert(0, mylib)

from src.dnn.train import main

main(["--checkpoints_dir", "/data1/tmps/street_view",
      "--dataset_file", "src/dataset.txt",
      "--score_file", "src/score/score_plus.txt",
      "--gpu_ids", "0,1",
      "--batch_size", "16",
      "--num_worker", "8",
      "--resume_iters", "-1",
      "--start_iters", "1",
      "--train_iters", "500",
      "--lr", "0.002",
      "--lr_update_step", "200",
      "--lr_update_gamma", "0.1"])
"""


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoints_dir", type=str, default="/data1/tmps/street_view")
    parser.add_argument("--dataset_file", type=str, default="src/dataset.txt")
    parser.add_argument("--score_file", type=str, default="src/score/score_plus.txt")
    parser.add_argument("--gpu_ids", type=str2list, default="0,")
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--num_worker", type=int, default=8)
    parser.add_argument("--resume_iters", type=int, default=-1)
    parser.add_argument("--start_iters", type=int, default=1)
    parser.add_argument("--train_iters", type=int, default=500)
    parser.add_argument("--lr", type=float, default=0.002)
    parser.add_argument("--lr_update_step", type=int, default=200)
    parser.add_argument("--lr_update_gamma", type=float, default=0.1)
    opt, _ = parser.parse_known_args(args)
    logger = Logger(opt)
    print_options(opt)

    torch.backends.cudnn.benchmark = True
    device = torch.device("cuda:{}".format(opt.gpu_ids[0]) if opt.gpu_ids else "cpu")
    model = Net(num_classes=6, pretrained=True).to(device)

    if opt.resume_iters > -1:
        load_net(model, opt.resume_iters, opt.checkpoints_dir, device)

    if len(opt.gpu_ids) > 1:
        model = torch.nn.DataParallel(model, device_ids=opt.gpu_ids)
    print_network(model, "Net")

    params_to_update = []
    # default: params_to_update = model.parameters()
    for name, param in model.named_parameters():
        if name.startswith("fc."):
            param.requires_grad = True
            params_to_update.append(param)
        else:
            param.requires_grad = False

    optimizer = torch.optim.Adam(params_to_update, lr=opt.lr, betas=(0.5, 0.999))
    criterion = torch.nn.L1Loss()
    scheduler = get_scheduler(optimizer, opt.lr_update_step, opt.lr_update_gamma)

    dataset_val, dataset_train = get_dataset(opt.dataset_file, opt.score_file)
    print("train size: {}, val size: {}".format(len(dataset_train), len(dataset_val)))
    data_loaders = {"train": get_loader(dataset_train, opt.batch_size, True, opt.num_worker),
                    "val": get_loader(dataset_val, opt.batch_size, True, opt.num_worker)}

    best_loss = np.Inf
    since = time.time()
    for curr_iters in range(opt.start_iters, opt.start_iters + opt.train_iters):
        print("-" * 50)
        for phase in ["train", "val"]:
            if phase == "train":
                scheduler.step()
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            for inputs, targets in data_loaders[phase]:
                inputs = inputs.to(device)
                targets = targets.to(device)

                optimizer.zero_grad()
                with torch.set_grad_enabled(phase == "train"):
                    outputs = torch.sigmoid(model(inputs))
                    loss = criterion(outputs, targets)
                    if phase == "train":
                        loss.backward()
                        optimizer.step()
                running_loss += loss.item()
            epoch_loss = running_loss / len(data_loaders[phase])

            save_net(model, curr_iters, opt.checkpoints_dir)
            if phase == "val" and epoch_loss < best_loss:
                best_loss = epoch_loss
                save_net(model, 0, opt.checkpoints_dir)

            time_elapsed = time.time() - since
            print("Complete in {:.0f}m {:.0f}s".format(time_elapsed // 60, time_elapsed % 60))
            message = "{}, lr:{:.8f}, {}_loss:{:.6f}, best_loss:{:.6f}".format(curr_iters,
                                                                               optimizer.param_groups[0]["lr"], phase,
                                                                               epoch_loss, best_loss)
            logger.log(message)
            print(message)
