from __future__ import annotations

import argparse
import csv
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
    """Convert the audited numeric seconds without guessing date formats.

    Invalid values retain their row position as NaN. Timestamp units must
    come from the source audit, not an automatic magnitude-based guess.
    """
    timestamps = pd.to_numeric(series, errors="coerce").to_numpy(
        dtype=np.float64
    )
    finite = timestamps[np.isfinite(timestamps)]
    if finite.size == 0:
        return None
    return timestamps, float(finite.max() - finite.min())


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
        """Read a rectangular headerless CSV, preserving its first row.

        subject=None reads a root annotation table, not a sensor stream.
        For a variable-width radar stream, use load_radar(subject).
        """
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

    def load_radar(self, subject: int):
        """Read timestamps and variable-size raw seven-value groups."""
        from data.radar_io import read_radar_csv

        source = find_file_ci(
            self.root / f"subject_{subject}", "radar"
        )
        if source is None:
            raise FileNotFoundError(
                f"Cannot find radar.csv for subject {subject}"
            )
        return read_radar_csv(source)

    def load_record(self, subject: int) -> dict:
        """Read modalities and original annotations without synchronization."""
        thermal_record = self.load_sensor(subject, "ir_camera")
        thermal = self.thermal_frames(subject=subject)
        thermal_times = thermal_record.iloc[:, 0].to_numpy(
            dtype=np.float64
        )
        radar_times, radar = self.load_radar(subject)

        falls = self.load_falls()
        column = subject - 1
        if column < 0 or column >= falls.shape[1]:
            raise ValueError("Subject has no annotation column.")

        fall_times = falls.iloc[:, column].to_numpy(dtype=np.float64)
        if not np.isfinite(fall_times).all():
            raise ValueError("Invalid fall timestamps.")

        raw_indices = {}
        for name, sensor in (
            ("thermal", "ir_camera"),
            ("radar", "radar"),
        ):
            table = self.load_sensor(None, sensor)
            if table.shape != falls.shape:
                raise ValueError(
                    f"{sensor} annotation table shape differs from falls."
                )

            values = table.iloc[:, column].to_numpy(dtype=np.float64)
            if not (
                np.isfinite(values).all()
                and np.equal(values, np.floor(values)).all()
            ):
                raise ValueError(f"Invalid raw {sensor} indices.")

            raw_indices[name] = values.astype(np.int64)

        return {
            "thermal_frames": thermal,
            "radar_frames": radar,
            "timestamps": {
                "thermal": thermal_times,
                "radar": radar_times,
            },
            "label": {
                "fall_timestamps_s": fall_times,
                "frame_indices_raw": raw_indices,
                "subject_column_0based": column,
                "index_base": None,
                "frame_labels": None,
                "status": "unverified",
            },
            "subject": subject,
        }

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
        """Audit first-column seconds in one subject's raw sensor CSV.

        Root CSVs are annotation tables and are deliberately excluded.
        csv.reader supports radar rows with differing point counts. Payload
        decoding, pixel layout and synchronization are not checked here.
        """
        if subject is None:
            raise ValueError(
                "Root CSVs are annotations, not sensor recordings. "
                "Pass a subject ID to audit_sensor."
            )
        if sensor not in SENSORS:
            raise ValueError(f"Unknown sensor: {sensor}")

        folder = self.root / f"subject_{subject}"
        source = find_file_ci(folder, sensor)
        info = {"subject": subject, "sensor": sensor}
        if source is None:
            info["status"] = "MISSING"
            return info

        timestamps = []
        widths = []
        blank_rows = 0
        try:
            with source.open(
                "r", encoding="utf-8-sig", newline=""
            ) as stream:
                for row in csv.reader(stream, strict=True):
                    # Preserve every CSV row's position, including blanks.
                    if not row or not any(cell.strip() for cell in row):
                        blank_rows += 1
                        timestamps.append(float("nan"))
                        continue
                    widths.append(len(row))
                    try:
                        timestamp = float(row[0].strip())
                    except ValueError:
                        timestamp = float("nan")
                    timestamps.append(timestamp)
        except (csv.Error, UnicodeError, OSError) as exc:
            info.update(status="READ_ERROR", error=str(exc))
            return info

        values = np.asarray(timestamps, dtype=np.float64)
        finite = np.isfinite(values)
        invalid = int((~finite).sum())
        dt = np.diff(values)
        repeated = int((dt == 0).sum())
        backwards = int((dt < 0).sum())
        info.update(
            rows=len(values),
            valid_timestamps=int(finite.sum()),
            invalid_timestamps=invalid,
            blank_rows=blank_rows,
            n_cols=max(widths, default=0),
            min_cols=min(widths, default=0),
            variable_width=len(set(widths)) > 1,
            time_col=0,
            repeated_timestamps=repeated,
            backwards_steps=backwards,
            unit="s",
            large_gap_factor=3.0,
            status="ok",
        )
        if not finite.any():
            info["status"] = "INVALID_TIMESTAMPS"
            return info

        valid_values = values[finite]
        info.update(
            duration=float(valid_values.max() - valid_values.min()),
            first_timestamp_s=float(valid_values[0]),
            last_timestamp_s=float(valid_values[-1]),
        )
        if invalid or repeated or backwards:
            info["status"] = "REVIEW_TIMESTAMP_ERRORS"
        elif len(values) < 2:
            info["status"] = "INSUFFICIENT_TIMESTAMPS"

        # Do not drop invalid rows before differencing: doing so would
        # create artificial adjacent timestamp pairs across bad rows.
        positive_dt = dt[np.isfinite(dt) & (dt > 0)]
        if positive_dt.size:
            median_dt = float(np.median(positive_dt))
            gaps = int((positive_dt > 3.0 * median_dt).sum())
            info.update(median_dt=median_dt, large_gaps=gaps)
            if not (invalid or repeated or backwards):
                info["approx_Hz"] = 1.0 / median_dt
                if gaps:
                    info["status"] = "REVIEW_IRREGULAR_SAMPLING"
        return info

    def audit_all(self) -> pd.DataFrame:
        """Audit each subject/sensor pair; never audit root annotations."""
        rows = []
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
