# E0 pilot benchmark — bản đo L2 đầu tiên

Trạng thái: **đã chạy thermal bản thô và RadarSimL2 trên 5 clip × 1 cảnh**.
**Chọn L2 làm mức radar chính của pilot trên máy hiện tại; L1 chưa chạy, GPU/VRAM không áp dụng.**

## Phạm vi và nguồn

- Số liệu dưới đây do người thực hiện chạy `python -m sprint1_tools.run_e0_pilot` trên máy local và cung cấp output terminal; bản báo cáo này chưa trực tiếp đọc các NPZ/CSV trên máy đó.
- Đầu vào: năm NPZ skeleton NTU RGB+D 120 từ cùng archive `nturgbd_skeletons_s001_to_s017.zip`. Hai clip A043 (ngã), ba ADL A006 (nhặt đồ), A008 (ngồi xuống), A009 (đứng dậy).
- Thermal: lưới `(24,32)`, phép chiếu trực giao Camera X/Y lên các đoạn khớp, nền/người/nhiễu giả lập; không phải nhiệt độ hoặc FOV đã hiệu chuẩn theo MLX90640.
- Radar L2: lấy điểm trên **đường nối các khớp**, tính vận tốc hướng tâm so với cảm biến ở Camera XYZ `(0,0,0)`; chưa phải điểm bề mặt người, phản xạ RF hoặc cấu hình chirp IWR6843.
- Cùng một bounds cảnh được tính từ năm pose cộng lề 0,2 m: Camera X `[−1,1196665; 0,8069512] m`, Camera Y `[−1,138991; 1,0440115] m`; cảm biến giả định tại camera `(0,0,0)`. Cấu hình gốc ở `reports/e0_pilot_l2_run1/config.json`. FPS=30 chỉ là giả định từ metadata RGB, chưa có timestamp skeleton độc lập.
- Python 3.11.7, NumPy 2.4.6 theo thông tin người thực hiện cung cấp. Probe sau lần chạy: không có `conda` hoặc `nvidia-smi` trong PATH; PyTorch đã cài nhưng `torch.cuda.is_available()` là `False`. Commit Git được báo là `36bdf12` (`docs: record RGB review and hthr pilot limitations`); **chưa xác nhận** đây là commit chứa các module mô phỏng dùng cho run, nên không gọi đó là mã nguồn được đóng băng cho benchmark. CPU/RAM chưa được ghi nhận.
- Mỗi clip chạy lạnh một lượt; số đo tách thời gian tạo thermal, L2, ghi NPZ nén. Không tính thời gian đọc NPZ. Chưa warm-up hay lặp để báo biến thiên.
- Theo [README chính thức của RF-Genesis](https://github.com/Asixa/RF-Genesis/blob/main/README.md), phần mềm tác giả thử trên Ubuntu 20.04.5, Python 3.10, conda và GPU CUDA; mô hình radar mẫu dùng AWR1843 3TX/4RX. Máy chạy pilot hiện báo Windows/Python 3.11.7 và PyTorch không thấy CUDA. Đây là đánh giá điều kiện chạy ban đầu, **không phải log đã thử và thất bại với L1**, cũng không phải cấu hình IWR6843 của Taramasco/MM-Fi.

## Số đo lần chạy 1

| Clip | Vai trò | Frame | Thermal ms/frame | L2 ms/frame | Ghi file ms/frame | NPZ bytes |
|---|---|---:|---:|---:|---:|---:|
| S001C001P001R001A043 | Ngã | 85 | 0,589 | 0,014 | 0,279 | 255687 |
| S001C001P008R001A043 | Ngã | 63 | 0,577 | 0,015 | 0,284 | 190739 |
| S001C001P008R001A006 | Nhặt đồ | 83 | 0,586 | 0,013 | 0,282 | 250471 |
| S001C001P008R001A008 | Ngồi xuống | 85 | 0,611 | 0,012 | 0,277 | 256541 |
| S001C001P008R001A009 | Đứng dậy | 63 | 0,587 | 0,013 | 0,273 | 190461 |

Tổng: **379 frame**, **1.143.899 bytes** đầu ra NPZ của năm clip. Trung bình có trọng số theo frame, **tính lại từ số terminal đã làm tròn ba chữ số**: thermal ~0,591 ms/frame, L2 ~0,013 ms/frame, ghi file ~0,279 ms/frame. Các tổng này không bao gồm CSV/JSON và không phải VRAM.

## Kiểm tra đầu ra và ảnh xem nhanh

Người thực hiện đã đọc lại năm NPZ và xác nhận các mảng có kích thước lần lượt theo thứ tự bảng: thermal `(85,24,32)`, `(63,24,32)`, `(83,24,32)`, `(85,24,32)`, `(63,24,32)`; radar tương ứng `(85,60,4)`, `(63,60,4)`, `(83,60,4)`, `(85,60,4)`, `(63,60,4)`. Ảnh ghép `reports/e0_pilot_l2_run1/thermal_five_clips_review.png` thể hiện frame giữa và cuối của mỗi clip. Ở **mười frame được xem**, hình người nằm trong ảnh; hai clip ngã có hình cuối thấp và trải ngang hơn, ba ADL vẫn hiện người. Ảnh rời rạc này chưa kiểm tra tất cả frame hoặc đối chiếu từng frame với RGB; đường viền góc cạnh phản ánh mô phỏng đường khớp trên lưới 24×32, không phải đặc tính được xác thực của cảm biến nhiệt.

## Quyết định mức radar trong pilot

Dùng **RadarSimL2 làm mức chính trên máy hiện tại**, theo Plan B trong yêu cầu Sprint 2: đã tạo được đầu ra và đo thời gian cho đúng năm clip; probe không thấy GPU CUDA mà RF-Genesis bản chính thức yêu cầu. **L1 chưa được benchmark, không có bằng chứng L1 chậm hơn L2.** Quyết định này chỉ áp dụng cho pilot trên máy hiện tại, không khẳng định L2 tương đương L1 về độ trung thực RF.

## Giới hạn và việc phải làm để kết luận E0

1. Đối chiếu bảng với `reports/e0_pilot_l2_run1/measurements.csv` (terminal PowerShell hiện cắt cột), ghi CPU/RAM, commit thực sự chứa mã mô phỏng của run, cách tạo năm NPZ và trạng thái tracking. Chưa có số đo CPU/RAM trong output được cung cấp.
2. Kiểm tra toàn bộ frame để định lượng cắt biên và các điểm radar ngoài vùng hợp lệ; ảnh ghép mới kiểm tra hai frame mỗi clip, chưa xem trực quan radar. Chưa xác thực giá trị cảm biến hoặc hành vi Doppler bằng dữ liệu radar thật.
3. RadarSimL1 (RF-Genesis) chưa thử trên một máy CUDA tương thích. Probe máy hiện tại cho thấy PyTorch CUDA `False`, thiếu conda và không có lệnh `nvidia-smi`; theo điều kiện chạy do tác giả nêu, **chọn RadarSimL2 làm mức chính cho pilot máy hiện tại (Plan B)**. Khi có máy CUDA, thử L1 riêng rồi mới so sánh tốc độ/VRAM; **không điền số đo L1 hoặc VRAM khi chưa đo**.
4. Bổ sung `sensor_params.yaml` với nguồn/đơn vị và `TBD` cho số chưa chắc; khi đổi thông số cảnh phải chạy benchmark mới, không gán ngược cấu hình mới cho lần chạy này.

Đây là **benchmark hiệu năng mô phỏng thô**, không chứng minh chất lượng phát hiện ngã, độ trung thực ảnh nhiệt/radar hoặc mục tiêu độ trễ báo động 1,5 s.
