import torch
import torch.nn as nn
from torchvision import models


class Net(nn.Module):
    def __init__(self, num_classes=6, pretrained=True):
        super(Net, self).__init__()
        resnet = models.resnet50(pretrained=pretrained)

        self.firstconv = resnet.conv1
        self.firstbn = resnet.bn1
        self.firstrelu = resnet.relu
        self.firstmaxpool = resnet.maxpool

        self.layer1 = resnet.layer1
        self.layer2 = resnet.layer2
        self.layer3 = resnet.layer3
        self.layer4 = resnet.layer4

        self.drop = nn.Dropout2d(p=0.2)
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(2048, num_classes)
        self.init_weights()

    def forward(self, x):
        out = self.firstconv(x)
        out = self.firstbn(out)
        out = self.firstrelu(out)
        out = self.firstmaxpool(out)

        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)

        out = self.drop(out)
        out = self.avgpool(out)
        out = out.view(out.size(0), -1)
        out = self.fc(out)
        return out

    def init_weights(self):
        pass


if __name__ == "__main__":
    net = Net(num_classes=6, pretrained=True)
    num_params = 0
    for p in net.parameters():
        num_params += p.numel()
    print("The number of parameters: [{}]".format(num_params))
    x = torch.randn(2, 3, 256, 256)
    c = torch.sigmoid(net(x))
    print(x.shape, c.shape, "\n", c.tolist())
