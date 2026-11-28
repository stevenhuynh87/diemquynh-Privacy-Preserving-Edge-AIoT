# Sprint 2 — báo cáo tiến độ (bản nháp, 28/11/2026)

Theo yêu cầu cập nhật của thầy ngày 22/11/2026, sprint chưa huấn luyện KD.
Mã extractor và các kết quả E0 trước đây đã được người thực hiện push lên
`main`. Báo cáo thử ngưỡng HDM05 mới chưa xác nhận đã đưa vào repo.

## 1. PhysicsExtractor — đã có mã và ngưỡng thử; chờ thầy xem

`physics/extractor.py::PhysicsExtractor(joints, fps)` đã có COM theo 14 đoạn
Winter ánh xạ xấp xỉ sang NTU, vận tốc/gia tốc Savitzky–Golay, góc thân và
thời gian dưới ngưỡng. Test tổng hợp rơi tự do và các kiểm tra biên trước
đây đã đạt; cần đối chiếu trực tiếp file test khi gửi thầy để ghi chính
xác sai số cho phép, cửa sổ SG và bậc đa thức. `docs/physics_formulation.md`
ghi hệ số, giả định và giới hạn. Đã chọn **ngưỡng thử 0,275 m** từ COM
ở các tư thế nằm dự kiến của ba clip HDM05 04-01. Sau khi cố định ngưỡng,
kiểm tra hai chuỗi nằm/ngồi 241 frame và hai chuỗi chuyển tư thế: đứng→ngồi
0/515 frame dưới ngưỡng; đứng→nằm chủ động vượt tại frame 9650 và duy trì
đến cuối (374/772 frame, `T_ground` cuối 3,108 s). Chi tiết cách chọn và
giới hạn nằm trong `reports/physics_hthr_amass_pilot.md` (chưa xác nhận
đã có trên GitHub).

HDM05 04-01 không phải clip ngã có nhãn. Ánh xạ SMPL+H→25 khớp NTU và
mốc sàn từ một frame đứng là phép xấp xỉ do trợ lý đề xuất; chưa xác thực
ngưỡng này trên skeleton NTU đã hiệu chuẩn sàn. `h_thr` trong hàm cần
truyền tường minh; không áp dụng 0,275 m cho Camera Y gốc. Báo ngưỡng
pilot để thầy xem sớm, không tuyên bố độ chính xác phát hiện ngã.

## 2. Pilot E0 — đã chạy L2, còn giới hạn

Năm clip NTU RGB+D 120, một cảnh: 2 ngã A043 và 3 ADL A006/A008/A009.
`sim/thermal_render.py` tạo ảnh 24×32 từ đường khớp; `sim/radar_sim.py`
lấy điểm trên đường khớp và tính Doppler hướng tâm. Đây là proxy hình học,
chưa lấy điểm bề mặt và chưa mô phỏng sóng RF. Đã kiểm tra kích thước và
giá trị hữu hạn của cả năm NPZ: 379 frame, tổng 1.143.899 byte.
`eval/latency.py::benchmark` đo một lượt lạnh trên CPU, gồm thermal + L2
+ ghi NPZ, trung bình có trọng số 0,937 ms/frame. Không tính đọc đầu vào.
Không có CUDA trên máy này nên VRAM không áp dụng. Theo Plan B của thầy,
L2 là mức chính cho pilot máy hiện tại; RF-Genesis L1 chưa được benchmark.
Chi tiết năm clip và ảnh xem nhanh nằm trong `pilot_benchmark.md`.

`docs/e0_scenario_catalog.md` là danh mục **đề xuất** 8 kiểu ngã, 10 ADL,
5 confounder. E0 mới có 5 clip thật và chưa cài confounder (để Sprint 3).
Danh mục chưa chứng minh mọi kịch bản đều có dữ liệu hay đã chạy mô phỏng.

## 3. Thông số cảm biến — bản nháp có nguồn

`sensor_params.yaml` ghi các lựa chọn FOV, NETD và refresh của MLX90640,
băng tần IWR6843, và tốc độ Taramasco báo cáo. Chirp cụ thể của Taramasco
và MM-Fi ghi `TBD` vì chưa xác nhận từ nguồn. Không gán thông số phần cứng
cho lần chạy E0 proxy; FPS 30 của NTU chỉ giả định từ metadata RGB.

## Việc kế tiếp để xin thầy nghiệm thu

1. Đưa báo cáo ngưỡng pilot vào repo, đối chiếu trực tiếp test rơi tự do
   (tham số SG và sai số), gửi thầy `PhysicsExtractor` và test để xem sớm.
   Không cần tiếp tục thử HDM05 để điều chỉnh ngưỡng pilot.
2. Kiểm tra độ nhạy trên nhiều cảnh/người, thời gian lặp lại, và giới hạn
   mô hình L2; chỉ thử L1 khi có máy CUDA phù hợp. Không suy ra độ trễ
   báo động 1,5 s từ thời gian render mỗi frame.
3. Đối chiếu chirp với cấu hình gốc nếu nhận được; giữ `TBD` khi chưa có.
4. Kiểm kê lit matrix ≥40 bài và các bài thầy chỉ định; chuẩn bị demo
   30 phút sau khi phần 1–3 đủ bằng chứng. Sprint 1 còn các việc trong
   issue S01 trước khi qua gate Research & Novelty.
