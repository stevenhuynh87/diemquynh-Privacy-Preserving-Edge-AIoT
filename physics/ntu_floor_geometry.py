"""Convert NTU camera coordinates using an externally calibrated floor."""

import numpy as np


def camera_to_floor_z_up(joints_camera_m, floor_normal_camera, floor_offset_m):
    """Return a pose whose z is signed height above the floor, in metres.

    The floor plane is n dot p + d = 0 in camera coordinates.
    n must be a unit vector pointing upward; d is floor_offset_m.

    The caller must supply a measured/calibrated plane. This function
    neither estimates the floor from foot joints nor interprets the
    Kinect SDK's FloorClipPlane w value.
    """
    pose = np.asarray(joints_camera_m, dtype=float)
    normal = np.asarray(floor_normal_camera, dtype=float)
    offset = np.asarray(floor_offset_m, dtype=float)

    if pose.ndim != 3 or pose.shape[1:] != (25, 3) or len(pose) == 0:
        raise ValueError(
            "joints_camera_m must have shape (T, 25, 3), T >= 1"
        )
    if not np.isfinite(pose).all():
        raise ValueError("joints_camera_m must be finite")
    if normal.shape != (3,) or not np.isfinite(normal).all():
        raise ValueError("floor_normal_camera must be a finite 3-vector")
    if not np.isclose(
        np.linalg.norm(normal), 1.0, rtol=0, atol=1e-6
    ):
        raise ValueError("floor_normal_camera must have unit length")
    if offset.shape != () or not np.isfinite(offset):
        raise ValueError("floor_offset_m must be a finite scalar")

    reference = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(reference, normal)) > 0.9:
        reference = np.array([0.0, 0.0, 1.0])

    axis_x = reference - np.dot(reference, normal) * normal
    axis_x /= np.linalg.norm(axis_x)
    axis_y = np.cross(normal, axis_x)
    axis_y /= np.linalg.norm(axis_y)

    result = np.empty_like(pose)
    result[:, :, 0] = pose @ axis_x
    result[:, :, 1] = pose @ axis_y
    result[:, :, 2] = pose @ normal + float(offset)
    return result
