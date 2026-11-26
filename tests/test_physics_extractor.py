import numpy as np
import pytest

from physics.extractor import extract_vertical_kinematics


def test_free_fall():
    """Kiểm tra đạo hàm Savitzky-Golay trên rơi tự do lý tưởng."""
    fps = 10
    g = 9.81
    t = np.arange(5) / fps

    height = 2.0 - 0.5 * g * t**2

    # Tham số đề xuất cho test tổng hợp, chưa chốt cho clip thật.
    result = extract_vertical_kinematics(
        height,
        fps,
        window_length=5,
        polyorder=2,
    )

    expected_velocity = -g * t
    expected_acceleration = np.full(5, -g)

    velocity_error = np.max(
        np.abs(result["vertical_velocity_m_s"] - expected_velocity)
    )
    acceleration_error = np.max(
        np.abs(
            result["vertical_acceleration_m_s2"]
            - expected_acceleration
        )
    )

    print(f"\nMax velocity error: {velocity_error:.3e} m/s")
    print(f"Max acceleration error: {acceleration_error:.3e} m/s^2")

    # Sai số tuyệt đối cho dữ liệu lý tưởng, không nhiễu.
    np.testing.assert_allclose(
        result["vertical_velocity_m_s"],
        expected_velocity,
        rtol=0,
        atol=1e-8,
    )

    np.testing.assert_allclose(
        result["vertical_acceleration_m_s2"],
        expected_acceleration,
        rtol=0,
        atol=1e-8,
    )
    # Rơi tự do lý tưởng: gia tốc = -g, nên độ lớn đỉnh = g.
    np.testing.assert_allclose(
        result["a_peak_m_s2"],
        g,
        rtol=0,
        atol=1e-8,
    )

def test_invalid_fps():
    """FPS phải lớn hơn 0."""
    with pytest.raises(ValueError, match="fps"):
        extract_vertical_kinematics(
            [2.0, 1.9, 1.6],
            0,
            window_length=3,
            polyorder=2,
        )

def test_com_elbow_contribution():
    """Kiểm tra ID khớp, chiều hệ số và đóng góp của hai đoạn."""
    from physics.extractor import estimate_ntu_com_winter14

    pose = np.zeros((1, 25, 3))

    # Chỉ khuỷu trái (khớp 6) có x = 1 mét.
    # Đây là dữ liệu nhân tạo kiểm tra phép tính, không phải pose thật.
    pose[0, 5, 0] = 1.0

    result = estimate_ntu_com_winter14(pose)

    # Khuỷu là đầu cuối cánh tay trên và đầu đầu cẳng tay.
    expected_x = 0.028 * 0.436 + 0.016 * (1.0 - 0.430)

    np.testing.assert_allclose(
        result["com_m"],
        [[expected_x, 0.0, 0.0]],
        rtol=0,
        atol=1e-12,
    )

    assert len(result["segment_com_m"]) == 14


def test_com_translation():
    """Dịch toàn bộ khớp một vector thì trọng tâm dịch cùng vector."""
    from physics.extractor import estimate_ntu_com_winter14

    rng = np.random.default_rng(0)
    pose = rng.normal(size=(3, 25, 3))
    shift = np.array([1.2, -0.4, 2.0])

    original = estimate_ntu_com_winter14(pose)["com_m"]
    translated = estimate_ntu_com_winter14(pose + shift)["com_m"]

    np.testing.assert_allclose(
        translated,
        original + shift,
        rtol=0,
        atol=1e-12,
    )

def test_torso_angle_known_directions():
    """Vector thân hướng lên, ngang, hướng xuống: 0, 90, 180 độ."""
    from physics.extractor import extract_ntu_torso_angle

    pose = np.zeros((3, 25, 3))

    # Hai hông đối xứng, trung điểm ở gốc tọa độ.
    pose[:, 12, :] = [-0.1, 0.0, 0.0]
    pose[:, 16, :] = [0.1, 0.0, 0.0]

    # Vị trí cổ ở ba trường hợp tổng hợp.
    pose[0, 2, :] = [0.0, 0.0, 1.0]
    pose[1, 2, :] = [1.0, 0.0, 0.0]
    pose[2, 2, :] = [0.0, 0.0, -1.0]

    theta = extract_ntu_torso_angle(pose)

    np.testing.assert_allclose(
        theta,
        [0.0, np.pi / 2, np.pi],
        rtol=0,
        atol=1e-12,
    )


