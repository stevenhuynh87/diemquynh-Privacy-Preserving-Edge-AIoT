import numpy as np
import pytest

from sim.radar_sim import RadarSimL2


def test_radial_motion_and_shape():
    pose = np.zeros((5, 25, 3))
    pose[:, :, 2] = 2 + np.arange(5)[:, None] / 10
    cloud = RadarSimL2(sensor_origin=(0, 0, 0)).simulate(pose, fps=10)
    assert cloud.shape == (5, 20 * 3, 4)
    np.testing.assert_allclose(cloud[:, :, 3], 1, atol=1e-5)


def test_stationary_and_invalid_fps():
    pose = np.ones((5, 25, 3))
    cloud = RadarSimL2().simulate(pose, fps=10)
    np.testing.assert_allclose(cloud[:, :, 3], 0, atol=1e-6)
    with pytest.raises(ValueError, match="fps"):
        RadarSimL2().simulate(pose, fps=0)
