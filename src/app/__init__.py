import torch
import torchvision.transforms as transforms
from PIL import Image
from src.dnn.model import Net

"""
import os
import sys

mylibs = ["/home/hejian/PycharmProjects/google-street-view"]
os.chdir(mylibs[0])
for mylib in mylibs:
    if mylib not in sys.path:
        sys.path.insert(0, mylib)
"""

normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])


def load_net(model_path, device):
    net = Net(num_classes=6, pretrained=False).to(device)
    net.load_state_dict(torch.load(model_path, map_location=device))
    net.to(device)
    net.eval()
    return net


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_path = "/data1/tmps/street_view/net_00000500.pth"
model = load_net(model_path, device)
trans = transforms.Compose([transforms.Resize(256), transforms.CenterCrop(256), transforms.ToTensor(), normalize])


def inference(image_path, device):
    # image_path = "/data1/tmps/images_pulse/-x46IJ2AQTU4FWu9WiCRfw,1214011640.jpg"
    image = Image.open(image_path)
    if image.mode != "RGB":
        image = image.convert("RGB")
    x = trans(image).unsqueeze(0).to(device)
    y = torch.sigmoid(model(x))
    return y.tolist()
