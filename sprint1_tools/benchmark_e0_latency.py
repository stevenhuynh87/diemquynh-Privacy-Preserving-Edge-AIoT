"""Measure five E0 clips through eval.latency.benchmark."""

import argparse
import json
from pathlib import Path

import numpy as np

from eval.latency import benchmark
from sim.radar_sim import RadarSimL2
from sim.thermal_render import ThermalRenderer
from sprint1_tools.run_e0_pilot import CLIPS


def run(input_dir, scene_config, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    with Path(scene_config).open(encoding="utf-8") as file:
        config = json.load(file)

    scene = config["scene"]
    fps = float(scene["fps_assumed_from_rgb_metadata"])
    if not np.isfinite(fps) or fps <= 0:
        raise ValueError("Invalid fps in scene config")

    clips = []
    for index, (name, label) in enumerate(CLIPS):
        with np.load(input_dir / (name + ".npz"), allow_pickle=False) as data:
            pose = data["joints_camera_m"].copy()
            states = data["tracking_state"]
            if states.shape != pose.shape[:2]:
                raise ValueError(f"Invalid tracking shape: {name}")

        if pose.ndim != 3 or pose.shape[1:] != (25, 3) or len(pose) < 2:
            raise ValueError(f"Invalid pose shape: {name}")
        if not np.isfinite(pose).all():
            raise ValueError(f"Non-finite pose: {name}")

        clips.append((name, len(pose), (pose, index)))

    def render_clip(data, shared_scene, destination):
        pose, seed = data

        thermal = ThermalRenderer(
            x_bounds=shared_scene["x_bounds_m"],
            y_bounds=shared_scene["y_bounds_m"],
            background=shared_scene["thermal_background_arbitrary"],
            person=shared_scene["thermal_person_arbitrary"],
            noise_std=shared_scene["thermal_noise_std_arbitrary"],
            seed=seed,
        ).render(pose)

        radar = RadarSimL2(
            sensor_origin=shared_scene["sensor_origin_camera_xyz_m"]
        ).simulate(pose, fps)

        np.savez_compressed(
            destination,
            thermal=thermal,
            radar_points=radar,
        )

    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(
            f"Output directory is not empty: {output_dir}"
        )

    result = benchmark(render_clip, clips, scene, output_dir)
    result["source_scene_config"] = str(scene_config)
    result["fps_note"] = (
        "Assumed from RGB metadata; skeleton timestamps unverified"
    )
    result["radar_note"] = (
        "L2 skeleton-line proxy; no RF propagation"
    )

    (output_dir / "benchmark.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--scene-config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    result = run(args.input_dir, args.scene_config, args.output_dir)

    for row in result["clips"]:
        print(
            row["clip"],
            row["frames"],
            f"{row['ms_per_frame_including_write']:.3f} ms/frame",
            f"{row['output_bytes']} bytes",
        )

    print("Total frames:", result["total_frames"])
    print(
        "Weighted ms/frame including write:",
        round(result["weighted_ms_per_frame"], 3),
    )
    print("CUDA available:", result["cuda_available"])
    print("Saved:", args.output_dir / "benchmark.json")


if __name__ == "__main__":
    main()
