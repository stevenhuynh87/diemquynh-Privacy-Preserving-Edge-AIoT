# PhysicsExtractor — Công thức, triển khai và kết quả kiểm thử

Ngày cập nhật: 25/11/2026.
Phạm vi: Sprint 2 — PhysicsExtractor.
Trạng thái: BẢN THỬ NGHIỆM — CHƯA XÁC THỰC TRÊN DỮ LIỆU THỰC.

## 1. Nguồn và phạm vi yêu cầu

Nguồn yêu cầu:
- DiemQuynh_Planning_12_Month_Research_Roadmap.md:
  Mục 3.1, Mục 7.2 và Sprint 2.
- Yêu cầu bổ sung của thầy: hoàn thiện Phần 1 về
  PhysicsExtractor, chọn h_thr từ vài clip mẫu khi nằm,
  ghi cấu hình làm trơn và kết quả test để gửi thầy xem.

Phân biệt:
- “Phần 1” của yêu cầu bổ sung không đồng nghĩa “Sprint 1”.
- Triển khai PhysicsExtractor thuộc Sprint 2 trong Planning.
- Kiểm tra tracking ba clip NTU là bước hỗ trợ triển khai
  được đề xuất, không phải một đầu việc riêng do thầy quy định.

Nguồn mô hình trọng tâm:
- TaFall, Mục 2.2, trang 4–5: công thức COM theo đoạn cơ thể,
  dẫn Winter tại tài liệu tham khảo [59].
- Winter (2009), Biomechanics and Motor Control of Human
  Movement, Table 4.1 “Anthropometric Data”:
  trang sách 86, trang PDF 99 của bản đã cung cấp.

Các lựa chọn triển khai và cấu hình test bên dưới được ghi
riêng; không xem chúng là tham số do thầy quy định.

## 2. Đầu vào của PhysicsExtractor

P(t): chuỗi tư thế 3D của cơ thể người.

Giao diện được yêu cầu trong Sprint 2:

PhysicsExtractor(joints, fps) -> dict

- joints: chuỗi khớp 3D, kích thước (T, J, 3).
- T: số frame.
- J: số khớp.
- Tọa độ có đơn vị mét, trục z hướng lên.
- fps: số frame mỗi giây.

Giao diện bản triển khai hiện tại:

PhysicsExtractor(
    joints,
    fps,
    *,
    window_length,
    polyorder,
    h_thr,
) -> dict

Giới hạn và điều kiện của bản hiện tại:
- Chỉ hỗ trợ định dạng NTU 25 khớp: (T, 25, 3).
- Các frame phải cách đều nhau theo thời gian.
- Người gọi cung cấp window_length, polyorder và h_thr.
- Theo quy ước hiện tại của hàm, đầu vào có sàn tại z = 0.
- Hàm không tự hiệu chỉnh mặt sàn hoặc chuyển hệ tọa độ.
- Hàm chưa nhận hoặc xử lý tracking state.
- Cần tọa độ hữu hạn và vector hông → cổ khác 0.

Điều kiện sàn tại z = 0 là quy ước triển khai hiện tại để
diễn giải độ cao và ngưỡng. Không suy rằng chỉ đổi thứ tự
trục camera là đã hiệu chuẩn sàn.

## 3. Đầu ra theo Planning Mục 7.2

phi(t) = [h, v_z, a_peak, theta, T_ground]

### 3.1. Trọng tâm và độ cao h(t)

c(t): trung bình có trọng số khối lượng của vị trí trọng tâm
các đoạn cơ thể.

Với m_s là tỉ phần khối lượng của đoạn s:

c(t) = sum_s m_s * c_s(t)

sum_s m_s = 1

h(t) = c_z(t)

Bản hiện tại dùng mô hình 14 đoạn xấp xỉ cho skeleton NTU.
Hệ số số học đã đối chiếu Winter; ánh xạ mốc giải phẫu sang
khớp NTU chưa được xác thực trên dữ liệu thực.

### 3.2. Vận tốc thẳng đứng v_z(t)

