from pathlib import Path

import numpy as np
import pytest

from data.radar_io import read_radar_csv
from data.taramasco import TaramascoDS


ROOT = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "Taramasco"
    / "dataset"
)


def test_empty_frames_and_value_order_are_preserved(tmp_path):
    source = tmp_path / "radar.csv"
    source.write_text(
        "10\n"
        "11,1,2,3,4,5,6,7,8,9,10,11,12,13,14\n"
        "12\n",
        encoding="utf-8",
    )

    timestamps, frames = read_radar_csv(source)

    np.testing.assert_array_equal(timestamps, [10, 11, 12])
    assert [frame.shape for frame in frames] == [
        (0, 7), (2, 7), (0, 7)
    ]
    np.testing.assert_array_equal(
        frames[1],
        np.arange(1, 15).reshape(2, 7),
    )


@pytest.mark.parametrize(
    "content",
    [
        "10,1,2\n",
        "nan\n",
        "10,1,2,3,4,5,6,nan\n",
    ],
)
def test_invalid_radar_rows_are_rejected(tmp_path, content):
    source = tmp_path / "invalid.csv"
    source.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError):
        read_radar_csv(source)


def test_dataset_reads_real_subject1_radar():
    dataset = TaramascoDS(ROOT)
    timestamps, frames = dataset.load_radar(subject=1)

    assert len(timestamps) == len(frames) == 5396
    assert timestamps.dtype == np.float64
    assert sum(len(frame) == 0 for frame in frames) == 242
    assert frames[0].shape == (0, 7)
    assert frames[1].shape == (0, 7)
    assert frames[2].shape == (1, 7)

    assert timestamps[0] == pytest.approx(
        1701265323.543925, rel=0, abs=1e-5
    )

    dt = np.diff(timestamps)
    assert (dt > 0).all()

    estimated_hz = 1.0 / float(np.median(dt))
    assert estimated_hz == pytest.approx(8.309798, rel=1e-5)

    print(
        f"\nRadar subject 1: {len(frames)} frames; "
        f"242 empty frames preserved; {estimated_hz:.6f} Hz"
    )
