# Sprint 2 — Kiểm tra tracking đầu vào COM

## Phạm vi
Ba clip NTU A043 trong nturgbd_skeletons_s001_to_s017.zip.
Kiểm tra 17 khớp mà estimate_ntu_com_winter14 hiện sử dụng:
Head (4) và các khớp 5–20.
Nhóm khớp tính góc thân: Neck (3), HipLeft (13), HipRight (17).

## Kết quả
| Clip | Frames | COM toàn bộ tracked | Có inferred, không untracked | Có untracked | COM không hữu hạn | Thân toàn bộ tracked |
|---|---:|---:|---:|---:|---:|---:|
| S001C001P001R001A043 | 85 | 17 | 68 | 0 | 0 | 85 |
| S001C001P002R001A043 | 84 | 21 | 63 | 0 | 0 | 84 |
| S001C001P003R001A043 | 71 | 37 | 34 | 0 | 0 | 71 |

Khớp có số frame inferred cao nhất từng clip:
- P001: AnkleLeft, 53/85 frame.
- P002: KneeRight, 46/84 frame.
- P003: FootRight, 30/71 frame.
- HipLeft và HipRight không có frame inferred trong cả ba clip.

## Diễn giải
- Tọa độ hữu hạn không chứng minh độ chính xác của khớp hoặc COM.
- Nhiều frame COM sử dụng ít nhất một khớp inferred.
- P003 có tỷ lệ toàn bộ khớp COM tracked cao nhất trong ba clip:
  52,11%; chưa chứng minh COM chính xác hơn.
- Các khớp dùng tính góc thân đều tracked; điều này chưa xác nhận
  trục camera Y trùng phương thẳng đứng thực tế.

## Quyết định triển khai đề xuất
- Giữ nguyên frame và tracking state.
- Chưa nội suy, loại khớp hoặc thay đổi trọng số khối lượng.
- Giữ nguyên tọa độ camera; chưa hiệu chuẩn sàn.
- Chưa đưa tọa độ camera trực tiếp vào PhysicsExtractor,
  vì hàm hiện yêu cầu z hướng lên và sàn tại z = 0.
- Chưa chốt ngưỡng độ cao hoặc thời điểm chạm sàn.

## Trạng thái
Hoàn thành kiểm tra tracking cho ba clip.
Chưa hoàn thành xác thực COM trên dữ liệu thực.
Còn cần đối chiếu hệ số và mốc giải phẫu với tài liệu Winter/TaFall,
xác minh FPS, và đối chiếu video RGB khi được cấp quyền.

## Tệp minh chứng
- summary.csv
- *_frames.csv
- *_joints.csv

Các CSV nằm cùng thư mục với báo cáo này.