v_z(t) = dh(t)/dt

Đơn vị: m/s.

Bản hiện tại tính đạo hàm bậc nhất trực tiếp từ chuỗi độ cao
bằng Savitzky–Golay.

### 3.3. Gia tốc đỉnh a_peak

a_z(t) = d²h(t)/dt²

a_peak = max |a_z(t)| trong cửa sổ đang xét.

Đơn vị: m/s².

Planning Mục 7.2 yêu cầu đạo hàm số có làm trơn Savitzky–Golay.

Quy ước triển khai hiện tại:
- Tính đạo hàm bậc hai trực tiếp từ chuỗi độ cao.
- Toàn bộ chuỗi đầu vào được xem là một cửa sổ.
- a_peak trả về một số vô hướng cho cửa sổ đó.
- Chưa triển khai chuỗi a_peak trên các cửa sổ trượt.
- Dùng mode="interp".
- Chưa chốt cấu hình cửa sổ/bậc đa thức cho clip thật.

### 3.4. Góc thân theta(t)

Góc giữa vector hông → cổ và trục thẳng đứng.

Ánh xạ NTU được đề xuất trong bản hiện tại:
- Hông: trung điểm HipLeft (13) và HipRight (17).
- Cổ: Neck (3).
- Vector thân: trung điểm hông → cổ.
- Trục thẳng đứng đầu vào: +z.
- Đơn vị đầu ra: radian.

Các hướng tổng hợp đã kiểm tra:
- Hướng lên: 0.
- Nằm ngang: pi/2.
- Hướng xuống: pi.

Vector thân bằng 0 không xác định được góc và bị từ chối.

### 3.5. Thời gian dưới ngưỡng T_ground(t)

Khoảng thời gian liên tục mà:

h(t) < h_thr

Đơn vị: giây.

h(t) và h_thr phải cùng đơn vị và cùng mốc độ cao.

Quy ước rời rạc được đề xuất trong bản hiện tại:
- Frame đầu tiên dưới ngưỡng: 0 giây.
- Mỗi frame tiếp tục dưới ngưỡng: cộng 1/fps.
- Khi h(t) bằng hoặc lớn hơn h_thr: đặt lại 0.
- Nếu clip bắt đầu dưới ngưỡng, chỉ đếm từ đầu clip.
- Không nội suy thời điểm vượt ngưỡng giữa hai frame.

Tên T_ground không có nghĩa hàm trực tiếp nhận biết tiếp xúc
với sàn. Hàm hiện tính thời gian dưới ngưỡng COM theo định nghĩa.

## 4. Đối chiếu trực tiếp nguồn Winter

Nguồn: Table 4.1, trang sách 86, trang PDF 99.

Các hệ số dùng trong code đã đối chiếu:

| Đoạn | Tỉ phần khối lượng | Hệ số vị trí COM từ đầu gần thân |
|---|---:|---:|
| Cánh tay trên, mỗi bên | 0.028 | 0.436 |
| Cẳng tay, mỗi bên | 0.016 | 0.430 |
| Bàn tay, mỗi bên | 0.006 | 0.506 |
| Đùi, mỗi bên | 0.100 | 0.433 |
| Cẳng chân, mỗi bên | 0.0465 | 0.433 |
| Bàn chân, mỗi bên | 0.0145 | 0.500 |
| Thân | 0.497 | 0.500 |
| Đầu–cổ | 0.081 | 1.000 theo mốc giải phẫu trong bảng |

Đối với các đoạn chi, code tính:

c_s = start + r * (end - start)

Trong đó r lấy theo cột Proximal của Table 4.1.

Mô hình gồm:
- 12 đoạn chi: 6 đoạn mỗi bên.
- 1 đoạn thân.
- 1 đoạn đầu–cổ.

Tổng tỉ phần khối lượng bằng 1.

### 4.1. Ánh xạ NTU đang sử dụng

ID khớp bắt đầu từ 1.