def test_torso_angle_zero_vector():
    """Hông trùng cổ thì không xác định được góc."""
    from physics.extractor import extract_ntu_torso_angle

    pose = np.zeros((1, 25, 3))

    with pytest.raises(ValueError, match="nonzero"):
        extract_ntu_torso_angle(pose)

def test_ground_duration_reset_and_threshold():
    """Đếm thời gian dưới ngưỡng và đặt lại khi bằng ngưỡng."""
    from physics.extractor import extract_ground_duration

    height = [0.8, 0.3, 0.2, 0.1, 0.5, 0.2, 0.1]

    result = extract_ground_duration(
        height,
        fps=10,
        h_thr=0.5,
    )

    np.testing.assert_allclose(
        result,
        [0.0, 0.0, 0.1, 0.2, 0.0, 0.0, 0.1],
        rtol=0,
        atol=1e-12,
    )


def test_ground_duration_starts_below_threshold():
    """Nếu clip bắt đầu dưới ngưỡng, chỉ đếm từ đầu clip."""
    from physics.extractor import extract_ground_duration

    result = extract_ground_duration(
        [0.2, 0.2, 0.2],
        fps=10,
        h_thr=0.5,
    )

    np.testing.assert_allclose(
        result,
        [0.0, 0.1, 0.2],
        rtol=0,
        atol=1e-12,
    )

def test_full_extractor_synthetic_free_fall():
    """Kiểm tra đủ 5 đầu ra trên chuỗi khớp tổng hợp."""
    from physics.extractor import PhysicsExtractor

    fps = 10
    g = 9.81
    t = np.arange(5) / fps

    pose = np.zeros((5, 25, 3))

    # Hông ở gốc, cổ phía trên hông để vector thân khác 0.
    pose[:, 2, 2] = 1.0
    pose[:, 3, 2] = 2.0

    # Dịch tất cả khớp cùng một quỹ đạo thẳng đứng.
    translation_z = 2.0 - 0.5 * g * t**2
    pose[:, :, 2] += translation_z[:, None]

    result = PhysicsExtractor(
        pose,
        fps,
        window_length=5,
        polyorder=2,
        h_thr=2.12,  # Chỉ dùng cho test tổng hợp.
    )

    # Ở cấu hình ban đầu, chỉ đầu-cổ đóng góp COM theo z:
    # khối lượng 0.081, vị trí Head z = 2.0.
    expected_height = translation_z + 0.081 * 2.0

    expected = {
        "h": expected_height,
        "v_z": -g * t,
        "a_peak": g,
        "theta": np.zeros(5),
        "T_ground": np.array([0.0, 0.0, 0.1, 0.2, 0.3]),
    }

    for key, expected_value in expected.items():
        np.testing.assert_allclose(
            result[key],
            expected_value,
            rtol=0,
            atol=1e-8,
            err_msg=f"Incorrect output: {key}",
        )

def test_full_extractor_height_reference_shift():
    """Kiểm tra PhysicsExtractor khi thay đổi mốc độ cao."""
    from physics.extractor import PhysicsExtractor

    pose = np.zeros((9, 25, 3))
    pose[:, :, 2] = np.linspace(1.0, 0.2, 9)[:, None]
    pose[:, 2, 2] += 0.5

    original = PhysicsExtractor(
        pose,
        10,
        window_length=5,
        polyorder=2,
        h_thr=0.55,
    )

    shifted_pose = pose.copy()
    shifted_pose[:, :, 2] += 1.0

    shifted = PhysicsExtractor(
        shifted_pose,
        10,
        window_length=5,
        polyorder=2,
        h_thr=1.55,
    )

    np.testing.assert_allclose(
        shifted["h"], original["h"] + 1.0, atol=1e-10
    )
    np.testing.assert_allclose(
        shifted["v_z"], original["v_z"], atol=1e-10
    )
    np.testing.assert_allclose(
        shifted["a_peak"], original["a_peak"], atol=1e-10
    )
    np.testing.assert_allclose(
        shifted["theta"], original["theta"], atol=1e-10
    )
    np.testing.assert_allclose(
        shifted["T_ground"], original["T_ground"], atol=1e-10
    )
