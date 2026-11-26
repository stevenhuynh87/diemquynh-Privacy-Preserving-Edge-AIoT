import numpy as np
import pytest

from physics.ntu_quality import assess_ntu_tracking


def test_com_and_torso_flags_are_independent():
    pose = np.zeros((3, 25, 3))
    states = np.full((3, 25), 2, dtype=np.int8)

    states[1, 4] = 1   # ShoulderLeft: used by COM, not torso angle.
    states[2, 2] = 0   # Neck: used by torso angle, not COM.

    result = assess_ntu_tracking(pose, states)

    np.testing.assert_array_equal(
        result["com_all_tracked"], [True, False, True]
    )
    np.testing.assert_array_equal(
        result["com_has_inferred"], [False, True, False]
    )
    np.testing.assert_array_equal(
        result["com_has_untracked"], [False, False, False]
    )
    np.testing.assert_array_equal(
        result["torso_all_tracked"], [True, True, False]
    )


def test_nonfinite_com_joint_is_reported():
    pose = np.zeros((1, 25, 3))
    pose[0, 3, 1] = np.nan  # Head, NTU joint 4.
    states = np.full((1, 25), 2, dtype=np.int8)

    result = assess_ntu_tracking(pose, states)
    assert result["com_all_tracked"][0]
    assert not result["com_joints_finite"][0]
    assert result["torso_joints_finite"][0]


def test_invalid_tracking_shape_rejected():
    with pytest.raises(ValueError, match="tracking_state"):
        assess_ntu_tracking(
            np.zeros((2, 25, 3)),
            np.zeros((1, 25)),
        )


def test_wrapper_attaches_quality_without_changing_physics():
    from physics.extractor import PhysicsExtractor
    from physics.ntu_quality import physics_extractor_with_tracking

    fps = 10
    times = np.arange(5) / fps
    pose = np.zeros((5, 25, 3))
    pose[:, 2, 2] = 1.0  # Neck above hips.
    pose[:, 3, 2] = 2.0  # Head.
    pose[:, :, 2] += (2.0 - 0.5 * 9.81 * times**2)[:, None]

    states = np.full((5, 25), 2, dtype=np.int8)
    states[2, 7] = 1  # HandLeft inferred only at frame 3.

    kwargs = dict(window_length=5, polyorder=2, h_thr=2.12)
    plain = PhysicsExtractor(pose, fps, **kwargs)
    audited = physics_extractor_with_tracking(
        pose, fps, states, **kwargs
    )

    for key in ("h", "v_z", "a_peak", "theta", "T_ground"):
        np.testing.assert_allclose(audited[key], plain[key])

    np.testing.assert_array_equal(
        audited["tracking_quality"]["com_all_tracked"],
        [True, True, False, True, True],
    )
    np.testing.assert_array_equal(
        audited["tracking_quality"]["torso_all_tracked"],
        [True, True, True, True, True],
    )