| Đoạn | Ánh xạ NTU |
|---|---|
| Cánh tay trên trái/phải | 5 → 6 / 9 → 10 |
| Cẳng tay trái/phải | 6 → 7 / 10 → 11 |
| Bàn tay trái/phải | 7 → 8 / 11 → 12 |
| Đùi trái/phải | 13 → 14 / 17 → 18 |
| Cẳng chân trái/phải | 14 → 15 / 18 → 19 |
| Bàn chân trái/phải | 15 → 16 / 19 → 20 |
| Thân | Trung điểm hai hông → trung điểm hai vai |
| Đầu–cổ | Dùng trực tiếp vị trí Head (4) |

### 4.2. Giới hạn của ánh xạ

Hệ số số học khớp bảng không chứng minh các khớp NTU trùng
với mốc giải phẫu Winter.

Các khác biệt cần ghi rõ:
- Đầu–cổ: bảng dùng mốc C7–T1 và xương sườn thứ nhất → ống tai.
  Code dùng Head làm vị trí COM đại diện.
- Bàn tay: bảng dùng trục cổ tay → khớp ngón giữa được chỉ định
  trong bảng; code dùng Wrist → Hand.
- Bàn chân: bảng dùng mắt cá ngoài → đầu xương bàn chân II;
  code dùng Ankle → Foot.
- Thân: bảng dùng mấu chuyển lớn → khớp vai;
  code dùng trung điểm hai hông → trung điểm hai vai.

Kết luận:
- Đã xác minh các hệ số số học nêu trên từ bảng gốc.
- Ánh xạ NTU là xấp xỉ triển khai được đề xuất.
- Chưa xác thực độ chính xác COM trên dữ liệu thực.
- Không gọi đây là bản tái hiện chính xác mô hình TaFall.

## 5. Kiểm tra tracking trên ba clip NTU

Nguồn:
nturgbd_skeletons_s001_to_s017.zip

Các clip:
- S001C001P001R001A043.
- S001C001P002R001A043.
- S001C001P003R001A043.

Nhóm khớp dùng tính COM: Head (4) và các khớp 5–20.
Nhóm khớp tính góc thân: Neck (3), HipLeft (13), HipRight (17).

| Clip | Tổng frame | COM toàn bộ tracked | Có inferred, không untracked | Có untracked | COM đầu vào không hữu hạn | Thân toàn bộ tracked |
|---|---:|---:|---:|---:|---:|---:|
| P001 | 85 | 17 | 68 | 0 | 0 | 85 |
| P002 | 84 | 21 | 63 | 0 | 0 | 84 |
| P003 | 71 | 37 | 34 | 0 | 0 | 71 |

Khớp có số frame inferred cao nhất từng clip:
- P001: AnkleLeft, 53/85 frame.
- P002: KneeRight, 46/84 frame.
- P003: FootRight, 30/71 frame.

HipLeft và HipRight luôn tracked trong cả ba clip.

Diễn giải:
- P003 có tỷ lệ toàn bộ khớp COM tracked cao nhất trong ba clip:
  52,11%; chưa chứng minh COM chính xác hơn.
- Tọa độ hữu hạn không chứng minh khớp hoặc COM chính xác.
- Các khớp tính góc thân đều tracked; điều này không xác nhận
  camera Y trùng phương thẳng đứng thực tế.
- Dữ liệu vẫn ở hệ tọa độ camera, chưa hiệu chuẩn sàn.
- Chưa xóa frame, nội suy hoặc thay trọng số khối lượng.

