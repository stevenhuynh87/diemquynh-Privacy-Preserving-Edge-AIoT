
import numpy as np
from scipy.signal import savgol_filter


def extract_vertical_kinematics(
    height_m, fps, *, window_length, polyorder
):
    """
    Tính vận tốc và gia tốc thẳng đứng.

    Quy ước:
    - Trục z hướng lên.
    - Độ cao tính bằng mét.
    - Các mẫu cách đều nhau: dt = 1/fps.
    - Dùng Savitzky-Golay để tính đạo hàm.
    - a_peak được tính trên toàn bộ chuỗi đầu vào.
    """

    if not np.isfinite(fps) or fps <= 0:
        raise ValueError("fps must be finite and positive")

    height = np.asarray(height_m, dtype=float)

    if height.ndim != 1 or len(height) < 3:
        raise ValueError(
            "At least 3 height samples are required"
        )

    if not np.all(np.isfinite(height)):
        raise ValueError("Height samples must be finite")

    if not isinstance(window_length, (int, np.integer)):
        raise ValueError(
            "window_length must be an integer"
        )

    if (
        window_length < 3
        or window_length % 2 == 0
        or window_length > len(height)
    ):
        raise ValueError(
            "window_length must be odd, >= 3, "
            "and <= sample count"
        )

    if not isinstance(polyorder, (int, np.integer)):
        raise ValueError(
            "polyorder must be an integer"
        )

    if not 2 <= polyorder < window_length:
        raise ValueError(
            "Require 2 <= polyorder < window_length"
        )

    dt = 1.0 / fps

    velocity = savgol_filter(
        height,
        window_length=window_length,
        polyorder=polyorder,
        deriv=1,
        delta=dt,
        mode="interp",
    )

    acceleration = savgol_filter(
        height,
        window_length=window_length,
        polyorder=polyorder,
        deriv=2,
        delta=dt,
        mode="interp",
    )

    a_peak = float(np.max(np.abs(acceleration)))

    return {
        "height_m": height,
        "vertical_velocity_m_s": velocity,
        "vertical_acceleration_m_s2": acceleration,
        "a_peak_m_s2": a_peak,
    }


def estimate_ntu_com_winter14(joints):
    """
    Ước lượng trọng tâm cơ thể từ pose NTU 25 khớp.

    Input:
    - joints: (T, 25, 3), đơn vị mét.

    Nguồn hệ số:
    - Winter (2009), bảng 4.1.

    Ánh xạ NTU -> các đoạn cơ thể là xấp xỉ.

    Giới hạn:
    - Chưa xác thực trên dữ liệu thực.
    - Không tự chuyển hệ tọa độ.
    - Không tự hiệu chỉnh mặt sàn.
    - Không xử lý tracking state.
    """

    pose = np.asarray(joints, dtype=float)

    if (
        pose.ndim != 3
        or pose.shape[1:] != (25, 3)
        or pose.shape[0] == 0
    ):
        raise ValueError(
            "joints must have shape (T, 25, 3), T >= 1"
        )

    if not np.all(np.isfinite(pose)):
        raise ValueError(
            "Joint coordinates must be finite"
        )

    # NTU joint IDs bắt đầu từ 1.
    # (name, start_id, end_id, ratio, mass_fraction)

    limb_specs = [
        ("upper_arm_left", 5, 6, 0.436, 0.028),
        ("upper_arm_right", 9, 10, 0.436, 0.028),
        ("forearm_left", 6, 7, 0.430, 0.016),
        ("forearm_right", 10, 11, 0.430, 0.016),
        ("hand_left", 7, 8, 0.506, 0.006),
        ("hand_right", 11, 12, 0.506, 0.006),
        ("thigh_left", 13, 14, 0.433, 0.100),
        ("thigh_right", 17, 18, 0.433, 0.100),
        ("shank_left", 14, 15, 0.433, 0.0465),
        ("shank_right", 18, 19, 0.433, 0.0465),
        ("foot_left", 15, 16, 0.500, 0.0145),
        ("foot_right", 19, 20, 0.500, 0.0145),
    ]

    segment_com = {}
    mass_fractions = {}

    for name, start_id, end_id, ratio, weight in limb_specs:

        start = pose[:, start_id - 1, :]
        end = pose[:, end_id - 1, :]

        segment_com[name] = (
            start + ratio * (end - start)
        )

        mass_fractions[name] = weight

    # Trung điểm hai hông
    hip_midpoint = 0.5 * (
        pose[:, 12, :] + pose[:, 16, :]
    )

    # Trung điểm hai vai
    shoulder_midpoint = 0.5 * (
        pose[:, 4, :] + pose[:, 8, :]
    )

    # Trọng tâm thân (xấp xỉ)
    segment_com["trunk"] = 0.5 * (
        hip_midpoint + shoulder_midpoint
    )

    mass_fractions["trunk"] = 0.497

    # Head đại diện cho trọng tâm đoạn đầu-cổ
    segment_com["head_neck"] = pose[:, 3, :].copy()
    mass_fractions["head_neck"] = 0.081

    total_weight = sum(mass_fractions.values())

    if not np.isclose(
        total_weight, 1.0, rtol=0, atol=1e-12
    ):
        raise ValueError(
            "Segment mass fractions must sum to 1"
        )

    com = np.zeros(
        (pose.shape[0], 3),
        dtype=float,
    )

    for name, positions in segment_com.items():
        com += mass_fractions[name] * positions

    return {
        "com_m": com,
        "segment_com_m": segment_com,
        "mass_fractions": mass_fractions,
        "model": "NTU_Winter14_approximation",
        "validated_on_real_data": False,
    }


