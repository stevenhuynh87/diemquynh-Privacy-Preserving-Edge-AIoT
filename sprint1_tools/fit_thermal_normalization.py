import json
from pathlib import Path

import numpy as np
import pandas as pd


project = Path(__file__).resolve().parents[1]

config = json.loads(
    (project / "configs/sprint1_split.json").read_text(
        encoding="utf-8-sig"
    )
)
windows = pd.read_csv(
    project / "reports/thermal_window_candidates.csv"
)
train = windows.loc[windows["split"] == "train"]

assert not train.empty, "No training windows"
assert set(train["subject"]) == set(config["train_subjects"])

root = Path(config["dataset_root"])
if not root.is_absolute():
    root = project / root

pixel_count = 0
pixel_sum = 0.0
pixel_square_sum = 0.0
minimum = float("inf")
maximum = float("-inf")
frames_per_subject = {}

for subject, subject_windows in train.groupby("subject"):
    subject = int(subject)
    source = root / f"subject_{subject}" / "ir_camera.csv"
    record = pd.read_csv(source, header=None)

    assert record.shape[1] == 769, "Expected timestamp + 768 pixels"

    # Each selected frame contributes once, even if windows overlap.
    selected = np.zeros(len(record), dtype=bool)

    for window in subject_windows.itertuples(index=False):
        start = int(window.start_row_0based)
        stop = int(window.stop_row_exclusive)

        assert 0 <= start < stop <= len(record), "Invalid row range"
        assert stop - start == int(window.n_frames)

        selected[start:stop] = True

    pixels = record.iloc[selected, 1:].to_numpy(dtype=np.float64)
    assert pixels.size > 0, "No selected pixels"
    assert np.isfinite(pixels).all(), "Non-finite training pixels"

    frames_per_subject[str(subject)] = int(selected.sum())
    pixel_count += int(pixels.size)
    pixel_sum += float(pixels.sum())
    pixel_square_sum += float(np.square(pixels).sum())
    minimum = min(minimum, float(pixels.min()))
    maximum = max(maximum, float(pixels.max()))

mean = pixel_sum / pixel_count
variance = max(0.0, pixel_square_sum / pixel_count - mean ** 2)
std = float(np.sqrt(variance))

assert np.isfinite(mean) and np.isfinite(std)
assert std > 0, "Cannot normalize pixels with zero variation"

report = {
    "method": "global_pixel_standardization",
    "fit_split": "train",
    "fit_subjects": sorted(config["train_subjects"]),
    "fit_scope": "unique frames selected by training windows",
    "mean": mean,
    "std": std,
    "std_definition": "population",
    "pixel_count": pixel_count,
    "frames_per_subject": frames_per_subject,
    "minimum": minimum,
    "maximum": maximum,
    "training_ready": False,
}

destination = project / "reports/thermal_normalization.json"
destination.write_text(
    json.dumps(report, indent=2),
    encoding="utf-8",
)

print("Fit subjects:", report["fit_subjects"])
print("Unique training frames:", sum(frames_per_subject.values()))
print(f"Mean: {mean:.6f}")
print(f"Std: {std:.6f}")
print(f"Pixel range: {minimum:.6f} to {maximum:.6f}")
print("Validation/test used for fitting: False")
print("Saved: reports/thermal_normalization.json")
print("Training: not started")
