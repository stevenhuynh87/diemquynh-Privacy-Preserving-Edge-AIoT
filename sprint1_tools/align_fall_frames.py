import csv
from pathlib import Path

ROOT = Path("data/Taramasco/dataset")
OUTPUT = Path("reports/fall_frame_alignment.csv")


def read_table(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return [[float(x) for x in row] for row in csv.reader(f)]


falls = read_table(ROOT / "falls.csv")
listed_frames = read_table(ROOT / "ir_camera.csv")

if len(falls) != 10 or any(len(row) != 10 for row in falls):
    raise ValueError("Expected falls.csv to contain 10 rows and 10 columns.")

results = []

for subject in range(1, 11):
    sensor_path = ROOT / f"subject_{subject}" / "ir_camera.csv"
    data = read_table(sensor_path)
    times = [row[0] for row in data]

    if any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError(f"Non-increasing timestamps: {sensor_path}")

    for event, row in enumerate(falls, start=1):
        target = row[subject - 1]
        index = min(
            range(len(times)),
            key=lambda i: abs(times[i] - target),
        )
        error = times[index] - target
        within_recording = times[0] <= target <= times[-1]

        results.append({
            "subject": subject,
            "event": event,
            "fall_timestamp_s": target,
            "listed_frame_raw": int(listed_frames[event - 1][subject - 1]),
            "nearest_index_0based": index,
            "nearest_row_1based": index + 1,
            "frame_timestamp_s": times[index],
            "signed_error_s": round(error, 6),
            "absolute_error_s": round(abs(error), 6),
            "within_recording": within_recording,
            "visual_check": "pending",
        })

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=list(results[0]))
    writer.writeheader()
    writer.writerows(results)

print(f"Saved: {OUTPUT}")
print(f"Events: {len(results)}")
print(f"Outside recording: {sum(not r['within_recording'] for r in results)}")
print(f"Maximum error: {max(r['absolute_error_s'] for r in results):.6f} seconds")
print("Visual checks: pending")
