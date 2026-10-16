# Ghi chú kiểm tra dữ liệu Taramasco

Cập nhật: 16/10/2026. Phạm vi: audit dữ liệu và pilot CNN ảnh nhiệt Sprint 1.

Các bảng cửa sổ và kết quả do script tạo được lưu riêng trong `reports/`.
Giữ nguyên các file cảm biến và bảng annotation gốc của tác giả.

## subject_8 — accelerometer.csv

- File: data/Taramasco/dataset/subject_8/accelerometer.csv
- Tổng số dòng: 8125.
- Timestamp đi lùi tại ranh giới dòng 6250 → 6251:
  - Dòng 6250: 1701273122.984
  - Dòng 6251: 1701273056.000
  - Chênh lệch: -66.984 giây.
- Hai đoạn theo thứ tự dòng:
  - Đoạn 1: dòng 1–6250.
  - Đoạn 2: dòng 6251–8125.
- Khoảng thời gian của hai đoạn chồng nhau.
- Không phát hiện timestamp trùng chính xác.
- Chưa xác định nguyên nhân; chưa kết luận giá trị cảm biến có bị lặp.
- Giữ nguyên file gốc. Chưa dùng file này để tạo cửa sổ
  đa cảm biến trước khi xác minh cách xử lý.
- Trạng thái: cần kiểm tra thêm.
## Đối chiếu mốc té với camera nhiệt

- Đã so sánh bảng falls.csv, bảng ir_camera.csv ở thư mục
  dataset và timestamp trong các file camera nhiệt từng subject.
- Chưa xác nhận quy ước chỉ số bắt đầu từ 0 hay 1.
- Subject 3, sự kiện 2:
  - Bảng chỉ số ghi 391.
  - Nếu đếm từ 1, dòng 391 lệch mốc té 9.385950 giây.
  - Dòng gần mốc té nhất là 367, lệch 0.103035 giây.
- Chưa xác định nguyên nhân không khớp; giữ nguyên file gốc.
- Đã đối chiếu đủ 100 mốc với timestamp camera nhiệt:
  0 mốc nằm ngoài bản ghi; sai lệch tới frame gần nhất
  lớn nhất là 0,226928 giây.
- Kết quả lưu tại [fall_frame_alignment.csv](fall_frame_alignment.csv).
- Đây là ánh xạ để kiểm tra, không thay thế annotation gốc
  và không chứng minh nhãn đúng về mặt trực quan.
- Đã xem trực quan hai sự kiện; chưa xác minh toàn bộ annotation.

### Kiểm tra trực quan subject 3, sự kiện 2

- Đã xem 59 khung quanh timestamp trong falls.csv.
- Quanh dòng 367 chưa thấy rõ chuyển động ngã.
- Khoảng dòng 391–393 có chuyển động từ dạng dọc xuống
  thấp, trải ngang; có vẻ phù hợp với ngã.
- Chỉ số tác giả cung cấp là 391.
- Chưa xác nhận ý nghĩa khác nhau giữa hai bảng đánh dấu.
- Không thay nhãn gốc; chưa dùng sự kiện này làm nhãn
  huấn luyện đã xác minh.

Quyết định cho pilot:
- Tạm không chọn S3–Event 2 vào bảng cửa sổ.
- Lý do lưu trong summary: `annotation_conflict_pending_review`.
- Khi chọn cửa sổ không ngã, bảo vệ vùng ±4 giây quanh
  timestamp sự kiện và quanh timestamp tương ứng với cả hai
  cách hiểu chỉ số frame (bắt đầu từ 0 hoặc từ 1).
- Chưa kết luận annotation của tác giả sai; chưa tự sửa mốc hoặc chỉ số.
- Dataset gốc vẫn đủ 100 mốc. Việc tạm bỏ một sự kiện chỉ áp dụng
  cho bảng mẫu pilot, không phải xóa dữ liệu của tác giả.
- Quyết định này đã được ghi trong cấu hình/bảng mẫu trước khi train;
  khi báo cáo phải nêu việc chọn 99/100 mốc và lý do.

### Kiểm tra trực quan subject 1, sự kiện 1

- Đã xem 68 khung hình quanh mốc trong falls.csv.
- Dòng 418 có timestamp khoảng +0.08 giây so với mốc.
- Khoảng +0.48 đến +1.21 giây thấy chuyển động từ
  tư thế dọc xuống thấp và trải ngang.
- Quan sát phù hợp với sự kiện té được đánh dấu.
- Chỉ số 418 của tác giả phù hợp khi hiểu là dòng đếm từ 1.
- Đây là kiểm tra trực quan một mẫu, chưa xác nhận
  toàn bộ nhãn hoặc quy ước chỉ số của dataset.

## Cửa sổ đề xuất và chia tập cho pilot

- Cửa sổ dài 4 giây, lấy từ 2 giây trước đến 2 giây sau mốc ngã.
- Tỷ lệ mục tiêu ngã:không ngã là 1:3.
- Khoảng thời gian dùng quy ước `[start_s, end_s)`.
- Cửa sổ không ngã không được giao với vùng ±4 giây quanh mốc ngã.
- Không chọn cửa sổ vượt bản ghi, thiếu frame hoặc gặp khoảng trống
  lớn hơn ba lần median khoảng cách timestamp dương.
- Seed: 42; chia theo subject.