Tệp minh chứng:
- reports/ntu_com_tracking/review.md.
- reports/ntu_com_tracking/summary.csv.
- reports/ntu_com_tracking/*_frames.csv.
- reports/ntu_com_tracking/*_joints.csv.

## 6. Kiểm thử trên dữ liệu tổng hợp

File test: tests/test_physics_extractor.py.

Kết quả chạy:
- 9 passed in 1.99s.
- Python 3.11.7.
- pytest 9.1.1.

Log:
reports/physics_extractor_tests.txt

### 6.1. Phạm vi chín test

1. Vận tốc, gia tốc và gia tốc đỉnh của rơi tự do lý tưởng.
2. Từ chối FPS bằng 0.
3. Đóng góp của khuỷu trái vào COM và số đoạn bằng 14.
4. Dịch toàn bộ khớp thì COM dịch cùng vector.
5. Góc thân ở ba hướng: lên, ngang, xuống.
6. Từ chối vector thân bằng 0.
7. Thời gian dưới ngưỡng và đặt lại khi bằng ngưỡng.
8. Clip bắt đầu dưới ngưỡng.
9. Test tích hợp đủ h, v_z, a_peak, theta và T_ground.

### 6.2. Cấu hình test rơi tự do

Đây là cấu hình tổng hợp được đề xuất để kiểm tra phép tính,
không phải cấu hình đã chọn cho dữ liệu thật.

- fps = 10.
- Số mẫu = 5.
- g = 9.81 m/s².
- Savitzky–Golay: window_length = 5, polyorder = 2.
- Quỹ đạo dịch chuyển: 2.0 - 0.5 * g * t².
- Vận tốc kỳ vọng: -g * t.
- Gia tốc kỳ vọng: -g.
- Gia tốc đỉnh kỳ vọng: g.
- rtol = 0.
- atol = 1e-8 cho test rơi tự do và test tích hợp.
- atol = 1e-12 cho các test COM, góc và thời gian nêu trong code.
- h_thr = 2.12 m chỉ dùng trong test tích hợp.
- h_thr = 0.5 m chỉ dùng trong các test riêng về thời gian.

Sai số đo được trong test helper:
- Vận tốc tối đa: 4.885e-15 m/s.
- Gia tốc tối đa: 7.638e-14 m/s².

### 6.3. Giới hạn kết luận

Các test đã đạt xác nhận những trường hợp tổng hợp đã kiểm tra.

Chưa chứng minh:
- Tất cả đầu vào không hợp lệ đều được xử lý.
- Mô hình COM phù hợp giải phẫu từng người.
- Độ chính xác trên dữ liệu có nhiễu hoặc khớp inferred.
- Cấu hình làm trơn phù hợp với clip thật.
- Ngưỡng h_thr phù hợp dữ liệu thực.

## 7. Trạng thái triển khai và việc còn thiếu

### 7.1. Đã có bằng chứng

- [x] Có helper động học dùng Savitzky–Golay.
- [x] Có mô hình COM 14 đoạn xấp xỉ cho NTU.
- [x] Đã đối chiếu các hệ số số học với Winter Table 4.1.
- [x] Có hàm tính góc thân.
- [x] Có hàm tính thời gian liên tục dưới ngưỡng.
- [x] Có PhysicsExtractor nhận chuỗi khớp 3D NTU.
- [x] Đã kiểm tra tracking đầu vào trên ba clip.
- [x] Đã rà và chạy chín test.
- [x] Test tích hợp kiểm tra đủ năm đầu ra trên dữ liệu tổng hợp.

### 7.2. Chưa hoàn thành

- [ ] Xác thực ánh xạ giải phẫu Winter → khớp NTU.
- [ ] Chốt cách xử lý tracking state trong pipeline tính đặc trưng.
- [ ] Xác minh FPS và tính đều của thời gian trên clip thật.
- [ ] Xác định phương thẳng đứng và mốc sàn.
- [ ] Chọn cửa sổ/bậc Savitzky–Golay phù hợp dữ liệu thật.
- [ ] Chốt cửa sổ a_peak dùng cho thí nghiệm.
- [ ] Chọn h_thr từ vài clip mẫu khi nằm và ghi cách chọn.
- [ ] Đối chiếu kết quả trên dữ liệu thực.
- [ ] Xác nhận commit/push phiên bản code và test hiện tại.
- [ ] Gửi code và kết quả cho thầy xem.
- [ ] Nhận phản hồi/thẩm định của thầy.

Không đánh dấu hoàn thành Phần 1 chỉ từ kết quả 9 test passed.

## 8. My understanding of Section 3.1

Phần này là diễn giải của sinh viên, chưa được thầy thẩm định.

### 8.1. Kí hiệu

- Student: mô hình nhỏ chạy trên thiết bị biên, dùng để phát hiện ngã.
- Teacher: mô hình hướng dẫn student trong huấn luyện,
  sử dụng thông tin đặc quyền như pose 3D.
- Xth: chuỗi ảnh nhiệt, kích thước 24 × 32.
- Xrd: chuỗi dữ liệu radar, có thể là point cloud hoặc micro-Doppler.
- [t-W, t]: cửa sổ W giây gần nhất tại thời điểm t.

Các dải tần số mô tả trong bản diễn giải:
- Thermal: 2–8 Hz.
- Radar: 8–20 Hz.

Các dải này không thay thế tần số thực tế đo trên từng bản ghi
và không được dùng làm FPS mặc định cho skeleton NTU.

### 8.2. Input trong cửa sổ [t-W, t]

- Chuỗi ảnh nhiệt và timestamp riêng.
- Chuỗi radar và timestamp riêng.

Với point cloud, một điểm có thể được mô tả bởi:
x, y, z, vận tốc Doppler v_D và SNR.

Mô tả trên không áp dụng nguyên dạng cho micro-Doppler;
cần kiểm tra schema thực tế của nguồn dữ liệu.

Kết quả audit Taramasco đã ghi nhận trước đó:
- Thermal khoảng 2,6 Hz.
- Radar khoảng 8,3 Hz.

Hai luồng lấy mẫu khác tốc độ nên cần dùng timestamp
để xử lý quan hệ thời gian giữa chúng.

### 8.3. Output

- p(fall | Xth, Xrd): xác suất ngã từ dữ liệu nhiệt và radar.
- Thời điểm báo động dự đoán.
- phi_hat(t): các đại lượng vật lý do student dự đoán,
  gồm h, v_z, a_peak, theta và T_ground.

### 8.4. Vai trò của teacher và đặc trưng vật lý

Thông tin đặc quyền là thông tin chỉ dùng trong huấn luyện,
chẳng hạn pose 3D P(t) từ nguồn dữ liệu thật hoặc mô phỏng.

Teacher học từ pose; student học thông qua quá trình
knowledge distillation.

Trong phần đang thử nghiệm, pose NTU là skeleton 3D được
cung cấp sẵn. Không mô tả bước đọc skeleton này là đã chạy
một mô hình trích pose từ video RGB.

Các đặc trưng vật lý được tính từ pose để hỗ trợ huấn luyện.
Student học dự đoán chúng từ ảnh nhiệt và radar.
Hiệu quả cần được kiểm chứng bằng thực nghiệm.

### 8.5. Ràng buộc và mục tiêu

- Không dùng pose/RGB khi student suy luận.
- Chạy trong giới hạn tài nguyên thiết bị biên.
- Mục tiêu độ trễ báo động không quá 1,5 giây sau va chạm.
- Đây là mục tiêu thiết kế, chưa phải kết quả đo đạt được.

## Kiểm tra thực tế P008 - NTU RGB+D 120

Mẫu: S001C001P008R001A043, 63 frame. Video RGB cho thấy người
chuyển từ đứng sang tư thế rất thấp, chống tay; không xác nhận
thân nằm hẳn trên sàn.

Tệp skeleton có hai body ID trong cả 63 frame. Chọn
72057594037945234 để khảo sát người di chuyển: SpineBase dịch
0,543 m từ đầu đến cuối. Body 72057594037945240 gần như đứng
yên (dịch 0,004 m). Đây là lựa chọn dựa trên chuyển động và
đối chiếu RGB, không xác nhận độ chính xác từng khớp.

Trong 63 frame: 23 frame có toàn bộ 17 khớp COM tracked;
40 frame có ít nhất một khớp COM inferred; không có frame
chứa khớp COM untracked. COM tính được hữu hạn ở 63 frame.
COM Camera Y ở frame 1 là 0,207 m, frame 55 là -0,494 m:
giảm 0,701 m trong hệ tọa độ camera. Frame 55 có khớp COM
inferred; chưa xác nhận đó là thời điểm va chạm.

Trong 20 frame đầu, FootRight (khớp 20) tracked 20/20,
Camera Y trung vị -0,585 m, khoảng [-0,591; -0,584] m.
FootLeft (khớp 16) cũng tracked 20/20 nhưng ở frame 45,
55 và 63 là inferred; Camera Y frame 55 là -0,756 m,
thấp hơn rõ rệt so với khoảng đứng ban đầu
[-0,586; -0,547] m. Không dùng cực tiểu FootLeft làm sàn.

Chênh lệch COM Camera Y trừ FootRight Camera Y:
- Frame 1: xấp xỉ 0,792 m.
- Frame 55: 0,102 m (FootRight tracked, COM có khớp inferred).
- Frame 63: 0,224 m (FootRight tracked, COM có khớp inferred).

Các chênh lệch trên chỉ để kiểm tra xu hướng, không phải
độ cao COM đã hiệu chuẩn. Chưa xác minh mặt phẳng sàn,
hướng trục thẳng đứng và khoảng thời gian lấy mẫu skeleton.
Chưa đưa joints_camera_m trực tiếp vào PhysicsExtractor,
vì hàm hiện yêu cầu z hướng lên và sàn ở z = 0.

Đối chiếu yêu cầu Sprint 2: đã có ví dụ kiểm tra COM trên
pose thực và ghi nhận chất lượng tracking. Yêu cầu định nghĩa
h_thr có căn cứ vẫn CHƯA HOÀN THÀNH. Bước cần làm tiếp là
kiểm tra mốc sàn và so sánh với hoạt động không ngã nhưng
cũng có COM thấp trước khi đề xuất hoặc đánh giá ngưỡng.
Việc chọn P008 và cách kiểm tra FootRight là đề xuất triển khai,
không phải chỉ định cụ thể của thầy.

## Doi chung P008 A043-A008-A006

Nguon du lieu: ba mau S001C001P008R001A043 (nga),
S001C001P008R001A008 (ngoi xuong) va
S001C001P008R001A006 (nhat do). Day la so sanh de khao sat
tren cung subject, setup va camera; chua phai danh gia mo hinh.

Dai luong khao sat = COM Camera Y tru trung vi Camera Y cua
FootRight tracked trong 20 frame dau, tinh rieng cho moi clip.
Moc lan luot la -0.585 m (A043), -0.623 m (A008),
-0.499 m (A006). Moc nay chua duoc hieu chuan thanh mat san.

Gia tri thap nhat: A043 0.073 m tai frame 52;
A008 0.387 m tai frame 49; A006 0.077 m tai frame 34.
A006 ha thap gan bang A043 roi tro lai 0.760 m o frame cuoi;
do do chi so sanh do thap cuc tieu khong phan biet duoc
hai clip nay.

Do dai khoang lien tuc duoi cac muc thu, tinh bang frame:
| Muc thu | A043 nga | A008 ngoi xuong | A006 nhat do |
|---|---:|---:|---:|
| 0.15 m | 15 | 0 | 1 |
| 0.25 m | 21 | 0 | 3 |
| 0.35 m | 24 | 0 | 6 |

Moi khoang thap dai nhat o tren deu co 0 frame ma toan bo
17 khop COM la tracked. Gia tri COM tai cac frame nay chua
duoc xac thuc. Cac muc thu 0.15/0.25/0.35 m khong phai
h_thr. Chua doi frame sang giay vi chua xac minh khoang lay
mau skeleton. Chua hieu chuan huong truc va mat phang san.

Lien he yeu cau Sprint 2: ket qua goi y can xem xet
T_ground ben canh h, dung voi nhom dac trung vat ly trong
muc 7.2 cua roadmap. Chua hoan thanh viec dinh nghia
h_thr co can cu va chua kiem dinh tren nhieu subject.
