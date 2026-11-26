"""Audit tracking quality for three NTU clips used in COM review."""

import csv
import io
from pathlib import Path
from zipfile import ZipFile

import numpy as np


DATA_ROOT = Path(
    r"C:\Q\NCKH\Privacy-Preserving Edge AIoT Fall Detection via Cross-Modal Knowledge Distillation from RGB to Low-Resolution"
    r"\phykd_datasets\NTU_RGBD_120"
)
ARCHIVE = DATA_ROOT / "nturgbd_skeletons_s001_to_s017.zip"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "reports" / "ntu_com_tracking"

SAMPLES = [
    "S001C001P001R001A043",
    "S001C001P002R001A043",
    "S001C001P003R001A043",
]

# Joint IDs start at 1.
# Taken from the implementation supplied by the user.
COM_IDS = [4] + list(range(5, 21))
TORSO_IDS = [3, 13, 17]

JOINT_NAMES = {
    3: "Neck",
    4: "Head",
    5: "ShoulderLeft",
    6: "ElbowLeft",
    7: "WristLeft",
    8: "HandLeft",
    9: "ShoulderRight",
    10: "ElbowRight",
    11: "WristRight",
    12: "HandRight",
    13: "HipLeft",
    14: "KneeLeft",
    15: "AnkleLeft",
    16: "FootLeft",
    17: "HipRight",
    18: "KneeRight",
    19: "AnkleRight",
    20: "FootRight",
}


def read_line(stream):
    line = stream.readline()
    if not line:
        raise ValueError("Unexpected end of skeleton file")
    return line.strip()


def read_sample(archive, member):
    """Require exactly one body and a stable body ID."""
    with archive.open(member) as raw:
        with io.TextIOWrapper(raw, encoding="utf-8-sig") as stream:
            frame_count = int(read_line(stream))
            if frame_count < 1:
                raise ValueError("No frames")

            joints = np.empty((frame_count, 25, 3), dtype=float)
            tracking = np.empty((frame_count, 25), dtype=np.int8)
            body_ids = []

            for frame in range(frame_count):
                body_count = int(read_line(stream))
                if body_count != 1:
                    raise ValueError(
                        f"Frame {frame + 1}: expected one body, "
                        f"found {body_count}"
                    )

                metadata = read_line(stream).split()
                if not metadata:
                    raise ValueError("Missing body metadata")
                body_ids.append(metadata[0])

                if int(read_line(stream)) != 25:
                    raise ValueError("Expected 25 joints")

                for joint in range(25):
                    values = read_line(stream).split()
                    if len(values) != 12:
                        raise ValueError("Expected 12 fields per joint")

                    joints[frame, joint] = [
                        float(value) for value in values[:3]
                    ]
                    state = int(values[11])
                    if state not in (0, 1, 2):
                        raise ValueError("Invalid tracking state")
                    tracking[frame, joint] = state

    if len(set(body_ids)) != 1:
        raise ValueError("Body ID changes across frames")

    return joints, tracking


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def joint_list(mask, ids):
    return ";".join(str(joint) for joint, flag in zip(ids, mask) if flag)


def audit(sample, joints, tracking):
    com_indices = np.asarray(COM_IDS) - 1
    torso_indices = np.asarray(TORSO_IDS) - 1

    com_states = tracking[:, com_indices]
    torso_states = tracking[:, torso_indices]

    com_finite = np.isfinite(joints[:, com_indices]).all(axis=(1, 2))
    com_all_tracked = np.all(com_states == 2, axis=1)
    com_has_inferred = np.any(com_states == 1, axis=1)
    com_has_untracked = np.any(com_states == 0, axis=1)
    torso_all_tracked = np.all(torso_states == 2, axis=1)

    # Mutually exclusive tracking categories.
    com_inferred_only = com_has_inferred & ~com_has_untracked

    frame_rows = []
    for frame in range(len(joints)):
        if com_has_untracked[frame]:
            category = "contains_untracked"
        elif com_has_inferred[frame]:
            category = "inferred_without_untracked"
        else:
            category = "all_tracked"

        frame_rows.append({
            "frame_1based": frame + 1,
            "com_tracking_category": category,
            "com_coordinates_finite": bool(com_finite[frame]),
            "com_inferred_joint_ids": joint_list(
                com_states[frame] == 1, COM_IDS
            ),
            "com_untracked_joint_ids": joint_list(
                com_states[frame] == 0, COM_IDS
            ),
            "torso_all_tracked": bool(torso_all_tracked[frame]),
            "torso_coordinates_finite": bool(
                np.isfinite(joints[frame, torso_indices]).all()
            ),
        })

    joint_rows = []
    for joint in sorted(set(COM_IDS + TORSO_IDS)):
        states = tracking[:, joint - 1]
        joint_rows.append({
            "joint_id_1based": joint,
            "joint_name": JOINT_NAMES[joint],
            "used_for_com": joint in COM_IDS,
            "used_for_torso": joint in TORSO_IDS,
            "state0_untracked_frames": int(np.sum(states == 0)),
            "state1_inferred_frames": int(np.sum(states == 1)),
            "state2_tracked_frames": int(np.sum(states == 2)),
            "nonfinite_coordinate_frames": int(
                np.sum(~np.isfinite(joints[:, joint - 1]).all(axis=1))
            ),
        })

    write_csv(REPORT_DIR / f"{sample}_frames.csv", frame_rows)
    write_csv(REPORT_DIR / f"{sample}_joints.csv", joint_rows)

    summary = {
        "sample": sample,
        "frames": len(joints),
        "com_all_tracked_frames": int(com_all_tracked.sum()),
        "com_inferred_without_untracked_frames": int(
            com_inferred_only.sum()
        ),
        "com_contains_untracked_frames": int(com_has_untracked.sum()),
        "com_nonfinite_frames": int((~com_finite).sum()),
        "com_all_tracked_percent": round(
            100 * float(com_all_tracked.mean()), 2
        ),
        "torso_all_tracked_frames": int(torso_all_tracked.sum()),
    }

    print(f"\nSample: {sample}")
    print("Frames:", summary["frames"])
    print("COM all tracked:", summary["com_all_tracked_frames"])
    print(
        "COM inferred, no untracked:",
        summary["com_inferred_without_untracked_frames"],
    )
    print(
        "COM contains untracked:",
        summary["com_contains_untracked_frames"],
    )
    print("COM non-finite frames:", summary["com_nonfinite_frames"])
    print("COM all tracked (%):", summary["com_all_tracked_percent"])
    print("Torso all tracked:", summary["torso_all_tracked_frames"])

    return summary


def main():
    if not ARCHIVE.is_file():
        raise FileNotFoundError(f"Archive not found: {ARCHIVE}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    summaries = []

    with ZipFile(ARCHIVE) as archive:
        members = archive.namelist()

        for sample in SAMPLES:
            matches = [
                name for name in members
                if name.rsplit("/", 1)[-1] == f"{sample}.skeleton"
            ]
            if len(matches) != 1:
                raise ValueError(
                    f"{sample}: expected one matching file, "
                    f"found {len(matches)}"
                )

            joints, tracking = read_sample(archive, matches[0])
            summaries.append(audit(sample, joints, tracking))

    write_csv(REPORT_DIR / "summary.csv", summaries)

    print("\nSaved reports to:", REPORT_DIR)
    print("Original ZIP and NPZ files unchanged.")
    print("No frames removed; no interpolation applied.")
    print("Tracking quality does not validate COM accuracy.")
    print("No floor calibration or FPS assumption used.")


if __name__ == "__main__":
    main()
