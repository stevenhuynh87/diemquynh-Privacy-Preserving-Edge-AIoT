# phykd_fall - Báo cáo Sprint 1/26

Sprint: 01/10/2026-18/10/2026 | Cập nhật: 18/10/2026
Project: C:\phykd_fall | Nhánh bàn giao: main

## 1. Mục tiêu và kết quả

Mục tiêu Sprint: xác minh gap/novelty, tiếp cận dữ liệu, dựng môi trường, viết TaramascoDS, audit dữ liệu và chạy bài tập CNN nhiệt theo yêu cầu GitHub của cố vấn.

| Hạng mục | Kết quả và bằng chứng |
| --- | --- |
| Literature matrix v0 | Đã hoàn thành 25 bài S1; giữ thêm bốn bài S2 đã đọc sớm, tổng cộng 29 công trình trong docs/lit_matrix.xlsx. A1 đã đọc; phần toàn văn IEEE đi kèm A5 còn vướng ở Mục 4. |
| Môi trường và repo | Đã chuyển project khỏi OneDrive; .venv/PyTorch CPU hoạt động. Code và công cụ kiểm tra được quản lý trên main local. |
| TaramascoDS | data/taramasco.py có thermal_frames, radar_frames, timestamps, label và subject. Subject 1: 1.785 frame nhiệt 24x32; 5.396 frame radar, giữ 242 frame rỗng. Annotation gốc được giữ nguyên. |
| Audit dữ liệu | 10 subject, 40 CSV cảm biến. Tần số từ median dt dương: nhiệt 2,59-2,61 Hz; radar 8,31-8,33 Hz; LiDAR khoảng 10 Hz; accelerometer khoảng 62,5 Hz. Có 100 mốc ngã; không có mốc ngoài bản ghi nhiệt; sai lệch nearest-frame tối đa 0,226928 s. |
| Dataset khác | MM-Fi E01/S01/A01: depth, keypoint RGB/IR và ground_truth đọc PASS; LiDAR/mmWave/WiFi-CSI chưa giải mã. NTU đã đăng ký truy cập; đọc một skeleton trong mỗi ZIP PASS. UR Fall: hai ZIP depth và bốn CSV đọc PASS trong phạm vi sample. |
| Kiểm tra và tài liệu | Pytest đã lưu: 18 passed trong 9,29 s; pre-commit đã pass trên source/config đã kiểm tra. Đã có README.md, docs/data_card.md v0 và reports/data_audit_notes.md. |

Audit ban đầu dùng gap >1,5 lần median dt dương: 13 ok / 26 cần xem xét lấy mẫu không đều / một lỗi timestamp. V2 dùng >3 lần: 28 / 11 / một. Số dòng của 40 bản ghi khớp; 15 bản ghi đổi cờ do đổi ngưỡng, không phải do sửa dữ liệu. Báo cáo: reports/frequency_audit_sprint1.csv và reports/taramasco_loader_audit_v2.csv. Sample checks lưu tại reports/mmfi_sample_check.txt, ntu_sample_check.txt và urfall_sample_check.txt.

## 2. Bài tập CNN nhiệt

CNN có 1.282 tham số; trung bình logits theo cửa sổ. Chia subject: train 1-6, validation 7-8, test 9-10. Chuẩn hóa fit trên 2.537 frame duy nhất của train: mean 24,384259; std 1,762894. Có 396 cửa sổ: 99 fall / 297 non-fall; train 59/177, validation 20/60, test 20/60.

Cửa sổ ±2 giây và tỷ lệ 1:3 kế thừa Taramasco et al. (2025) [1]. Vùng bảo vệ ±4 giây, ngưỡng gap và tạm không dùng S3-Event 2 là lựa chọn của dự án. Dữ liệu gốc vẫn giữ đủ 100 mốc. Pilot đã chạy với nhãn đề xuất; cấu hình vẫn ghi label_policy=pending và training_ready=false vì nhãn chưa được xác minh đầy đủ.

Hai pilot đã chạy 20 epoch. Baseline không trọng số: validation accuracy 75%, recall/F1 ngã bằng 0. Pilot có trọng số [2/3,2]: chọn checkpoint epoch 20 theo validation loss. Test 80 cửa sổ: accuracy 78,75%; balanced accuracy 84,17%; precision ngã 54,29%; recall 95%; F1 69,09%; TN=44, FP=16, FN=1, TP=19. Không cập nhật mạng khi test. Đây là kết quả pilot trên nhãn đề xuất, chưa phải kết quả bài báo cuối.

Hồ sơ: reports/cnn_pilot_20261016_164312_452288/; giữ cả baseline 20261016_162316_766339. Checkpoint lưu trong results/. Đối chiếu SHA-256 của 10 CSV nhiệt, checkpoint và manifest working/Git đã PASS; kết quả này xác nhận tính nhất quán của file với hồ sơ lần chạy.

