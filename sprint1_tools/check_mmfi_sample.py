import sys
from pathlib import Path

import numpy as np
from PIL import Image

root = Path(sys.argv[1])
lines = [f"Sample: {root}"]


def log(message):
    lines.append(message)
    print(message)


files = [
    root / "depth/frame001.png",
    root / "rgb/frame001.npy",
    root / "infra1/frame001.npy",
    root / "infra2/frame001.npy",
]

# Include ground-truth arrays if present.
files.extend(sorted(root.glob("*.npy")))

for path in files:
    log(f"\nFile: {path.relative_to(root)}")
    try:
        if path.suffix.lower() == ".png":
            with Image.open(path) as image:
                array = np.array(image)
        else:
            array = np.load(path, allow_pickle=False)

        log(f"Shape: {array.shape}")
        log(f"Dtype: {array.dtype}")

        if array.size == 0:
            raise ValueError("Empty array")
        if not np.issubdtype(array.dtype, np.number):
            raise ValueError("Expected numeric data")
        if not np.isfinite(array).all():
            raise ValueError("Non-finite values")

        log(f"Range: {array.min()} to {array.max()}")
        log("Read check: PASS")
    except Exception as error:
        log(f"Read check: FAIL — {error}")

log("\nLiDAR, mmWave and WiFi-CSI: decoding not checked.")

output = Path("reports/mmfi_sample_check.txt")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text("\n".join(lines), encoding="utf-8")
print(f"\nSaved: {output}")
