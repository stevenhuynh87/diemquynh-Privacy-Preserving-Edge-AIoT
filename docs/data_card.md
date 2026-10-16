# Thẻ dữ liệu Taramasco — phiên bản v0

Cập nhật: 16/10/2026
Dự án: phykd_fall
Phạm vi: Kiểm tra dữ liệu cục bộ và thử nghiệm CNN ảnh nhiệt
trong Sprint 1/26.

## 1. Nguồn dữ liệu và mục đích sử dụng

Dữ liệu: bộ dữ liệu ngã đa cảm biến đi kèm bài báo dưới đây.

DOI dữ liệu:
https://doi.org/10.17605/OSF.IO/YJGDV

Bài báo tham khảo:
Taramasco và cộng sự (2025).
Multimodal dataset for sensor fusion in fall detection.
PeerJ, 13:e19004.

DOI bài báo:
https://doi.org/10.7717/peerj.19004

Bài báo mô tả các tình huống ngã được thực hiện có chủ đích
trong môi trường kiểm soát, với 10 người tham gia.

Đây là số đo cảm biến được ghi thực tế trong các tình huống
được dàn dựng; không phải bằng chứng về hiệu quả phát hiện
các ca ngã tự nhiên ngoài thực tế.

Mục đích trong Sprint 1:
- Kiểm tra cấu trúc và khả năng đọc dữ liệu.
- Audit số dòng, timestamp, tần số lấy mẫu và annotation.
- Xây dựng bộ đọc dữ liệu.
- Huấn luyện thử CNN nhỏ trên ảnh nhiệt.

Thư mục dữ liệu đang sử dụng:
`data/Taramasco/dataset`.

## 2. Quy mô dữ liệu cục bộ

- 10 người tham gia, tương ứng subject_1 đến subject_10.
- 40 CSV cảm biến: mỗi subject có bốn modality.
- 5 bảng phụ ở thư mục gốc.
- Các bảng annotation mang tên cảm biến ở thư mục gốc
  không được xem là bản ghi cảm biến liên tục khi tính tần số.

| Cảm biến | Tổng số dòng của 10 subject |
| --- | ---: |
| Accelerometer | 81.250 |
| Camera nhiệt | 11.877 |
| LiDAR | 44.226 |
| Radar | 36.838 |

Đây là số dòng của từng luồng cảm biến, không phải số mẫu
đa cảm biến đã đồng bộ hoặc số lần ngã.

Số dòng chi tiết theo từng subject/cảm biến:
[frequency_audit_sprint1.csv](../reports/frequency_audit_sprint1.csv).

## 3. Cảm biến và tần số quan sát được

| Cảm biến | Median khoảng cách timestamp dương | Tần số ước lượng |
| --- | --- | --- |
| Camera nhiệt MLX90640 | Khoảng 0,384 giây | 2,59–2,61 Hz |
| Radar mmWave | Khoảng 0,120 giây | 8,31–8,33 Hz |
| LiDAR | Khoảng 0,100 giây | Khoảng 10 Hz |
| Accelerometer | Khoảng 0,016 giây | Khoảng 62,5 Hz |

Tần số được ước lượng bằng nghịch đảo median của các
chênh lệch timestamp dương trong từng file.

Các giá trị này không có nghĩa dữ liệu được lấy mẫu đều
và liên tục trong toàn bộ thời lượng bản ghi.

Frequency audit ban đầu đã kiểm tra đủ 40 CSV cảm biến:
- 13 file có trạng thái ok.
- 26 file cần xem xét lấy mẫu không đều.
- 1 file cần xem xét lỗi thứ tự timestamp.

Báo cáo timestamp từ bộ đọc đã cập nhật:
[taramasco_loader_audit_v2.csv](../reports/taramasco_loader_audit_v2.csv).
Kết quả gồm 40 bản ghi cảm biến của 10 subject:
- 28 bản ghi có trạng thái ok.
- 11 bản ghi có trạng thái REVIEW_IRREGULAR_SAMPLING.
- 1 bản ghi có trạng thái REVIEW_TIMESTAMP_ERRORS.