def extract_ntu_torso_angle(joints_z_up):
    """
    Tính góc thân so với trục z hướng lên.

    Input:
    - joints_z_up: (T, 25, 3), đơn vị mét.

    Vector thân:
    - Trung điểm HipLeft và HipRight -> Neck.

    Output:
    - theta, đơn vị radian.

    Hàm không tự chuyển hệ tọa độ camera.
    """

    pose = np.asarray(joints_z_up, dtype=float)

    if (
        pose.ndim != 3
        or pose.shape[1:] != (25, 3)
        or pose.shape[0] == 0
    ):
        raise ValueError(
            "joints must have shape (T, 25, 3), T >= 1"
        )

    if not np.all(np.isfinite(pose)):
        raise ValueError(
            "Joint coordinates must be finite"
        )

    hip = 0.5 * (
        pose[:, 12, :] + pose[:, 16, :]
    )

    neck = pose[:, 2, :]

    torso = neck - hip

    lengths = np.linalg.norm(torso, axis=1)

    if np.any(lengths == 0):
        raise ValueError(
            "Hip-to-neck vector must be nonzero"
        )

    cosine = torso[:, 2] / lengths

    theta_rad = np.arccos(
        np.clip(cosine, -1.0, 1.0)
    )

    return theta_rad


def extract_ground_duration(height_m, fps, *, h_thr):
    """
    Tính thời gian liên tục h(t) < h_thr.

    Input:
    - height_m: chuỗi độ cao COM.
    - fps: số khung hình mỗi giây.
    - h_thr: ngưỡng độ cao cùng mốc với height_m.

    Quy ước:
    - Frame đầu tiên dưới ngưỡng: 0 giây.
    - Các frame tiếp theo: cộng 1/fps.
    - Khi h >= h_thr: đặt lại 0.
    - Không nội suy thời điểm vượt ngưỡng.

    Output:
    - Mảng thời gian, đơn vị giây.
    """

    if not np.isfinite(fps) or fps <= 0:
        raise ValueError(
            "fps must be finite and positive"
        )

    if not np.isfinite(h_thr):
        raise ValueError(
            "h_thr must be finite"
        )

    height = np.asarray(height_m, dtype=float)

    if height.ndim != 1 or height.size == 0:
        raise ValueError(
            "height_m must be a nonempty 1D array"
        )

    if not np.all(np.isfinite(height)):
        raise ValueError(
            "Height samples must be finite"
        )

    duration_s = np.zeros(
        height.size,
        dtype=float,
    )

    start_index = None

    for index, value in enumerate(height):

        if value < h_thr:

            if start_index is None:
                start_index = index

            duration_s[index] = (
                index - start_index
            ) / fps

        else:
            start_index = None

    return duration_s


