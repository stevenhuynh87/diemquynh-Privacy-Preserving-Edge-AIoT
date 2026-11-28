"""E0 geometric radar proxy; no RF propagation or sensor chirp model."""

import numpy as np


class RadarSimL2:
    """Sample bone points and compute radial velocity relative to a sensor.

    Output is (T,N,4): camera x,y,z in metres and signed radial m/s.
    Positive radial velocity means moving away from the sensor.
    This skeleton-line approximation is not a sampled body surface.
    """

    BONES = ((0, 1), (1, 20), (20, 2), (2, 3),
             (20, 4), (4, 5), (5, 6), (6, 7),
             (20, 8), (8, 9), (9, 10), (10, 11),
             (0, 12), (12, 13), (13, 14), (14, 15),
             (0, 16), (16, 17), (17, 18), (18, 19))

    def __init__(self, *, sensor_origin=(0.0, 0.0, 0.0), points_per_bone=3):
        self.sensor_origin = np.asarray(sensor_origin, dtype=float)
        if self.sensor_origin.shape != (3,) or not np.isfinite(self.sensor_origin).all():
            raise ValueError("sensor_origin must be finite XYZ")
        if isinstance(points_per_bone, bool) or not isinstance(points_per_bone, int) or points_per_bone < 2:
            raise ValueError("points_per_bone must be integer >= 2")
        self.points_per_bone = points_per_bone

    def simulate(self, joints, fps):
        pose = np.asarray(joints, dtype=float)
        if pose.ndim != 3 or pose.shape[1:] != (25, 3) or len(pose) < 2:
            raise ValueError("joints must be (T,25,3), T >= 2")
        if not np.isfinite(pose).all() or not np.isfinite(fps) or fps <= 0:
            raise ValueError("Finite joints and positive fps required")
        a, b = np.array(self.BONES).T
        ratio = np.linspace(0, 1, self.points_per_bone)
        points = ((1 - ratio)[None, None, :, None] * pose[:, a, None, :]
                  + ratio[None, None, :, None] * pose[:, b, None, :])
        points = points.reshape(len(pose), -1, 3)
        velocity = np.gradient(points, 1 / fps, axis=0)
        direction = points - self.sensor_origin
        radius = np.linalg.norm(direction, axis=2)
        unit = np.divide(direction, radius[:, :, None],
                         out=np.zeros_like(direction),
                         where=radius[:, :, None] > 0)
        radial = np.sum(velocity * unit, axis=2)
        return np.concatenate((points, radial[:, :, None]), axis=2).astype(np.float32)