Trong audit v2, khoảng trống lớn được đánh dấu khi lớn hơn
ba lần median khoảng cách timestamp dương của file.
Đây là ngưỡng kiểm tra do dự án chọn.
Chưa đối chiếu xong toàn bộ tiêu chí với công cụ frequency audit ban đầu.
Giữ riêng cả hai báo cáo; chênh lệch số lượng cờ cảnh báo
không có nghĩa dữ liệu gốc đã được sửa hoặc tự hết vấn đề.
Audit timestamp cũng không xác nhận toàn bộ payload cảm biến đã hợp lệ.

## 4. Timestamp và khả năng đọc dữ liệu

Timestamp cảm biến là giá trị số, đơn vị giây.
Bộ đọc thermal/radar giữ timestamp ở kiểu float64.

### Camera nhiệt

- Mỗi dòng gồm timestamp và 768 giá trị pixel.
- Độ phân giải danh định: rộng 32 × cao 24.
- Quy ước tensor đang dùng: (N, 1, 24, 32), float32.
- Subject 1 đọc được đủ 1.785 frame.
- Kiểm tra giá trị pixel hữu hạn đã PASS trên Subject 1.
- Thứ tự trải phẳng pixel và hướng không gian của ảnh
  vẫn cần được xác minh đầy đủ.

### Radar

Kiểm tra payload của Subject 1:
- Đọc được 5.396 frame và timestamp.
- Dữ liệu điểm được giữ thành các nhóm bảy giá trị,
  theo đúng thứ tự cột gốc.
- Giữ lại 242 frame rỗng cùng timestamp tương ứng.
- Các giá trị payload đã kiểm tra đều hữu hạn.

Kết quả trên không xác nhận toàn bộ payload radar của
mọi subject đã được giải mã hoặc hiệu chuẩn đầy đủ.

Đồng bộ giữa các modality và cách diễn giải các trường
LiDAR chưa được xác minh đầy đủ tại dự án.

CNN thử nghiệm chỉ dùng ảnh nhiệt.
Chưa áp dụng nội suy giữa các cảm biến.

## 5. Annotation ngã gốc

Bảng thời điểm ngã ở thư mục gốc chứa 100 timestamp,
được sắp thành 10 sự kiện × 10 cột subject.

Bộ đọc xử lý tên file fall/falls hiện có trong dữ liệu cục bộ.

Các bảng mang tên cảm biến ở thư mục gốc cung cấp chỉ số
frame tương ứng. Chưa kết luận chắc chắn chỉ số bắt đầu
từ 0 hay từ 1.

Đã đối chiếu 100 timestamp ngã với timestamp camera nhiệt:
- Không có sự kiện nằm ngoài bản ghi.
- Sai lệch đến frame gần nhất lớn nhất: 0,226928 giây.

Đối chiếu frame gần timestamp nhất không phải là sửa
annotation gốc và không chứng minh annotation đúng trực quan.

Với 99 cửa sổ ngã được giữ lại, chỉ số frame tác giả cung cấp
đều nằm trong cửa sổ theo ít nhất một cách hiểu chỉ số
bắt đầu từ 0 hoặc từ 1.

Kiểm tra này không xác định được index base và không thay
thế việc xác minh trực quan.

Đã xem trực quan hai sự kiện để điều tra annotation.

## 6. Các vấn đề chất lượng dữ liệu đã phát hiện

### Subject 8 — accelerometer

Timestamp đi lùi 66,984 giây giữa dòng dữ liệu 6250 và 6251.

Chưa xác định nguyên nhân.
Chưa sửa timestamp, sắp xếp lại hoặc thay thế dữ liệu gốc.

Vấn đề này thuộc luồng accelerometer; không tự động có nghĩa
dữ liệu ảnh nhiệt của Subject 8 cũng bị lỗi.

### Subject 3 — sự kiện 2

Trong phép đối chiếu hiện tại của dự án, timestamp ngã và
chỉ số frame nhiệt tác giả cung cấp dẫn đến hai vị trí khác nhau.
Chưa xác định nguyên nhân và chưa kết luận annotation của tác giả sai.

Khi hiểu chỉ số từ 1:
- Dòng tác giả cung cấp: 391.
- Dòng gần timestamp ngã nhất: 367.

