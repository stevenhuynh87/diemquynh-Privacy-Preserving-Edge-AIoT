"""Per-frame quality flags for the NTU 25-joint physics approximation."""

import numpy as np


# One-based NTU IDs used by estimate_ntu_com_winter14:
# Head 4 and joints 5-20.
COM_JOINTS = np.arange(3, 20)

# One-based NTU IDs used by extract_ntu_torso_angle:
# Neck 3, HipLeft 13, HipRight 17.
TORSO_JOINTS = np.array([2, 12, 16])


def assess_ntu_tracking(joints, tracking_state):
    """Report tracking evidence without changing pose or COM values.

    Tracking state: 0=untracked, 1=inferred, 2=tracked.
    An all-tracked frame is not proof that its coordinates are accurate.
    """
    pose = np.asarray(joints, dtype=float)
    states = np.asarray(tracking_state)

    if pose.ndim != 3 or pose.shape[1:] != (25, 3) or len(pose) == 0:
        raise ValueError("joints must have shape (T, 25, 3), T >= 1")
    if states.shape != (len(pose), 25):
        raise ValueError("tracking_state must have shape (T, 25)")
    if not np.isin(states, (0, 1, 2)).all():
        raise ValueError("tracking_state must contain only 0, 1, or 2")

    com_states = states[:, COM_JOINTS]
    torso_states = states[:, TORSO_JOINTS]

    return {
        "com_all_tracked": np.all(com_states == 2, axis=1),
        "com_has_inferred": np.any(com_states == 1, axis=1),
        "com_has_untracked": np.any(com_states == 0, axis=1),
        "com_joints_finite": np.isfinite(
            pose[:, COM_JOINTS, :]
        ).all(axis=(1, 2)),
        "torso_all_tracked": np.all(torso_states == 2, axis=1),
        "torso_joints_finite": np.isfinite(
            pose[:, TORSO_JOINTS, :]
        ).all(axis=(1, 2)),
    }


def physics_extractor_with_tracking(
    joints_z_up,
    fps,
    tracking_state,
    *,
    window_length,
    polyorder,
    h_thr,
):
    """Run the prototype extractor and attach per-frame NTU quality flags.

    joints_z_up must already be in metres with z pointing up and
    the floor at z=0. This function does not calibrate NTU camera data.
    Tracking flags are diagnostic; they do not correct inferred joints.
    """
    from physics.extractor import PhysicsExtractor

    quality = assess_ntu_tracking(joints_z_up, tracking_state)
    result = PhysicsExtractor(
        joints_z_up,
        fps,
        window_length=window_length,
        polyorder=polyorder,
        h_thr=h_thr,
    )
    result["tracking_quality"] = quality
    return result
