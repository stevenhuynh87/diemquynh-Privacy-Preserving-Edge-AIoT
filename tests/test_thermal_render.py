import numpy as np
import pytest

from sim.thermal_render import ThermalRenderer


def test_fixed_scene_and_warm_skeleton():
    pose = np.zeros((2, 25, 3))
    pose[:, :, 0] = 0
    pose[:, :, 1] = 0
    renderer = ThermalRenderer(noise_std=0)
    frames = renderer.render(pose)
    assert frames.shape == (2, 24, 32)
    assert frames.dtype == np.float32
    assert np.any(frames[0] == 30)
    assert np.any(frames[0] == 22)
    np.testing.assert_array_equal(frames[0], frames[1])


def test_projection_and_reproducible_noise():
    pose = np.zeros((1, 25, 3))
    pose[:, :, 0] = 0.5
    left = ThermalRenderer(seed=9).render(pose)
    right = ThermalRenderer(seed=9).render(pose)
    np.testing.assert_array_equal(left, right)
    assert np.isfinite(left).all()


def test_rejects_invalid_input():
    with pytest.raises(ValueError, match="shape"):
        ThermalRenderer().render(np.zeros((3, 17, 3)))
    with pytest.raises(ValueError, match="Non-finite"):
        ThermalRenderer().render(np.full((1, 25, 3), np.nan))
