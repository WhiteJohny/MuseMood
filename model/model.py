from torch import nn


class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(75, 1024),
            nn.Sigmoid(),
            nn.Linear(1024, 2048),
            nn.Sigmoid(),
            nn.Linear(2048, 512),
            nn.Sigmoid(),
            nn.Linear(512, 6),
            nn.Sigmoid()
        )

    def forward(self, x):
        logits = self.linear_relu_stack(x)
        return logits


if __name__ == '__main__':
    from device_detector import DEVICE

    model = NeuralNetwork().to(DEVICE)
    print(model)
