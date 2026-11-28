"""E0 thermal and geometric radar pilot on five selected NTU pose NPZ files."""

import argparse
import csv
import json
from pathlib import Path
from time import perf_counter

import numpy as np

from sim.radar_sim import RadarSimL2
from sim.thermal_render import ThermalRenderer


CLIPS = (
    ("S001C001P001R001A043", "fall"),
    ("S001C001P008R001A043", "fall"),
    ("S001C001P008R001A006", "adl_pickup"),
    ("S001C001P008R001A008", "adl_sit"),
    ("S001C001P008R001A009", "adl_stand"),
)


def run(input_dir, output_dir, *, fps=30.0):
    """One cold CPU run; timing excludes reading, includes rendering and writing."""
    if not np.isfinite(fps) or fps <= 0:
        raise ValueError("fps must be positive")
    input_dir, output_dir = Path(input_dir), Path(output_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {output_dir}")
    poses = []
    for name, label in CLIPS:
        path = input_dir / (name + ".npz")
        with np.load(path, allow_pickle=False) as data:
            pose = data["joints_camera_m"].copy()
            states = data["tracking_state"].copy()
        if pose.ndim != 3 or pose.shape[1:] != (25, 3) or len(pose) < 2:
            raise ValueError(f"Invalid pose shape: {path}")
        if states.shape != pose.shape[:2] or not np.isfinite(pose).all():
            raise ValueError(f"Invalid tracking or coordinates: {path}")
        poses.append((name, label, pose, states))

    # Fixed bounds shared across all five clips: one orthographic scene.
    all_xy = np.concatenate([p[:, :, :2].reshape(-1, 2) for _, _, p, _ in poses])
    low = np.min(all_xy, axis=0) - 0.2
    high = np.max(all_xy, axis=0) + 0.2
    scene = {"x_bounds_m": [float(low[0]), float(high[0])],
             "y_bounds_m": [float(low[1]), float(high[1])],
             "sensor_origin_camera_xyz_m": [0.0, 0.0, 0.0],
             "thermal_background_arbitrary": 22.0,
             "thermal_person_arbitrary": 30.0,
             "thermal_noise_std_arbitrary": 0.2,
             "fps_assumed_from_rgb_metadata": float(fps)}
    radar = RadarSimL2(sensor_origin=(0, 0, 0))
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for index, (name, label, pose, states) in enumerate(poses):
        renderer = ThermalRenderer(x_bounds=scene["x_bounds_m"],
                                   y_bounds=scene["y_bounds_m"], seed=index)
        start = perf_counter()
        thermal = renderer.render(pose)
        thermal_seconds = perf_counter() - start
        start = perf_counter()
        cloud = radar.simulate(pose, fps)
        radar_seconds = perf_counter() - start
        path = output_dir / (name + "_e0.npz")
        start = perf_counter()
        np.savez_compressed(path, thermal=thermal, radar_points=cloud)
        write_seconds = perf_counter() - start
        rows.append({"clip": name, "label": label, "frames": len(pose),
                     "thermal_ms_per_frame": thermal_seconds * 1000 / len(pose),
                     "radar_l2_ms_per_frame": radar_seconds * 1000 / len(pose),
                     "write_ms_per_frame": write_seconds * 1000 / len(pose),
                     "output_bytes": path.stat().st_size,
                     "all_25_joints_tracked_frames": int(np.all(states == 2, axis=1).sum()),
                     "gpu_vram_mib": "N/A (CPU NumPy render)",
                     "output_file": str(path)})
    with (output_dir / "measurements.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (output_dir / "config.json").write_text(
        json.dumps({"scene": scene, "measurement": "one cold run per clip; read excluded; "
                    "thermal, L2 and compressed write separately timed",
                    "limitations": ["camera X/Y orthographic skeleton-line proxy",
                                    "not calibrated thermal or RF radar",
                                    "no tracking-state filtering",
                                    "skeleton sampling interval assumed from RGB metadata",
                                    "L1 and GPU VRAM unmeasured"]}, indent=2) + "\n", encoding="utf-8")
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--fps", type=float, default=30.0)
    args = parser.parse_args()
    rows = run(args.input_dir, args.output_dir, fps=args.fps)
    for row in rows:
        print(row["clip"], row["label"], row["frames"],
              f'thermal={row["thermal_ms_per_frame"]:.3f}ms/frame',
              f'L2={row["radar_l2_ms_per_frame"]:.3f}ms/frame',
              f'write={row["write_ms_per_frame"]:.3f}ms/frame',
              f'bytes={row["output_bytes"]}')
    print("Saved:", args.output_dir / "measurements.csv")
    print("L1/GPU VRAM not measured; results are performance pilot only.")


if __name__ == "__main__":
    main()