Sự kiện này tạm không được chọn vào bảng cửa sổ cho pilot CNN nhiệt,
với lý do `annotation_conflict_pending_review`.
Đây là quyết định chọn mẫu của dự án trong khi chờ xác minh.

Giữ nguyên toàn bộ file cảm biến và cả hai annotation gốc.
Bảng thời điểm ngã gốc vẫn có đủ 100 mốc; việc chọn mẫu pilot
không xóa, sửa, sắp xếp lại hoặc thay thế các mốc đó.

Bằng chứng liên quan:
- [fall_frame_alignment.csv](../reports/fall_frame_alignment.csv)
- [window_annotation_check.csv](../reports/window_annotation_check.csv)
- [thermal_window_candidates_summary.json](../reports/thermal_window_candidates_summary.json)

## 7. Nhãn cửa sổ được xây dựng trong dự án

CNN sử dụng nhãn cửa sổ đề xuất, chưa phải ground truth
đã được xác minh độc lập cho từng frame.

Quy tắc:
- Mỗi cửa sổ dài 4 giây.
- Cửa sổ ngã lấy từ 2 giây trước đến 2 giây sau timestamp ngã.
- Tỷ lệ mục tiêu ngã:không ngã là 1:3.
- Cửa sổ không ngã được chọn ngoài các vùng sự kiện được bảo vệ.
- Loại cửa sổ không ngã nếu giao với vùng ±4 giây quanh
  timestamp ngã.
- Với sự kiện còn tranh chấp, bảo vệ thêm vùng quanh cả hai
  cách hiểu chỉ số frame tác giả cung cấp.
- Loại cửa sổ vượt ngoài bản ghi hoặc có khoảng trống
  timestamp lớn hơn ba lần median khoảng cách timestamp dương.
- Khoảng thời gian sử dụng quy ước [start_s, end_s).
- Mỗi cửa sổ được giữ lại chứa 8–14 frame nhiệt.

Bài báo, mục Dataset segmentation, mô tả cửa sổ quanh timestamp,
đưa ví dụ ±2 giây và tỷ lệ ngã:không ngã 1:3.
Nguồn: [bản toàn văn trên PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11970414/).

Vùng bảo vệ bổ sung và ngưỡng loại khoảng trống timestamp
là lựa chọn xử lý của dự án, không phải annotation gốc
của tác giả.
Việc tạm không dùng S3–Event 2 trong pilot cũng là lựa chọn
của dự án và phải được nêu khi báo cáo kết quả.

## 8. Chia tập và chuẩn hóa

Seed: 42.
Đơn vị chia tập: subject.

| Tập | Subject | Cửa sổ ngã đề xuất | Cửa sổ không ngã đề xuất |
| --- | --- | ---: | ---: |
| Train | 1–6 | 59 | 177 |
| Validation | 7–8 | 20 | 60 |
| Test | 9–10 | 20 | 60 |

Tổng cộng: 396 cửa sổ đề xuất.
Trong 100 mốc ngã gốc, 99 mốc được chọn để tạo cửa sổ ngã
cho pilot: 59 thuộc train, 20 thuộc validation và 20 thuộc test.
Subject 3, sự kiện 2 thuộc train tạm không được sử dụng
vì bất nhất annotation đang chờ xác minh.
Kết quả pilot vì vậy không đại diện cho việc sử dụng đầy đủ
toàn bộ annotation gốc.

Chuẩn hóa chỉ được tính từ các frame riêng biệt thuộc
cửa sổ train:
- Số frame train riêng biệt: 2.537.
- Trung bình pixel toàn cục: khoảng 24,384259.
- Độ lệch chuẩn tổng thể: khoảng 1,762894.

Validation và test dùng lại thống kê đã lưu của train.
Không tính thông số chuẩn hóa từ validation hoặc test.

Thông số chuẩn hóa đã lưu của pilot:
[thermal_normalization.json](../reports/thermal_normalization.json).

Danh sách cửa sổ:
[thermal_window_candidates.csv](../reports/thermal_window_candidates.csv).

