import torch
from torch import nn
from torch.utils.data import DataLoader
from taramasco_ds import TaramascoDS


class ThermalCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Conv2d(1, 8, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(8, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(16, 2),
        )

    def forward(self, images):
        return self.network(images)


if __name__ == "__main__":
    torch.manual_seed(42)

    dataset = TaramascoDS(
        "data/Taramasco/dataset/subject_1/ir_camera.csv"
    )
    loader = DataLoader(
        dataset, batch_size=8, shuffle=False,
        num_workers=0
    )
    images = next(iter(loader))["image"]

    model = ThermalCNN()
    model.eval()

    with torch.no_grad():
        logits = model(images)

    print("Input shape:", tuple(images.shape))
    print("Output shape:", tuple(logits.shape))
    print("Finite outputs:", torch.isfinite(logits).all().item())
    print("Parameters:", sum(p.numel() for p in model.parameters()))
    print("Training: not started")