def PhysicsExtractor(
    joints,
    fps,
    *,
    window_length=None,
    polyorder=2,
    h_thr=None,
):
    """
    PhysicsExtractor cho NTU 25 khớp.

    Input:
    - joints: (T, 25, 3), đơn vị mét.
    - Trục z hướng lên.
    - fps: tần số lấy mẫu.
    - window_length: cửa sổ Savitzky-Golay.
    - polyorder: bậc đa thức.
    - h_thr: ngưỡng độ cao COM, đơn vị mét.

    Các đại lượng theo Planning:
    1. h: độ cao COM theo trục z.
    2. v_z: vận tốc thẳng đứng.
    3. a_peak: gia tốc đỉnh.
    4. theta: góc thân với phương thẳng đứng.
    5. T_ground: thời gian liên tục dưới ngưỡng.

    Quy ước triển khai do trợ lý đề xuất:
    - polyorder mặc định bằng 2.
    - window_length mặc định tối đa 7 frame,
      là số lẻ và không vượt số frame đầu vào.
    - h_thr=None nếu chưa cấu hình ngưỡng.
    - Nếu h_thr=None thì T_ground=None.
    - h_thr phải cùng hệ tọa độ và mốc độ cao
      với joints.
    - Toàn bộ chuỗi là cửa sổ tính a_peak.

    Giới hạn:
    - Cần ít nhất 3 frame.
    - Chưa xử lý tracking state.
    - Chưa tự hiệu chỉnh mặt sàn.
    - h là tọa độ COM theo z; chỉ là chiều cao
      so với sàn khi mốc tọa độ được xác định.
    - COM là mô hình NTU-Winter14 xấp xỉ.
    - h_thr chưa được hiệu chuẩn trên dữ liệu thật.
    """

    # 1. Tính trọng tâm cơ thể
    com_result = estimate_ntu_com_winter14(joints)

    com = com_result["com_m"]

    # 2. Độ cao COM
    height = com[:, 2]

    # 3. Cấu hình Savitzky-Golay mặc định
    if window_length is None:

        n_frames = len(height)

        window_length = min(
            7,
            n_frames if n_frames % 2 == 1
            else n_frames - 1,
        )

    # 4. Tính vận tốc và gia tốc
    kinematics = extract_vertical_kinematics(
        height,
        fps,
        window_length=window_length,
        polyorder=polyorder,
    )

    acceleration = kinematics[
        "vertical_acceleration_m_s2"
    ]

    # 5. Tính góc thân
    theta = extract_ntu_torso_angle(joints)

    # 6. Tính thời gian dưới ngưỡng
    if h_thr is None:

        ground_duration = None
        ground_status = "threshold_not_configured"

    else:

        ground_duration = extract_ground_duration(
            height,
            fps,
            h_thr=h_thr,
        )

        ground_status = (
            "computed_with_supplied_threshold"
        )

    # 7. Trả về kết quả
    return {
        "h": height,
        "v_z": kinematics[
            "vertical_velocity_m_s"
        ],
        "a_peak": float(
            np.max(np.abs(acceleration))
        ),
        "theta": theta,
        "T_ground": ground_duration,
        "com_m": com,
        "vertical_acceleration_m_s2": acceleration,
        "metadata": {
            "body_model": com_result["model"],
            "validated_on_real_data": False,
            "fps": float(fps),
            "sg_window_length": int(window_length),
            "sg_polyorder": int(polyorder),
            "h_thr_m": (
                None if h_thr is None
                else float(h_thr)
            ),
            "T_ground_status": ground_status,
            "a_peak_window": "entire_input_sequence",
            "theta_unit": "rad",
            "ground_duration_unit": "s",
        },
    }