| Tập | Subject | Ngã đề xuất | Không ngã đề xuất |
| --- | --- | ---: | ---: |
| Train | 1–6 | 59 | 177 |
| Validation | 7–8 | 20 | 60 |
| Test | 9–10 | 20 | 60 |

Tổng: 396 cửa sổ, gồm 99 cửa sổ ngã và 297 cửa sổ không ngã.
Mỗi cửa sổ giữ lại có 8–14 frame. Nhãn vẫn là `candidate_unreviewed`.
`training_ready: false` ghi nhận trạng thái nhãn còn chờ xác minh;
CNN đã được chạy dưới dạng pilot với nhãn đề xuất.

Quy tắc ±2 giây và 1:3 được mô tả trong mục Dataset segmentation
của [Taramasco et al. (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11970414/).
Vùng bảo vệ bổ sung, ngưỡng khoảng trống và việc tạm không dùng
S3–Event 2 là lựa chọn xử lý của dự án.

Nguồn: [bảng cửa sổ](thermal_window_candidates.csv),
[summary](thermal_window_candidates_summary.json) và
[cấu hình chia tập](../configs/sprint1_split.json).

## Đối chiếu các file pilot đã lưu

Đã kiểm tra lại bảng CSV, summary, mã nguồn chuẩn hóa/train/test
và các dự đoán test được cung cấp để rà soát:
- 396 dòng CSV khớp số lượng và subject split trong summary.
- Không có cửa sổ trùng hoặc chồng frame trong cùng subject.
- S3–Event 2 không nằm trong bảng mẫu; các cửa sổ không ngã
  tránh các vùng bảo vệ đã đối chiếu từ bảng mẫu và mốc sự kiện đã biết.
- Có đúng 2.537 frame train riêng biệt; số lượng theo subject
  khớp hồ sơ chuẩn hóa đã lưu.
- SHA-256 của bảng cửa sổ khớp `manifest_sha256` trong protocol đã cung cấp:

```text
59634b59cb48117a0748b9235f81a5d4ac353cdea843eba28d431c95dcf98966
```

- Đủ 80 dòng dự đoán test khớp thông tin cửa sổ trong manifest.
- Tính lại từ dự đoán được TN=44, FP=16, FN=1, TP=19;
  cả năm chỉ số khớp `metrics.json`.
- Kiểm tra chuẩn hóa bằng dữ liệu giả xác nhận chỉ mở các file train
  và mỗi frame được tính một lần khi cửa sổ chồng nhau.
- Rà soát mã nguồn và tính lại chỉ số từ dự đoán đã lưu;
  không chạy lại train hoặc suy luận test trong lần rà soát này.
- Chưa đối chiếu độc lập toàn bộ timestamp/pixel với các CSV cảm biến gốc
  trong lần rà soát file gửi lên.

Kết quả chỉ áp dụng cho pilot trên nhãn cửa sổ đề xuất và hai subject test.
Chưa phải kết quả đánh giá trên toàn bộ annotation gốc hoặc ngã tự nhiên.

## Hai báo cáo audit timestamp

| Báo cáo | ok | Cần xem xét lấy mẫu không đều | Cần xem xét thứ tự timestamp |
| --- | ---: | ---: | ---: |
| [frequency_audit_sprint1.csv](frequency_audit_sprint1.csv) | 13 | 26 | 1 |
| [taramasco_loader_audit_v2.csv](taramasco_loader_audit_v2.csv) | 28 | 11 | 1 |

Cả hai báo cáo có phạm vi 40 CSV cảm biến của 10 subject.
Audit v2 đọc được dòng radar có độ dài thay đổi, giữ vị trí dòng
và dùng ngưỡng khoảng trống lớn hơn ba lần median dt dương.
Đã đối chiếu mã nguồn và hai báo cáo trên cùng 40 bản ghi:
- Công cụ ban đầu sprint1_tools/frequency_audit.py dùng ngưỡng gap > 1,5 lần median dt dương.
- Audit v2 trong data/taramasco.py dùng ngưỡng gap > 3 lần median dt dương.
- Số dòng của từng bản ghi khớp giữa hai báo cáo.
- Có 15 bản ghi chuyển từ cảnh báo lấy mẫu không đều sang ok; số gap được đánh dấu của chúng giảm về 0 theo ngưỡng mới.
Đây là thay đổi tiêu chí cảnh báo của dự án, không phải bằng chứng dữ liệu đã được sửa hoặc trở thành lấy mẫu đều.
Lần đối chiếu này sử dụng mã nguồn và báo cáo đã lưu; không chạy lại hai công cụ trên dữ liệu gốc.
Giữ cả hai báo cáo; không diễn giải thay đổi số cờ cảnh báo
thành việc dữ liệu gốc đã được sửa hoặc hết lỗi.

## Các giới hạn còn mở

- Nguyên nhân timestamp lùi của accelerometer Subject 8.
- Ý nghĩa chính xác của hai loại annotation và bất nhất S3–Event 2.
- Thứ tự trải phẳng pixel và hướng không gian ảnh nhiệt.
- Đồng bộ đa cảm biến và kiểm tra payload ngoài phạm vi đã báo cáo.
- License tái sử dụng dataset Taramasco còn chưa xác nhận.
  Xem [data card](../docs/data_card.md).

Giữ riêng cả baseline và lần train có trọng số; không chỉnh tay
các file số đo tự sinh hoặc dùng kết quả test để tinh chỉnh rồi
báo lại cùng test như một phép đánh giá độc lập.
