import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from check_cnn import ThermalCNN


# Locate the project and read its configuration.
project = Path(__file__).resolve().parents[1]
config = json.loads(
    (project / "configs/sprint1_split.json").read_text(
        encoding="utf-8-sig"
    )
)

# Select one proposed training window.
windows = pd.read_csv(
    project / "reports/thermal_window_candidates.csv"
)
window = windows.loc[windows["split"] == "train"].iloc[0]

subject = int(window["subject"])
assert subject in config["train_subjects"]

# Read the thermal frames belonging to this window.
root = Path(config["dataset_root"])
if not root.is_absolute():
    root = project / root

source = root / f"subject_{subject}" / "ir_camera.csv"
record = pd.read_csv(source, header=None)
assert record.shape[1] == 769, "Expected timestamp + 768 pixels"

start = int(window["start_row_0based"])
stop = int(window["stop_row_exclusive"])

pixels = record.iloc[start:stop, 1:].to_numpy(dtype=np.float32)
assert len(pixels) == int(window["n_frames"])
assert np.isfinite(pixels).all(), "Non-finite pixels found"

images = torch.from_numpy(pixels.reshape(-1, 1, 24, 32))

# Reuse the existing CNN and combine frame outputs.
torch.manual_seed(config["seed"])
model = ThermalCNN()
model.eval()

with torch.no_grad():
    frame_logits = model(images)
    window_logits = frame_logits.mean(dim=0, keepdim=True)

print("Subject:", subject)
print("Window frames:", len(images))
print("Input shape:", tuple(images.shape))
print("Frame outputs:", tuple(frame_logits.shape))
print("Window output:", tuple(window_logits.shape))
print("Finite output:", torch.isfinite(window_logits).all().item())
print("Label status:", window["label_status"])
print("Training: not started")
