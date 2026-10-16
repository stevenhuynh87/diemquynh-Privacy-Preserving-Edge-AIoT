import csv
from pathlib import Path

import numpy as np
import pytest

from data.taramasco import TaramascoDS


ROOT = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "Taramasco"
    / "dataset"
)


@pytest.fixture(scope="module")
def dataset():
    assert ROOT.is_dir(), f"Dataset folder not found: {ROOT}"
    return TaramascoDS(ROOT)


def test_record_preserves_all_rows(dataset):
    source = ROOT / "subject_1" / "ir_camera.csv"

    with source.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        first_row = next(reader)
        raw_count = 1 + sum(
            1 for row in reader if any(cell.strip() for cell in row)
        )

    record = dataset.load_sensor(1, "ir_camera")

    assert raw_count == 1785
    assert record.shape == (raw_count, 769)

    np.testing.assert_allclose(
        record.iloc[0].to_numpy(dtype=np.float64),
        np.asarray(first_row, dtype=np.float64),
        rtol=1e-12,
        atol=1e-6,
    )

    print(f"\nSubject 1 thermal rows preserved: {len(record)}")


def test_thermal_frames_shape_and_values(dataset):
    frames = dataset.thermal_frames(subject=1)

    assert frames.shape == (1785, 24, 32)
    assert frames.dtype == np.float32
    assert np.isfinite(frames).all()

    print(f"\nThermal shape: {frames.shape}; finite pixels: True")


def test_real_thermal_frequency(dataset):
    record = dataset.load_sensor(1, "ir_camera")
    timestamps = record.iloc[:, 0].to_numpy(dtype=np.float64)

    assert np.isfinite(timestamps).all()
    assert timestamps[0] == pytest.approx(
        1701265332.33056, rel=0, abs=1e-5
    )

    dt = np.diff(timestamps)
    assert (dt > 0).all(), "Repeated or backwards timestamps"

    median_dt = float(np.median(dt))
    estimated_hz = 1.0 / median_dt

    # Expected range from the completed subject-1 audit.
    assert 2.5 < estimated_hz < 2.7

    print(f"\nMedian dt: {median_dt:.6f} s")
    print(f"Estimated thermal frequency: {estimated_hz:.6f} Hz")

def test_record_contains_modalities_and_raw_annotations(dataset):
    record = dataset.load_record(subject=1)

    assert set(record) == {
        "thermal_frames", "radar_frames",
        "timestamps", "label", "subject",
    }
    assert record["subject"] == 1
    assert record["thermal_frames"].shape == (1785, 24, 32)
    assert len(record["radar_frames"]) == 5396
    assert record["timestamps"]["thermal"].shape == (1785,)
    assert record["timestamps"]["radar"].shape == (5396,)

    label = record["label"]
    assert label["fall_timestamps_s"].shape == (10,)
    assert label["fall_timestamps_s"][0] == 1701265486.0
    assert label["frame_indices_raw"]["thermal"][0] == 418
    assert label["frame_indices_raw"]["radar"][0] == 1356

    # Unknown annotation conventions must remain explicit.
    assert label["index_base"] is None
    assert label["frame_labels"] is None
    assert label["status"] == "unverified"

    print("\nRecord fields complete; original annotations preserved.")
