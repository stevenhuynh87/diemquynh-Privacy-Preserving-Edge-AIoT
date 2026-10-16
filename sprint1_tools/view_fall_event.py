import csv
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path("data/Taramasco/dataset")
SUBJECT = 1
EVENT = 1

with Path("reports/fall_frame_alignment.csv").open(
    newline="", encoding="utf-8-sig"
) as f:
    events = list(csv.DictReader(f))

event = next(
    row for row in events
    if int(row["subject"]) == SUBJECT
    and int(row["event"]) == EVENT
)
target = float(event["fall_timestamp_s"])

path = ROOT / f"subject_{SUBJECT}" / "ir_camera.csv"
with path.open(newline="", encoding="utf-8-sig") as f:
    data = np.array(
        [[float(x) for x in row] for row in csv.reader(f)]
    )

if data.shape[1] != 769:
    raise ValueError(f"Expected 769 columns, got {data.shape[1]}")
if not np.isfinite(data).all():
    raise ValueError("Data contains non-finite values.")

times = data[:, 0]
offsets = [-10, -5, 0, 5, 10]
indices = [
    int(np.argmin(np.abs(times - (target + offset))))
    for offset in offsets
]

# Candidate layout; spatial orientation still needs verification.
images = [data[i, 1:].reshape(24, 32) for i in indices]
vmin, vmax = np.percentile(np.stack(images), [2, 98])

fig, axes = plt.subplots(
    1, 5, figsize=(15, 4), layout="constrained"
)

for ax, index, image in zip(axes, indices, images):
    plot = ax.imshow(
        image, cmap="inferno", vmin=vmin, vmax=vmax,
        interpolation="nearest"
    )
    relative_time = times[index] - target
    ax.set_title(
        f"{relative_time:+.2f} s\nRow {index + 1}"
    )
    ax.axis("off")

fig.suptitle(
    f"Subject {SUBJECT}, event {EVENT} — candidate 24x32 layout"
)
fig.colorbar(plot, ax=axes, label="Raw thermal value", shrink=0.7)

output = Path(f"reports/thermal_s{SUBJECT}_event{EVENT}_wide.png")
output.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(output, dpi=160)
plt.close(fig)
print(f"Saved: {output}")

from matplotlib.animation import FuncAnimation, PillowWriter

selected = np.flatnonzero(
    (times >= target - 12) & (times <= target + 12)
)
if len(selected) == 0:
    raise ValueError("No frames in the selected time range.")

fig, ax = plt.subplots(figsize=(6, 5))
display = ax.imshow(
    data[selected[0], 1:].reshape(24, 32),
    cmap="inferno", vmin=vmin, vmax=vmax,
    interpolation="nearest",
)
ax.axis("off")
title = ax.set_title("")

def update(position):
    index = selected[position]
    display.set_data(data[index, 1:].reshape(24, 32))
    title.set_text(
        f"Subject {SUBJECT}, event {EVENT}\n"
        f"Row {index + 1} | {times[index] - target:+.2f} s"
    )
    return display, title

animation = FuncAnimation(
    fig, update, frames=len(selected), interval=400
)
gif_path = Path(f"reports/thermal_s{SUBJECT}_event{EVENT}.gif")
animation.save(gif_path, writer=PillowWriter(fps=2.5))
plt.close(fig)
print(f"Saved: {gif_path}")
