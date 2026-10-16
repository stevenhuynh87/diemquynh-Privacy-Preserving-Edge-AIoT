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

root = Path(config["dataset_root"])
if not root.is_absolute():
    root = project / root

# Original thermal frame-index annotations.
original = pd.read_csv(root / "ir_camera.csv", header=None)
assert original.shape == (10, 10)

windows = pd.read_csv(
    project / "reports/thermal_window_candidates.csv"
)
positive = windows.loc[windows["candidate_label"] == 1]

assert not positive.empty
results = []

for window in positive.itertuples(index=False):
    subject = int(window.subject)
    event = int(window.event)

    value = float(original.iloc[event - 1, subject - 1])
    assert np.isfinite(value) and value.is_integer()
    supplied_index = int(value)

    start = int(window.start_row_0based)
    stop = int(window.stop_row_exclusive)

    # Check both possibilities without declaring an index base.
    inside_if_1based = start <= supplied_index - 1 < stop
    inside_if_0based = start <= supplied_index < stop

    results.append({
        "subject": subject,
        "event": event,
        "split": window.split,
        "supplied_index": supplied_index,
        "inside_if_1based": inside_if_1based,
        "inside_if_0based": inside_if_0based,
        "inside_under_at_least_one": (
            inside_if_1based or inside_if_0based
        ),
    })

report = pd.DataFrame(results)
destination = project / "reports/window_annotation_check.csv"
report.to_csv(destination, index=False)

outside = report.loc[~report["inside_under_at_least_one"]]

print("Fall windows checked:", len(report))
print("Outside under both index interpretations:", len(outside))

if not outside.empty:
    print(outside.to_string(index=False))

print("Index base: not determined by this check")
print("Visual correctness: not established by this check")
print("Saved: reports/window_annotation_check.csv")
print("Original annotations unchanged")
