import csv
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader


class TaramascoDS(Dataset):
    def __init__(self, csv_path):
        self.path = Path(csv_path)

        with self.path.open(
            newline="", encoding="utf-8-sig"
        ) as f:
            rows = [
                [float(x) for x in row]
                for row in csv.reader(f)
            ]

        data = np.asarray(rows, dtype=np.float64)

        if data.ndim != 2 or data.shape[1] != 769:
            raise ValueError("Expected timestamp + 768 pixels.")
        if len(data) == 0 or not np.isfinite(data).all():
            raise ValueError("Empty data or non-finite values.")
        if np.any(np.diff(data[:, 0]) <= 0):
            raise ValueError("Timestamps must increase.")

        self.times = data[:, 0].copy()

        # Candidate pixel layout, as used in the preview.
        self.images = data[:, 1:].astype(
            np.float32
        ).reshape(-1, 1, 24, 32)

    def __len__(self):
        return len(self.times)

    def __getitem__(self, index):
        return {
            "image": torch.from_numpy(
                self.images[index].copy()
            ),
            "timestamp_s": torch.tensor(
                self.times[index], dtype=torch.float64
            ),
            "row_1based": index + 1,
            "subject": self.path.parent.name,
        }


if __name__ == "__main__":
    dataset = TaramascoDS(
        "data/Taramasco/dataset/subject_1/ir_camera.csv"
    )
    loader = DataLoader(
        dataset, batch_size=8, shuffle=False,
        num_workers=0
    )
    batch = next(iter(loader))

    print("Samples:", len(dataset))
    print("Batch shape:", tuple(batch["image"].shape))
    print("Image dtype:", batch["image"].dtype)
    print("Timestamp dtype:", batch["timestamp_s"].dtype)
    print("Finite pixels:", torch.isfinite(
        batch["image"]
    ).all().item())
    print("First timestamp:", batch["timestamp_s"][0].item())
    print("Labels: not assigned")