<!-- PAGE_BREAK -->

## 3. Tổng hợp gap v0 và giới hạn

RF-Pose (A1) và HuPR (S1-X16) cung cấp tiền lệ giám sát tư thế từ thị giác sang radar. TaFall (A4), mmFall (A5) và ABC-HF (S1-X14) là các công trình cần đối chiếu khi sử dụng thông tin vật lý của ngã. Liang et al. (2024, S1-X18) đã dùng Kinect để giám sát cải thiện point cloud radar. Các tiền lệ này được dùng khi xác định đóng góp của đề tài; danh mục và nguồn nằm trong lit matrix.

Hướng cần khảo sát là chuyển tri thức vật lý từ teacher RGB/pose sang student nhiệt 32x24 + radar, kết hợp fusion bất đồng bộ và cổng tin cậy theo cảm biến. Đây là gap sơ bộ từ danh mục đã đối chiếu; tính mới của tổ hợp này còn cần tìm kiếm và xác minh thêm.

- Subject 8 accelerometer lùi timestamp 66,984 s giữa dòng 6250-6251; chưa xác định nguyên nhân.
- S3-Event 2 có xung đột timestamp/frame index; tạm không dùng để tạo mẫu pilot, chưa sửa annotation gốc. Mới xem trực quan 2/100 sự kiện; pixel layout và đồng bộ đa cảm biến chưa xác nhận toàn bộ.
- Sample checks không đại diện cho toàn bộ MM-Fi, NTU hoặc UR Fall. MM-Fi RGB/IR đã đọc là keypoint 2D (17,2), không phải ảnh thô.

## 4. Mục chưa hoàn tất và lý do

| Mục | Lý do, giới hạn và việc tiếp theo |
| --- | --- |
| Phần IEEE đi kèm A5 | Đã đọc mmFall; bài IEEE 8965661 đi kèm chưa đọc do chưa truy cập được toàn văn. Giữ rõ giới hạn truy cập và không tính thành bài đã đọc thêm. |
| Systematic search theo Mục 5.5; xác minh novelty | Chưa có hồ sơ truy vấn/sàng lọc đầy đủ để xác nhận hoàn tất systematic search. Cần đối chiếu Mục 5.5 của tài liệu gốc, lưu truy vấn/tiêu chí và tiếp tục xác minh gap v0. |
| Formulation Mục 3.1 và φ(t) | Chưa xác định được nội dung tham chiếu trong bộ tài liệu đã đối chiếu. PDF Brief Roadmap dẫn tới DiemQuynh_Planning_12_Month_Research_Roadmap.md nhưng không trình bày formulation tương ứng. Cần xác nhận đúng tài liệu/Mục 3.1 với cố vấn, rồi viết lại bằng lời và công thức. |
| License Taramasco | OSF hiển thị No License, khác thông tin CC-BY trong roadmap. Quyền tái sử dụng dataset chưa xác nhận; cần làm rõ giấy phép của đúng dataset/version với cố vấn hoặc tác giả. |
| Annotation và đồng bộ | Xung đột S3-Event 2 và timestamp S8 chưa được giải thích; nhãn pilot và đồng bộ đa cảm biến chưa xác minh đầy đủ. Giữ dữ liệu gốc, báo cáo các quyết định tiền xử lý và phạm vi kết quả. |

License đã kiểm tra theo điều khoản/tài liệu đã trao đổi: MM-Fi CC BY-NC 4.0; NTU ROSE Lab academic/non-commercial agreement; UR Fall CC BY-NC-SA 4.0. License bài báo Taramasco không thay thế license dataset.

## 5. Bằng chứng và ghi nhận nguồn

Đã có môi trường và dữ liệu thật đầu tiên; loader, audit và bài tập CNN pilot chạy được. Bằng chứng pytest: reports/pytest_sprint1.xml và reports/pytest_sprint1.txt. Số đo được script lưu trong reports/ hoặc results/, không sửa tay để làm đẹp kết quả. Các mục chưa hoàn tất và lý do được ghi tại Mục 4 theo Definition of Done; chưa xác nhận mọi yêu cầu Sprint đã hoàn thành.

Em sử dụng ChatGPT/Codex hỗ trợ soạn và rà code/tài liệu. Các bước kế thừa từ bài báo được ghi nguồn; lựa chọn tiền xử lý và giới hạn pilot được trình bày riêng.

[1] Taramasco et al. (2025). Multimodal dataset for sensor fusion in fall detection. PeerJ 13:e19004. https://doi.org/10.7717/peerj.19004. Dataset: https://doi.org/10.17605/OSF.IO/YJGDV.
