from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_ROOTS = [
    Path("data/Taramasco/dataset"),
    Path("data/Taramasco_dataset"),
    Path("data/Taramasco"),
]

SENSORS = ["accelerometer", "ir_camera", "lidar", "radar"]
THERMAL_H = 24
THERMAL_W = 32
TIME_HINTS = ("time", "stamp", "date")


def find_root(root: str | Path | None = None) -> Path:
    """Find the folder containing subject_1, subject_2, etc."""
    if root is None:
        candidates = DEFAULT_ROOTS
    else:
        supplied = Path(root)
        candidates = [supplied, supplied / "dataset"]

    for candidate in candidates:
        if candidate.is_dir() and any(
            path.is_dir() for path in candidate.glob("subject_*")
        ):
            return candidate

    raise FileNotFoundError(
        "Cannot find the folder containing subject_1, subject_2, etc. "
        "Expected data/Taramasco/dataset."
    )


def find_file_ci(folder: Path, stem: str) -> Path | None:
    """Find a CSV filename without depending on letter case."""
    for path in folder.glob("*"):
        if (
            path.is_file()
            and path.suffix.lower() == ".csv"
            and path.stem.lower() == stem.lower()
        ):
            return path
    return None


def detect_time_col(df: pd.DataFrame) -> str | int | None:
    """Find a named timestamp column or column 0 in raw sensor CSVs."""
    for column in df.columns:
        if any(hint in str(column).lower() for hint in TIME_HINTS):
            return column

    if 0 in df.columns:
        return 0

    return None


def to_seconds(
    series: pd.Series,
) -> tuple[np.ndarray, float] | None:
    """Read numeric timestamps as seconds, as verified in the audit."""
    if pd.api.types.is_numeric_dtype(series):
        timestamps = series.to_numpy(dtype=np.float64)
    else:
        parsed = pd.to_datetime(series, errors="coerce")
        if parsed.isna().all():
            return None
        first_valid = parsed.dropna().iloc[0]
        timestamps = (
            (parsed - first_valid).dt.total_seconds().to_numpy()
        )

    finite = timestamps[np.isfinite(timestamps)]
    if finite.size == 0:
        return None

    span = float(finite.max() - finite.min())
    return timestamps, span


class TaramascoDS:
    """Read Taramasco sensor files and provide basic audit helpers."""

    def __init__(self, root: str | Path | None = None):
        self.root = find_root(root)
        self.subjects = sorted(
            [
                path
                for path in self.root.glob("subject_*")
                if path.is_dir()
            ],
            key=lambda path: int(path.name.split("_")[1]),
        )

    def load_sensor(
        self,
        subject: int | None,
        sensor: str,
        nrows: int | None = None,
    ) -> pd.DataFrame:
        """Read a headerless sensor CSV, preserving its first row."""
        folder = (
            self.root
            if subject is None
            else self.root / f"subject_{subject}"
        )
        source = find_file_ci(folder, sensor)

        if source is None:
            raise FileNotFoundError(
                f"Cannot find {sensor}.csv in {folder}"
            )

        return pd.read_csv(source, header=None, nrows=nrows)

    def load_falls(self) -> pd.DataFrame:
        """Read the original fall timestamp table without changing it."""
        source = find_file_ci(self.root, "falls")

        if source is None:
            source = find_file_ci(self.root, "fall")

        if source is None:
            raise FileNotFoundError(
                f"Cannot find falls.csv or fall.csv in {self.root}"
            )

        return pd.read_csv(source, header=None)

    def thermal_frames(
        self,
        subject: int | None = None,
    ) -> np.ndarray:
        """Reshape thermal pixels; spatial layout still needs verification."""
        record = self.load_sensor(subject, "ir_camera")
        expected_columns = 1 + THERMAL_H * THERMAL_W

        if record.shape[1] != expected_columns:
            raise ValueError(
                f"Expected {expected_columns} columns "
                f"(timestamp + 768 pixels), got {record.shape[1]}."
            )

        pixels = record.iloc[:, 1:].to_numpy(dtype=np.float32)
        return pixels.reshape(-1, THERMAL_H, THERMAL_W)

    def audit_sensor(
        self,
        subject: int | None,
        sensor: str,
    ) -> dict:
        info = {
            "subject": "ALL" if subject is None else subject,
            "sensor": sensor,
        }

        try:
            record = self.load_sensor(subject, sensor)
        except FileNotFoundError:
            info["status"] = "MISSING"
            return info
        except (pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
            info["status"] = "READ_ERROR"
            info["error"] = str(exc)
            return info

        info.update(
            status="ok",
            rows=len(record),
            n_cols=record.shape[1],
            nan_pct=round(
                float(record.isna().mean().mean()) * 100,
                2,
            ),
        )

        time_column = detect_time_col(record)
        info["time_col"] = time_column

        if time_column is None:
            info["status"] = "NO_TIMESTAMP_COLUMN"
            return info

        converted = to_seconds(record[time_column])
        if converted is None:
            info["status"] = "INVALID_TIMESTAMPS"
            return info

        timestamps, span = converted
        dt = np.diff(timestamps)

        invalid = int((~np.isfinite(timestamps)).sum())
        repeated = int((dt == 0).sum())
        backwards = int((dt < 0).sum())

        info.update(
            duration=round(span, 6),
            invalid_timestamps=invalid,
            repeated_timestamps=repeated,
            backwards_steps=backwards,
        )

        if invalid or repeated or backwards:
            info["status"] = "REVIEW_TIMESTAMP_ERRORS"

        positive_dt = dt[np.isfinite(dt) & (dt > 0)]

        if positive_dt.size:
            median_dt = float(np.median(positive_dt))
            info["median_dt"] = median_dt

            # Do not report a single estimated frequency when timestamps
            # contain invalid, repeated or backwards values.
            if not (invalid or repeated or backwards):
                info["approx_Hz"] = 1.0 / median_dt

        return info

    def audit_all(self) -> pd.DataFrame:
        rows = [
            self.audit_sensor(None, sensor)
            for sensor in SENSORS
        ]

        for subject_folder in self.subjects:
            subject_id = int(subject_folder.name.split("_")[1])
            rows.extend(
                self.audit_sensor(subject_id, sensor)
                for sensor in SENSORS
            )

        return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=None)
    parser.add_argument(
        "--out",
        default="reports/taramasco_loader_audit.csv",
    )
    args = parser.parse_args()

    dataset = TaramascoDS(args.root)

    print(f"Root: {dataset.root}")
    print(f"Subjects: {len(dataset.subjects)}")

    try:
        falls = dataset.load_falls()
        print(f"Fall timestamp table shape: {falls.shape}")
    except FileNotFoundError as exc:
        print(exc)

    audit = dataset.audit_all()
    print(audit.to_string(index=False))

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(output, index=False)
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
