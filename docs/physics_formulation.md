# PhysicsExtractor — Formulation Draft

Source: DiemQuynh_Planning_12_Month_Research_Roadmap.md
Sections: 3.1, 7.2, Sprint 2

Status: DRAFT — NOT YET VALIDATED

## 1. Input [PLANNING]

P(t): sequence of 3D human poses.

Sprint 2 requires:
PhysicsExtractor(joints, fps) -> dict

## 2. Output [PLANNING]

phi(t) = [h, v_z, a_peak, theta, T_ground]

### h(t): Center-of-mass height

c(t): mass-weighted average of body-segment center-of-mass positions.

h(t) = c_z(t)

### v_z(t): Vertical velocity

v_z(t) = dh(t)/dt

### a_peak: Peak acceleration

a_peak = max |d²h(t)/dt²| within a window.

Use numerical differentiation with Savitzky–Golay
smoothing, according to Section 7.2.

### theta(t): Torso angle

Angle between the hip-to-neck vector
and the vertical axis.

### T_ground(t): Ground duration

Continuous duration for which:

h(t) < h_thr

## 3. Unresolved parameters [TBD]

- Body-segment mass weights and COM locations.
- Joint mapping for each skeleton format.
- Mapping each source dataset to the required coordinate convention: meters, z-axis pointing upward.
- Savitzky–Golay window and polynomial order.
- Ground-height threshold h_thr.
- Exact window definition for peak acceleration.

These must be sourced and verified before
using PhysicsExtractor for research experiments.

## 4. Implementation status

- [x] Preliminary vertical-kinematics helper.
- [x] Synthetic free-fall helper test.
- [ ] PhysicsExtractor accepting 3D joints.
- [ ] Five physics outputs validated.
- [ ] Configuration values sourced.
- [ ] Tests for full PhysicsExtractor.
- [ ] Reviewed and pushed to GitHub.

## 5. My understanding of Section 3.1

Kí hiệu:

- Student: mô hình nhỏ, chạy được trên thiết bị biên (edge), là mô hình cuối cùng dùng để phát hiện ngã.
- Teacher: mô hình hướng dẫn student trong lúc huấn luyện, sử dụng thông tin đặc quyền như pose 3D.
- Xth : chuỗi ảnh nhiệt (vì té ngã là chuỗi các hoạt động), mỗi ảnh 24x32 điểm, tốc độ thấp (2-8 Hz).
- Xrd: chuỗi dữ liệu radar (point cloud hoặc micro-Doppler), nhanh hơn (8-20Hz).
- [t-W, t]: cửa sổ thời gian trượt, mô hình chỉ nhìn W giây gần nhất, t là thời điểm, có nghĩa là mô hình nhìn trong khoảng W giây, lấy từ thời điểm t-W giây đến thời điểm t đó.

Input ( trong cửa sổ [t-W, t] ):

- Chuỗi ảnh nhiệt 24x32, tần số thấp và có timestamp riêng.
- Chuỗi radar ( mỗi điểm gồm vị trí x,y,z trên trục tọa độ, vận tốc Doppler v_D, SNR là tỉ số tín hiệu trên nhiễu, cho biết mức tín hiệu so với nhiễu), tần số cao hơn nên nhanh hơn.

(x, y, z, v_D, SNR là mô tả point cloud, không áp dụng nguyên dạng cho micro-Doppler)

- Đo được trên dữ liệu Taramasco:
  - Thermal thực tế≈ 2,6 Hz: khoảng 2,6 khung/giây.
  - Radar ≈ 8,3 Hz: khoảng 8,3 khung/giây.

Hai luồng lấy mẫu với tốc độ khác nhau nên cần dựa vào timestamp để ghép dữ liệu theo thời gian.

Output:

- p(fall ∣ Xth, Xrd) : xác suất xảy ra té ngã khi biết đồng thời dữ liệu ảnh nhiệt và radar.
- Thời điểm báo động dự đoán.
- φ̂(t): là các đại lượng vật lý do student dự đoán, gồm độ cao trọng tâm h, vận tốc theo phương thẳng đứng v_z ( theo trục z), độ lớn gia tốc thẳng đứng lớn nhất trong cửa sổ a_peak, góc thân người θ, thời gian liên tục trọng tâm ở dưới ngưỡng h_thr là T_ground.

Vai trò của teacher và đặc trưng vật lý:

- Thông tin đặc quyền (privileged information): là data chỉ có lúc huấn luyện, chuỗi pose 3D P(t), lấy từ RGB thật hoặc ground-truth của mô phỏng, giống như đáp án chi tiết của giáo viên và học sinh không được phép mang vào phòng thi.
- Teacher nhìn thấy P(t) nên hiểu rõ chuyển động cơ thể, học sinh nhận kiến thức đó từ teacher và học. Đây là ý tưởng knowledge distillation.

Đặc trưng vật lý (h, v_z, a_peak, θ, T_ground) được tính từ pose 3D để hỗ trợ huấn luyện. Student học từ teacher và học dự đoán các đại lượng vật lý từ ảnh nhiệt và radar. Hiệu quả của cách học này cần được kiểm chứng bằng thực nghiệm.

Các ràng buộc: không dùng pose/RGB khi suy luận; chạy trong giới hạn tài nguyên thiết bị biên; mục tiêu độ trễ báo động không quá 1,5 giây sau thời điểm va chạm.