## 9. Thử nghiệm CNN ảnh nhiệt

CNN có 1.282 tham số, xử lý từng frame nhiệt.
Điểm đầu ra chưa chuyển thành xác suất (logits) của các frame
được lấy trung bình để phân loại cả cửa sổ 4 giây.

Đã giữ lại hai lần huấn luyện, mỗi lần 20 epoch:
- Baseline dùng cross-entropy không trọng số.
- Lần có trọng số [2/3, 2], tương ứng [không ngã, ngã].

Phương án có trọng số được chọn dựa trên balanced accuracy
và F1 ngã của validation.

Checkpoint epoch 20 của phương án này được chọn bằng
validation loss, sau đó đánh giá trên Subject 9–10.

Bước đánh giá test không cập nhật tham số mạng.

Các đầu ra của pilot được script tự sinh:
- [Validation baseline](../reports/cnn_pilot_20261016_162316_766339/best_validation.json)
- [Validation có trọng số](../reports/cnn_pilot_20261016_164312_452288/best_validation.json)
- [Kế hoạch đánh giá](../reports/cnn_pilot_20261016_164312_452288/test_evaluation/evaluation_plan.json)
- [Chỉ số test](../reports/cnn_pilot_20261016_164312_452288/test_evaluation/metrics.json)
- [Dự đoán test](../reports/cnn_pilot_20261016_164312_452288/test_evaluation/predictions.csv)
- [Ma trận nhầm lẫn](../reports/cnn_pilot_20261016_164312_452288/test_evaluation/confusion_matrix.csv)

Không chỉnh tay các file số đo/kết quả tự sinh.

Không dùng kết quả test để điều chỉnh mô hình rồi tiếp tục
báo cùng tập test đó như một phép đánh giá độc lập.

## 10. License và quyền truy cập

Trạng thái license tái sử dụng dataset: CHƯA XÁC NHẬN.

Trong Sprint 1, sinh viên quan sát thấy mục OSF ghi
"No License", trong khi nội dung Sprint đề cập CC-BY.

Sự khác biệt này cần được làm rõ.

Việc tải được dữ liệu không tự xác nhận quyền nghiên cứu
hoặc tái phân phối.

Không suy ra license của dataset được lưu riêng trên OSF
chỉ từ license của bài báo.

Cần làm rõ quyền nghiên cứu, công bố và tái phân phối với
cố vấn và chủ sở hữu dữ liệu.

Không công khai dữ liệu gốc hoặc sản phẩm dữ liệu dẫn xuất
khi các quyền áp dụng vẫn chưa được làm rõ.

Hướng dẫn license của OSF:
https://help.osf.io/article/148-licensing

## 11. Giới hạn và ghi chú về tính liêm chính

- Chỉ có 10 người tham gia và các tình huống ngã được dàn dựng.
- Kết quả test chỉ gồm 80 cửa sổ của hai subject được giữ riêng.
- Tập test có tỷ lệ ngã:không ngã 1:3 theo cách chọn cửa sổ;
  các chỉ số này không phản ánh tần suất ngã tự nhiên.
- Nhãn cửa sổ đề xuất chưa được xác minh trực quan toàn bộ.
- Chỉ số theo cửa sổ không tương đương chỉ số theo từng frame
  hoặc hiệu quả phát hiện ngã liên tục ngoài thực tế.
- Tỷ lệ báo ngã nhầm trên cửa sổ được chọn không phải
  số lần báo động giả mỗi giờ.
- Hướng không gian của ảnh nhiệt và đồng bộ đa cảm biến
  chưa được xác minh đầy đủ.
- Các bất nhất timestamp/annotation được ghi nhận và giữ dấu vết.
- Không chỉnh sửa các file gốc của tác giả.
- Giữ lại cả baseline kém và lần huấn luyện có trọng số.
- Code và tài liệu có hỗ trợ từ ChatGPT/Codex; lưu lại
  các bước thực thi và đầu ra để con người kiểm tra.
- Đây là thẻ dữ liệu cho thử nghiệm nghiên cứu ban đầu,
  chưa xác nhận dataset hoặc mô hình đã sẵn sàng công bố
  hay triển khai thực tế.
