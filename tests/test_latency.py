from pathlib import Path

import numpy as np
import pytest

from eval.latency import benchmark


def renderer(data, scene, output_path):
    np.savez_compressed(output_path, thermal=data + scene["offset"])


def clips():
    return [
        (f"synthetic_{i}", i + 3, np.ones((i + 3, 24, 32)))
        for i in range(5)
    ]


def test_benchmark_writes_and_measures_five_clips(tmp_path):
    result = benchmark(renderer, clips(), {"offset": 2}, tmp_path)

    assert result["scene_count"] == 1
    assert result["total_frames"] == 25
    assert len(result["clips"]) == 5
    assert result["total_output_bytes"] > 0

    for row in result["clips"]:
        path = Path(row["output_file"])
        assert path.stat().st_size == row["output_bytes"]
        assert row["ms_per_frame_including_write"] >= 0
        with np.load(path, allow_pickle=False) as data:
            assert data["thermal"].shape == (
                row["frames"], 24, 32
            )
            assert np.all(data["thermal"] == 3)


def test_benchmark_refuses_overwrite(tmp_path):
    existing = tmp_path / "synthetic_0.npz"
    existing.write_bytes(b"existing")

    with pytest.raises(FileExistsError):
        benchmark(renderer, clips(), {"offset": 2}, tmp_path)

    assert existing.read_bytes() == b"existing"


def test_benchmark_requires_five_clips(tmp_path):
    with pytest.raises(ValueError, match="five clips"):
        benchmark(renderer, clips()[:4], {"offset": 2}, tmp_path)
