"""Benchmark five E0 clips in one shared scene."""

from pathlib import Path
from statistics import median
from time import perf_counter


def _cuda_device():
    try:
        import torch
    except ImportError:
        return None
    return torch.cuda if torch.cuda.is_available() else None


def benchmark(render_clip, clips, scene, output_dir, *, suffix=".npz"):
    """Measure rendering plus file writing; input loading is excluded."""
    if not callable(render_clip):
        raise TypeError("render_clip must be callable")

    entries = list(clips)
    if len(entries) != 5:
        raise ValueError("E0 requires exactly five clips")

    if not suffix.startswith(".") or "/" in suffix or "\\" in suffix:
        raise ValueError("suffix must be a simple file extension")

    target = Path(output_dir)
    prepared = []
    names = set()

    for entry in entries:
        if not isinstance(entry, tuple) or len(entry) != 3:
            raise ValueError(
                "Each clip must be (name, frame_count, clip_data)"
            )

        name, count, data = entry
        if (
            not isinstance(name, str)
            or not name
            or not name.isascii()
            or not all(char.isalnum() or char in "_-" for char in name)
        ):
            raise ValueError("Invalid clip name")
        if name in names:
            raise ValueError("Duplicate clip name")
        names.add(name)

        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise ValueError("frame_count must be a positive integer")

        destination = target / (name + suffix)
        if destination.exists():
            raise FileExistsError(destination)

        prepared.append((name, count, data, destination))

    target.mkdir(parents=True, exist_ok=True)
    cuda = _cuda_device()
    results = []

    for name, count, data, destination in prepared:
        if cuda is not None:
            cuda.synchronize()
            cuda.reset_peak_memory_stats()

        start = perf_counter()
        render_clip(data, scene, destination)

        if cuda is not None:
            cuda.synchronize()
        seconds = perf_counter() - start

        if not destination.is_file():
            raise RuntimeError(f"Renderer did not write {destination}")

        size = destination.stat().st_size
        if size == 0:
            raise RuntimeError(f"Renderer wrote empty file: {destination}")

        results.append({
            "clip": name,
            "frames": count,
            "seconds_including_write": seconds,
            "ms_per_frame_including_write": seconds * 1000 / count,
            "output_bytes": size,
            "cuda_peak_allocated_mib": (
                cuda.max_memory_allocated() / (1024 * 1024)
                if cuda is not None else None
            ),
            "output_file": str(destination),
        })

    total_frames = sum(row["frames"] for row in results)
    total_seconds = sum(
        row["seconds_including_write"] for row in results
    )

    return {
        "method": (
            "One cold run per clip; rendering and file write included"
        ),
        "scene_count": 1,
        "clips": results,
        "total_frames": total_frames,
        "total_seconds": total_seconds,
        "weighted_ms_per_frame": (
            total_seconds * 1000 / total_frames
        ),
        "median_clip_ms_per_frame": median(
            row["ms_per_frame_including_write"]
            for row in results
        ),
        "total_output_bytes": sum(
            row["output_bytes"] for row in results
        ),
        "cuda_available": cuda is not None,
    }
