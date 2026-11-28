# Sprint 2 — báo cáo tiến độ (bản nháp, 28/11/2026)

Theo yêu cầu cập nhật của thầy ngày 22/11/2026, sprint chưa huấn luyện KD.
Mã và báo cáo hiện đã push lên main; phần 1 chưa hoàn tất tiêu chí h_thr.

## 1. PhysicsExtractor — chưa hoàn tất

physics/extractor.py::PhysicsExtractor(joints, fps) đã có COM theo 14 đoạn
Winter ánh xạ xấp xỉ sang NTU, vận tốc/gia tốc Savitzky–Golay, góc thân và
thời gian dưới ngưỡng. Test tổng hợp rơi tự do và các kiểm tra biên đã đạt.
docs/physics_formulation.md ghi hệ số, giả định và giới hạn. Chưa chọn được
h_thr từ COM khi nằm ở vài clip RGB xác nhận. Mức 0,25 m trong
reports/ntu_com_tracking/threshold_pilot.md chỉ là kiểm tra độ nhạy của
Camera Y trừ mốc chân, chưa phải chiều cao COM hiệu chuẩn sàn. Nhiều khớp
cuối clip bị inferred. Chưa đánh dấu phần 1 hoàn thành hoặc coi COM đã
được xác thực trên dữ liệu thực.

## 2. Pilot E0 — đã chạy L2, còn giới hạn

Năm clip NTU RGB+D 120, một cảnh: 2 ngã A043 và 3 ADL A006/A008/A009.
sim/thermal_render.py tạo ảnh 24×32 từ đường khớp; sim/radar_sim.py
lấy điểm trên đường khớp và tính Doppler hướng tâm. Đây là proxy hình học,
chưa lấy điểm bề mặt và chưa mô phỏng sóng RF. Đã kiểm tra kích thước và
giá trị hữu hạn của cả năm NPZ: 379 frame, tổng 1.143.899 byte.
eval/latency.py::benchmark đo một lượt lạnh trên CPU, gồm thermal + L2
+ ghi NPZ, trung bình có trọng số 0,937 ms/frame. Không tính đọc đầu vào.
Không có CUDA trên máy này nên VRAM không áp dụng. Theo Plan B của thầy,
L2 là mức chính cho pilot máy hiện tại; RF-Genesis L1 chưa được benchmark.
Chi tiết năm clip và ảnh xem nhanh nằm trong pilot_benchmark.md.

docs/e0_scenario_catalog.md là danh mục đề xuất 8 kiểu ngã, 10 ADL,
5 confounder. E0 mới có 5 clip thật và chưa cài confounder (để Sprint 3).
Danh mục chưa chứng minh mọi kịch bản đều có dữ liệu hay đã chạy mô phỏng.

## 3. Thông số cảm biến — bản nháp có nguồn

sensor_params.yaml ghi các lựa chọn FOV, NETD và refresh của MLX90640,
băng tần IWR6843, và tốc độ Taramasco báo cáo. Chirp cụ thể của Taramasco
và MM-Fi ghi TBD vì chưa xác nhận từ nguồn. Không gán thông số phần cứng
cho lần chạy E0 proxy; FPS 30 của NTU chỉ giả định từ metadata RGB.

## Việc kế tiếp để xin thầy nghiệm thu

1. Xác nhận vài tư thế nằm bằng RGB, chọn và ghi cách chọn h_thr theo
   chiều cao COM đã có mốc sàn; kiểm tra nhầm với ADL thấp và tracking.
2. Kiểm tra độ nhạy trên nhiều cảnh/người, thời gian lặp lại, và giới hạn
   mô hình L2; chỉ thử L1 khi có máy CUDA phù hợp. Không suy ra độ trễ
   báo động 1,5 s từ thời gian render mỗi frame.
3. Đối chiếu chirp với cấu hình gốc nếu nhận được; giữ TBD khi chưa có.
4. Kiểm kê lit matrix ≥40 bài và các bài thầy chỉ định; chuẩn bị demo
   30 phút sau khi phần 1–3 đủ bằng chứng. Sprint 1 còn các việc trong
   issue S01 trước khi qua gate Research & Novelty.
