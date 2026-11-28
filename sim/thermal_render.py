"""Coarse orthographic thermal proxy for E0; not a calibrated MLX90640 model."""

import numpy as np


class ThermalRenderer:
    """Rasterize projected 3D skeleton bones into 24x32 float arrays.

    Camera X/Y projection and fixed scene bounds are explicit approximations.
    Background, person and noise are arbitrary temperature-like pilot values.
    """

    BONES = ((0, 1), (1, 20), (20, 2), (2, 3),
             (20, 4), (4, 5), (5, 6), (6, 7),
             (20, 8), (8, 9), (9, 10), (10, 11),
             (0, 12), (12, 13), (13, 14), (14, 15),
             (0, 16), (16, 17), (17, 18), (18, 19))

    def __init__(self, *, x_bounds=(-1.5, 1.5), y_bounds=(-1.5, 1.5),
                 background=22.0, person=30.0, noise_std=0.2,
                 thickness_pixels=1.5, seed=0):
        self.x_bounds = tuple(x_bounds)
        self.y_bounds = tuple(y_bounds)
        if not (len(self.x_bounds) == len(self.y_bounds) == 2
                and np.all(np.isfinite(self.x_bounds + self.y_bounds))
                and self.x_bounds[0] < self.x_bounds[1]
                and self.y_bounds[0] < self.y_bounds[1]):
            raise ValueError("Finite increasing scene bounds required")
        values = (background, person, noise_std, thickness_pixels)
        if not all(np.isfinite(v) for v in values) or noise_std < 0 or thickness_pixels <= 0:
            raise ValueError("Invalid rendering values")
        self.background = float(background)
        self.person = float(person)
        self.noise_std = float(noise_std)
        self.thickness_pixels = float(thickness_pixels)
        self.rng = np.random.default_rng(seed)

    def render(self, joints):
        """Return (T,24,32) with one fixed scene and no temporal resampling."""
        pose = np.asarray(joints, dtype=float)
        if pose.ndim != 3 or pose.shape[1:] != (25, 3) or len(pose) == 0:
            raise ValueError("joints must have shape (T,25,3), T >= 1")
        if not np.isfinite(pose).all():
            raise ValueError("Non-finite joints")
        x = (pose[:, :, 0] - self.x_bounds[0]) * 31 / (self.x_bounds[1] - self.x_bounds[0])
        y = (self.y_bounds[1] - pose[:, :, 1]) * 23 / (self.y_bounds[1] - self.y_bounds[0])
        row, col = np.mgrid[0:24, 0:32]
        output = np.empty((len(pose), 24, 32), dtype=np.float32)
        for t in range(len(pose)):
            mask = np.zeros((24, 32), dtype=bool)
            for first, second in self.BONES:
                ax, ay, bx, by = x[t, first], y[t, first], x[t, second], y[t, second]
                dx, dy = bx - ax, by - ay
                denom = dx * dx + dy * dy
                u = np.clip(((col - ax) * dx + (row - ay) * dy) / denom, 0, 1) if denom > 0 else 0
                mask |= (col - ax - u * dx) ** 2 + (row - ay - u * dy) ** 2 <= self.thickness_pixels ** 2
            frame = np.full((24, 32), self.background, dtype=np.float32)
            frame[mask] = self.person
            if self.noise_std:
                frame += self.rng.normal(0, self.noise_std, (24, 32)).astype(np.float32)
            output[t] = frame
        return output
