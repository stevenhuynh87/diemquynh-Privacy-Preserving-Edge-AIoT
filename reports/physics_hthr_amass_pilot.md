# Sprint 2 — thử ngưỡng độ cao COM trên HDM05

Ngày ghi: 28/11/2026. Trạng thái: **pilot thăm dò; chưa hiệu chuẩn hoặc xác thực ngưỡng**.

Theo Mục 7.2 của `DiemQuynh_Planning_12_Month_Research_Roadmap.md`,
`T_ground(t)` là thời gian liên tục mà `h(t) = c_z(t) < h_thr`.
Ngưỡng thử ở đây là **0,275 m**, chỉ áp dụng sau khi trừ mốc sàn proxy
của từng người. Đây là lựa chọn thăm dò do trợ lý đề xuất từ dữ liệu, không phải hằng số
được Planning hay nhà sản xuất cảm biến quy định.

## Cách chọn ngưỡng

Từ các frame HDM05 04-01 đã sàng lọc bằng hình chiếu khớp: COM trừ mốc
sàn của các tư thế nằm *dự kiến* ở `bk`, `mm`, `dg` nằm trong khoảng
0,0563–0,2647 m. Các frame ngồi được chọn nằm trong khoảng
0,2860–0,3558 m. Chọn 0,275 m gần trung điểm giữa giá trị nằm lớn nhất
(0,2647 m) và giá trị ngồi nhỏ nhất (0,2860 m). Không dùng kết quả thử
trên chuỗi để điều chỉnh ngưỡng này.

Nguồn dữ liệu: HDM05, các file `HDM_bk_04-01_01_120_poses.npz`,
`HDM_mm_04-01_01_120_poses.npz`, `HDM_dg_04-01_01_120_poses.npz`.
Tái dựng pose qua mô hình SMPL+H rồi ánh xạ xấp xỉ 52 khớp sang cấu
trúc 25 khớp NTU để gọi `PhysicsExtractor`. COM dùng mô hình đoạn cơ
thể Winter trong `physics/extractor.py`. Mốc sàn của mỗi diễn viên là
tọa độ z thấp nhất của mesh tại một frame đứng; **chưa phải mặt sàn
được đo độc lập**. Phép ánh xạ khớp và mốc sàn proxy do trợ lý đề xuất;
Planning không quy định hai phép xấp xỉ này. Các nhãn ngồi/nằm chỉ là kết quả sàng lọc bằng pose,
chưa có nhãn chuyên gia độc lập. Dữ liệu AMASS là chuyển động mocap;
đây không phải skeleton NTU ghi trực tiếp.

## Thử trên các đoạn liên tục, 120 frame/s

Mỗi cửa sổ gồm 241 frame liên tiếp, dài 240 khoảng thời gian = 2,000 s.
Kết quả sau do người chạy cung cấp từ script gọi `PhysicsExtractor` với
`h_thr=0.275`:

| Diễn viên và đoạn | Frame | COM thấp nhất (m) | COM trung vị (m) | Frame dưới ngưỡng | `T_ground` cuối đoạn (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| mm, ngồi | 8361–8601 | 0,301 | 0,306 | 0/241 | 0 |
| mm, nằm dự kiến | 9903–10143 | 0,050 | 0,057 | 241/241 | 2,000 |
| dg, ngồi | 5514–5754 | 0,280 | 0,287 | 0/241 | 0 |
| dg, nằm dự kiến | 6787–7027 | 0,082 | 0,089 | 241/241 | 2,000 |

`241/120 = 2,0083 s` nếu đếm thời lượng mỗi frame; giá trị cuối của
`T_ground` là `(241-1)/120 = 2,000 s` nếu đếm thời gian giữa hai frame.
Đây là khác biệt về quy ước một frame. Đoạn ngồi `dg` thấp nhất 0,280 m,
chỉ hơn ngưỡng 0,005 m, nên biên phân tách rất hẹp.

## Kiểm tra chuyển tư thế với ngưỡng giữ cố định

Sau khi chọn 0,275 m, kiểm tra thêm hai cửa sổ liên tục của cùng diễn
viên `mm` ở 120 frame/s. Không điều chỉnh ngưỡng theo kết quả:

| Chuyển tư thế | Frame | COM đầu → cuối (m) | COM thấp nhất (m) | Frame dưới ngưỡng | Frame vượt xuống đầu tiên | `T_ground` cuối (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Đứng → ngồi chủ động | 7967–8481 | 0,974 → 0,306 | 0,301 | 0/515 | Không có | 0 |
| Đứng → nằm dự kiến | 9252–10023 | 0,976 → 0,057 | 0,057 | 374/772 | 9650 (`h=0,274 m`) | 3,108 |

Ở cửa sổ thứ hai, frame 9650 đến 10023 có 374 frame dưới ngưỡng.
`T_ground` cuối = `(374-1)/120 = 3,1083 s`, phù hợp quy ước thời
gian giữa các frame đã quan sát ở trên. Kiểm tra này cho thấy hàm
phân biệt được **hai chuyển tư thế được chọn** và mốc vượt ngưỡng có
thể truy lại theo frame. Nó không xác nhận khả năng phát hiện ngã.

## Kết luận có giới hạn và việc tiếp theo

Ngưỡng thử tách được **2/2 đoạn nằm dự kiến và 2/2 đoạn ngồi được chọn**.
Đây là kiểm tra trên chính nguồn và kiểu tư thế dùng để chọn ngưỡng,
không phải đánh giá độc lập hay độ chính xác phát hiện ngã. Cửa sổ nằm
241 frame bắt đầu khi COM đã thấp; cửa sổ chuyển tư thế `mm` bổ sung
kiểm tra thời điểm vượt ngưỡng tại frame 9650.
HDM05 04-01 gồm các chuyển tư thế ngồi/nằm chủ động, **không được gán là
clip ngã**. `T_ground` là đặc trưng vật lý, không phải nhãn ngã.

Trước khi sử dụng như ngưỡng cho pose NTU thật hoặc tuyên bố đạt độ
chính xác phát hiện ngã, cần kiểm tra mốc sàn, độ nhạy với
ánh xạ SMPL+H→NTU, tracking và các clip có nhãn được xác minh. Không
áp dụng 0,275 m trực tiếp lên tọa độ Camera Y của NTU.
