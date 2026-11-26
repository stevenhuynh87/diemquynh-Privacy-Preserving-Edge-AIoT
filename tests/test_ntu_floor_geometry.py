import numpy as np
import pytest

from physics.ntu_floor_geometry import camera_to_floor_z_up


def test_horizontal_floor_sets_height_zero_at_floor():
    pose = np.zeros((2, 25, 3))
    pose[:, :, 1] = -0.6
    pose[:, 2, 1] = 0.4  # Neck is 1 m above floor.

    result = camera_to_floor_z_up(
        pose,
        floor_normal_camera=[0.0, 1.0, 0.0],
        floor_offset_m=0.6,
    )

    np.testing.assert_allclose(result[:, 0, 2], [0.0, 0.0])
    np.testing.assert_allclose(result[:, 2, 2], [1.0, 1.0])


def test_tilted_floor_preserves_height_under_tangent_shift():
    normal = np.array([0.0, 1.0, 1.0]) / np.sqrt(2)
    offset = 0.4
    floor_point = -offset * normal

    pose = np.broadcast_to(
        floor_point + 1.2 * normal, (1, 25, 3)
    ).copy()
    shifted = pose + np.array([0.7, 0.0, 0.0])

    first = camera_to_floor_z_up(pose, normal, offset)
    second = camera_to_floor_z_up(shifted, normal, offset)

    np.testing.assert_allclose(first[:, :, 2], 1.2, atol=1e-12)
    np.testing.assert_allclose(second[:, :, 2], 1.2, atol=1e-12)


def test_missing_or_invalid_plane_is_rejected():
    pose = np.zeros((1, 25, 3))

    with pytest.raises(ValueError, match="unit length"):
        camera_to_floor_z_up(pose, [0.0, 2.0, 0.0], 0.6)

    with pytest.raises(ValueError, match="finite scalar"):
        camera_to_floor_z_up(pose, [0.0, 1.0, 0.0], np.nan)
