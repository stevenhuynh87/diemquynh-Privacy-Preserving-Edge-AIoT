# PhysicsExtractor — Bản nháp công thức và diễn giải

Nguồn: DiemQuynh_Planning_12_Month_Research_Roadmap.md
Các mục liên quan: 3.1, 7.2, Sprint 2
Yêu cầu bổ sung: Nhận xét của thầy ngày 22/11/2026

Trạng thái: BẢN NHÁP — CHƯA ĐƯỢC THẨM ĐỊNH

## 1. Đầu vào của PhysicsExtractor

P(t): chuỗi tư thế 3D của cơ thể người.

Sprint 2 yêu cầu:

PhysicsExtractor(joints, fps) -> dict

- joints: chuỗi khớp 3D có kích thước (T, J, 3), trong đó T là số khung hình và J là số khớp.
- Tọa độ có đơn vị mét, trục z hướng lên.
- fps: tần số lấy mẫu của chuỗi tư thế, tính bằng số khung hình mỗi giây.

## 2. Đầu ra của PhysicsExtractor — theo Mục 7.2

phi(t) = [h, v_z, a_peak, theta, T_ground]

Các đại lượng này được tính từ pose 3D.

### h(t): Độ cao trọng tâm

c(t): trung bình có trọng số khối lượng của vị trí trọng tâm các đoạn cơ thể.

h(t) = c_z(t)

### v_z(t): Vận tốc theo phương thẳng đứng

v_z(t) = dh(t)/dt

### a_peak: Độ lớn gia tốc thẳng đứng lớn nhất trong cửa sổ

a_peak = max |d²h(t)/dt²| trong cửa sổ đang xét.

Sử dụng đạo hàm số có làm trơn Savitzky–Golay theo Mục 7.2.

### θ(t): Góc thân người

Góc giữa vector hông → cổ và trục thẳng đứng.

### T_ground(t): Thời gian liên tục trọng tâm ở dưới ngưỡng

Khoảng thời gian liên tục mà:

h(t) < h_thr

## 3. Các tham số chưa xác định

- Trọng số khối lượng và vị trí trọng tâm của các đoạn cơ thể.
- Cách ánh xạ các khớp cho từng định dạng bộ xương.
- Cách chuyển tọa độ của từng nguồn dữ liệu về quy ước: đơn vị mét, trục z hướng lên.
- Độ dài cửa sổ và bậc đa thức Savitzky–Golay.
- Ngưỡng độ cao h_thr.
- Định nghĩa cụ thể của cửa sổ tính gia tốc đỉnh.

Các tham số này cần có căn cứ và được kiểm tra trước khi sử dụng PhysicsExtractor cho các thí nghiệm nghiên cứu.

## 4. Trạng thái triển khai

- [x] Đã có hàm hỗ trợ sơ bộ tính các đại lượng chuyển động theo phương thẳng đứng.
- [x] Đã có test rơi tự do tổng hợp cho hàm hỗ trợ.
- [ ] PhysicsExtractor nhận đầu vào là chuỗi khớp 3D.
- [ ] Đã kiểm chứng đủ năm đại lượng vật lý đầu ra.
- [ ] Các giá trị cấu hình có nguồn hoặc căn cứ lựa chọn.
- [ ] Đã có các test cho PhysicsExtractor đầy đủ.
- [ ] Đã rà soát và push bản triển khai lên GitHub.

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
- Teacher nhìn thấy P(t) nên hiểu rõ chuyển động cơ thể, student nhận kiến thức đó từ teacher và học. Đây là ý tưởng knowledge distillation.

Đặc trưng vật lý (h, v_z, a_peak, θ, T_ground) được tính từ pose 3D để hỗ trợ huấn luyện. Student học từ teacher và học dự đoán các đại lượng vật lý từ ảnh nhiệt và radar. Hiệu quả của cách học này cần được kiểm chứng bằng thực nghiệm.

Các ràng buộc: không dùng pose/RGB khi suy luận; chạy trong giới hạn tài nguyên thiết bị biên; mục tiêu độ trễ báo động không quá 1,5 giây sau thời điểm va chạm.
