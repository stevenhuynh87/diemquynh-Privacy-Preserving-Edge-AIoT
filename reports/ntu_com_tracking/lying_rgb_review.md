# Đối chiếu RGB cho ngưỡng thăm dò 0,25 m

Trạng thái: Phần 1 PhysicsExtractor đã có code và test tổng hợp;
h_thr từ COM khi nằm của vài clip vẫn chưa được xác thực.
0,25 m là mức pilot thăm dò, không phải ngưỡng đã chứng minh.

## Quy ước phép thử

Proxy theo từng clip = COM Camera Y trừ trung vị Camera Y của
FootRight tracked trong 20 frame đứng đầu. Chưa hiệu chuẩn mặt sàn.
Không đồng nhất proxy này với độ cao vật lý h trong PhysicsExtractor.

## Kết quả đã quan sát

- P008 A043 (ngã): chuỗi dưới 0,25 m dài nhất 21 frame.
- P008 A008 (ngồi): 0 frame.
- P008 A006 (nhặt đồ): 3 frame.
- S012C001P007R002A043, body 72057594037933135:
  FootRight tracked 20/20 frame đầu; baseline Camera Y = -0,701 m.
  Proxy thấp nhất = -0,120 m; 32/67 frame dưới 0,25 m,
  liên tục từ frame 36 đến 67.
  Trong 32 frame thấp: 0/32 frame có đủ 17 khớp COM tracked;
  0/32 frame có khớp COM untracked; các frame đều có khớp inferred.

## Kiểm tra RGB S012

Video S012 có 67 frame, metadata 30 FPS.
Ở frame 58–67, người chống hai tay và co chân; không nằm tựa
toàn thân trên sàn. Vì vậy không dùng các frame này làm mẫu
"COM khi nằm" để chọn h_thr. Đây là phản ví dụ cho việc suy ra
tư thế nằm chỉ từ proxy dưới 0,25 m.

## Giới hạn và việc còn thiếu

- Camera Y chưa được hiệu chuẩn theo pháp tuyến và mốc mặt sàn.
- FPS của skeleton chưa được xác minh độc lập bằng timestamp.
- Tọa độ COM ở đoạn thấp phụ thuộc nhiều khớp inferred.
- Chưa có vài clip được RGB xác nhận nằm để chọn h_thr theo
  yêu cầu của thầy ngày 22/11/2026.
- Chưa kết luận 0,25 m phát hiện ngã đúng; một đặc trưng h thấp
  không tự quyết định nhãn té ngã.

Bước tiếp theo: gửi PhysicsExtractor, kết quả test và giới hạn
ngưỡng cho thầy xem; xin nhận xét về cách chọn h_thr. Sau đó
triển khai pilot E0 theo thứ tự thầy phân công, không đánh dấu
Phần 1 hoàn tất khi điều kiện chọn ngưỡng vẫn còn thiếu.
