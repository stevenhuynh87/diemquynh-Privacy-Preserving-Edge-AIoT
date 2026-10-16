import argparse
import csv
from pathlib import Path

import numpy as np


def read_radar_csv(source):
    """Preserve timestamps, row order and variable-size radar frames."""
    timestamps = []
    frames = []

    with Path(source).open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        for row_number, row in enumerate(csv.reader(handle), start=1):
            if not row or not any(cell.strip() for cell in row):
                raise ValueError(f"Blank CSV row: {row_number}")

            if (len(row) - 1) % 7:
                raise ValueError(
                    f"Row {row_number}: expected 1 + 7*N fields, "
                    f"got {len(row)}"
                )

            try:
                values = np.asarray(row, dtype=np.float64)
            except ValueError as exc:
                raise ValueError(
                    f"Non-numeric data at row {row_number}"
                ) from exc

            if not np.isfinite(values).all():
                raise ValueError(
                    f"Non-finite data at row {row_number}"
                )

            timestamps.append(values[0])
            frames.append(values[1:].reshape(-1, 7))

    if not timestamps:
        raise ValueError("Empty radar CSV")

    return np.asarray(timestamps, dtype=np.float64), frames


def main():
    project = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", type=int, default=1)
    parser.add_argument(
        "--root",
        type=Path,
        default=project / "data" / "Taramasco" / "dataset",
    )
    args = parser.parse_args()

    source = args.root / f"subject_{args.subject}" / "radar.csv"
    output = (
        project / "reports"
        / f"radar_subject_{args.subject}_check.txt"
    )
    report = []

    def log(message):
        text = str(message)
        print(text)
        report.append(text)

    failed = False

    try:
        timestamps, frames = read_radar_csv(source)
        counts = np.asarray([len(frame) for frame in frames])
        dt = np.diff(timestamps)
        positive_dt = dt[dt > 0]

        log(f"Source: {source}")
        log(f"Radar frames: {len(frames)}")
        log(f"Timestamps: {len(timestamps)}")
        log(f"Timestamp dtype: {timestamps.dtype}")
        log(f"Empty frames preserved: {int((counts == 0).sum())}")
        log(f"Groups per frame: {counts.min()} to {counts.max()}")
        log(f"First five shapes: {[f.shape for f in frames[:5]]}")
        log(f"First timestamp: {timestamps[0]}")
        log(f"Last timestamp: {timestamps[-1]}")
        log(f"Repeated timestamp steps: {int((dt == 0).sum())}")
        log(f"Backwards timestamp steps: {int((dt < 0).sum())}")

        if positive_dt.size:
            median_dt = float(np.median(positive_dt))
            log(f"Median positive dt: {median_dt:.6f} seconds")
            log(f"Hz from median positive dt: {1 / median_dt:.6f}")

        log("Finite values: True")
        log("Raw CSV read: PASS")
        log("Seven-value groups retain their original column order.")
        log("Feature meanings, synchronization and labels: not verified.")
        log("Original CSV unchanged.")

    except Exception as exc:
        failed = True
        log(f"FAIL: {type(exc).__name__}: {exc}")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Saved: {output}")

    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
