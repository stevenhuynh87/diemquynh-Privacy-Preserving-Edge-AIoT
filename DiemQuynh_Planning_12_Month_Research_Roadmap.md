# DiemQuynh — 12-Month Research & Algorithm Development Roadmap

## Privacy-Preserving Edge AIoT Fall Detection via Cross-Modal Knowledge Distillation from RGB to Low-Resolution Thermal and mmWave Radar

*Hệ thống AIoT Giám sát Tư thế và Phát hiện Té ngã Bảo vệ Quyền riêng tư tại Biên: Hợp nhất Mảng Nhiệt Phân giải thấp và Radar mmWave bằng Kỹ thuật Chưng cất Tri thức Đa phương thức*

| Mục | Nội dung |
|---|---|
| Mã đề tài | DT-02 (theo `2026_09_23_DiemQuynh_Research_Topics_AIoT_CV_DL`) |
| Sinh viên | Diễm Quỳnh (IU-VNUHCMC) |
| Cố vấn | TS. Huỳnh Võ Trung Dũng (Dr. Steven Huynh) |
| Phiên bản | v1 — 01/10/2026 (thay cho các bản DT-03 lập nhầm ngày 30/09/2026) |
| Khung thời gian | 26 sprint × 2 tuần: 05/10/2026 → 03/10/2027 |
| Tài nguyên tính toán | GPU hiện có tại trường (cấu hình **TBD**, đo ở Sprint 2) |
| Phạm vi | Thuật toán, mô hình, mô phỏng, thí nghiệm trên GPU. Dữ liệu công khai + dữ liệu mô phỏng. **Không** mua/lắp cảm biến, **không** thu dữ liệu diễn ngã tại lab, **không** deployment |
| Mục tiêu | ≤ Tháng 6: conference paper (CORE B trở lên) sẵn sàng nộp. ≤ Tháng 12: journal paper Q1 sẵn sàng nộp |

---

## 0. Cách roadmap giữ đúng đề tài dưới ràng buộc simulation-only

| Thành phần trong DT-02 | Trong roadmap này | Giới hạn phải ghi trong paper |
|---|---|---|
| Teacher: video RGB + pose estimation 3D (MediaPipe / YOLOv8-Pose) | Giữ. Teacher học trên **chuỗi pose**: pose thật từ dataset công khai có RGB (NTU RGB+D 120, UR Fall, MM-Fi) và pose ground-truth trong mô phỏng | Teacher chỉ dùng khi huấn luyện; không có camera khi suy luận |
| Student: ma trận nhiệt 32×24 (MLX90640) + micro-Doppler / point cloud radar mmWave (IWR6843) | Giữ đúng cấu hình cảm biến. Dữ liệu student đến từ (a) bộ mô phỏng **FallTwin** và (b) dataset thật có đúng MLX90640 + IWR6843AOP (Taramasco et al., 2025) | Dataset thật nhỏ (10 người, 100 cú ngã) |
| Cross-Modal Knowledge Distillation (CMKD) | Giữ, và mở rộng thành **chưng cất đại lượng vật lý của cú ngã** (độ cao trọng tâm, vận tốc rơi, góc thân, thời gian nằm sàn) — phần đóng góp mới | — |
| Thu dữ liệu đồng bộ RGB + thermal + mmWave trong phòng mô phỏng, diễn ngã | **Loại** (cần phần cứng). Thay bằng mô phỏng FallTwin (chuyển động SMPL → ảnh nhiệt 32×24 + radar mmWave + pose) và dataset công khai | Khoảng cách sim-to-real phải được đo, không được bỏ qua |
| Zero-storage edge execution trên ESP32-S3 / Raspberry Pi | Chuyển thành **edge-profiled inference**: params, MACs, peak memory, INT8, độ trễ CPU giới hạn luồng | Chỉ là proxy; không claim chạy trên ESP32-S3 |
| Nhiễu thật: gió nóng, ấm đun nước, thú cưng (thermal); ngồi bệt xuống sàn (radar) | Giữ dưới dạng **confounder có kiểm soát** trong FallTwin + hard negatives | Mô hình confounder là giả định, quét độ nhạy |
| Mục tiêu sensitivity > 98%, FPR < 2%, alarm ≤ 1.5 s | Giữ làm mục tiêu đo; thêm **false alarms / 24 h** trên luồng ADL dài mô phỏng | Không cam kết đạt trên người cao tuổi thật |

**Hai điều chỉnh bắt buộc so với DT-02 gốc** (lý do ở Mục 3, 5):
1. CMKD từ RGB/pose sang RF đã có từ 2018 (RF-Pose, Zhao et al., CVPR 2018), và fall detection bằng thermal dựa trên pose/cân bằng đã có bản 2026 (TaFall, arXiv). "CMKD RGB → thermal + radar" đơn thuần là integration. Đóng góp phải nằm ở: chưng cất đại lượng vật lý (privileged information), fusion hai cảm biến **khác tần số lấy mẫu** có độ tin cậy, và khả năng chống confounder.
2. Vì không thu dữ liệu, kết quả phải được kiểm chứng trên dữ liệu thật có sẵn (Taramasco et al. 2025 — cùng loại cảm biến với DT-02) ngay trong conference paper, không chỉ trên mô phỏng.

---

## 1. Executive Summary

**Kết luận:** 🟡 **FEASIBLE WITH CONDITIONS.** DT-02 làm được trong 12 tháng với GPU của trường nếu (a) dữ liệu huấn luyện student đến từ bộ mô phỏng FallTwin + dataset công khai thay cho thu thập tại lab, (b) novelty chuyển từ "CMKD" chung sang **physics-informed, asynchronous, confounder-aware CMKD**, (c) mọi claim được kiểm chứng sim-to-real trên dataset thermal + radar thật.

**Câu hỏi trung tâm (viết lại từ focal RQ của DT-02):**

> Có thể chuyển tri thức tư thế từ teacher RGB/pose sang student chỉ dùng ảnh nhiệt 32×24 và radar mmWave để đạt độ nhạy phát hiện ngã cao, báo động giả thấp, độ trễ ≤ 1.5 s — mà không dùng hình ảnh nhận dạng khi suy luận — và kết quả học trong mô phỏng có giữ được trên dữ liệu thật không?

**Mô hình đề xuất — PhyKD-Fall (Physics-informed Cross-Modal Knowledge Distillation for Fall detection):**
- *Teacher* (chỉ khi train): bộ mã hoá chuỗi pose 3D (ST-GCN hoặc Transformer nhỏ) + bộ tính **đại lượng vật lý** φ(t): độ cao trọng tâm, vận tốc thẳng đứng, gia tốc đỉnh, góc thân, thời gian nằm sàn.
- *Student*: nhánh nhiệt (CNN nhỏ trên 32×24 theo thời gian) + nhánh radar (PointNet-lite trên point cloud hoặc CNN trên micro-Doppler) + **fusion bất đồng bộ** (hai cảm biến có tần số khác nhau) + **cổng tin cậy** theo từng modality.
- *Chưng cất*: logit KD + feature KD + **physics KD** (student phải hồi quy φ(t) của teacher) + temporal relation KD.
- *Đầu ra*: xác suất ngã, φ̂(t) (diễn giải được), thời điểm báo động.

**Bộ mô phỏng FallTwin:** chuyển động người dạng SMPL (Mixamo, AMASS/HumanML3D, chuyển động sinh từ text-to-motion) → render đồng thời (1) pose ground-truth cho teacher, (2) ảnh nhiệt 32×24 theo cấu hình MLX90640, (3) tín hiệu radar FMCW 60–64 GHz theo cấu hình IWR6843 (point cloud + micro-Doppler), với confounder có kiểm soát (nguồn nhiệt, thú cưng, luồng khí nóng, ngồi bệt, nằm ngủ) và luồng ADL 24 giờ để đo báo động giả.

**Kiểm chứng trên dữ liệu thật:**
- Taramasco et al. 2025 (*PeerJ*): MLX90640 32×24 + IWR6843AOP + LiDAR 8×8 + IMU, 10 người, 100 cú ngã, CC-BY — **cùng cảm biến với DT-02**, dùng cho test sim-to-real.
- MM-Fi (NeurIPS 2023): RGB-D + IWR6843 + LiDAR + WiFi, 40 người, 27 hành động (không có ngã) — dùng cho CMKD **thật** RGB-pose → radar ở mức đặc trưng tư thế.
- NTU RGB+D 120 (lớp *falling*), UR Fall: dữ liệu pose có ngã để huấn luyện teacher.

**Publication:**
- Conference: ưu tiên IEEE ICIP 2027 (CORE2023: B; Singapore 29/11–03/12/2027; deadline chưa công bố); IJCNN 2027 (CORE2023: B; deadline 31/01/2027) nếu kết quả kịp.
- Journal Q1: *IEEE Journal of Biomedical and Health Informatics* (SJR 2025 Q1), *IEEE Internet of Things Journal* (SJR 2025 Q1), *IEEE Sensors Journal* (SJR 2025 Q1 — có trong DT-02).

**Điều kiện giữ màu vàng:**
- C1. Sprint 1–2: không có công trình đã làm physics-descriptor distillation + fusion thermal–radar bất đồng bộ cho fall detection.
- C2. Sprint 2: tải được dataset Taramasco (OSF) và MM-Fi; license cho phép nghiên cứu.
- C3. Cuối Sprint 6: FallTwin tạo được dữ liệu mà thống kê cơ bản (số điểm/khung radar, phân bố Doppler, phân bố nhiệt độ pixel người) nằm trong khoảng của dữ liệu thật.
- C4. GPU ≥ 8 GB, ≥ 20 GPU-giờ/tuần (giả định); sinh viên đạt mức PyTorch trung bình trước Sprint 3.

---

## 2. Current Research Status

Nguồn: `2026_09_23_DiemQuynh_Research_Topics_AIoT_CV_DL.pdf` (bản PDF hiện có trong folder; bản `.md` cùng nội dung đã được đọc ngày 30/09/2026).

### 2.1 Nội dung của DT-02

| Hạng mục | Nội dung trong file | Trạng thái |
|---|---|---|
| Research problem | Giám sát té ngã 24/7 cho người cao tuổi trong không gian riêng tư (phòng ngủ, nhà tắm) mà không dùng camera | **PARTIAL** — rõ bối cảnh, chưa có formulation |
| Research gap | RGB vi phạm riêng tư; wearable bị quên đeo/sạc; thermal 32×24 nhiễu bởi gió nóng, ấm đun, thú cưng; radar nhầm ngồi bệt với ngã | **PARTIAL** — đúng hướng, chưa đối chiếu literature (Mục 5) |
| Research questions | 1 focal RQ: sensitivity > 98%, FPR < 2% chỉ với thermal + radar | **PARTIAL** — viết lại thành RQ1–RQ5 |
| Research objectives | Ngầm định | **PARTIAL** |
| Existing methodology | Teacher RGB + pose 3D (MediaPipe / YOLOv8-Pose); student nhẹ trên thermal 32×24 + micro-Doppler; distillation loss; zero-storage edge | **PARTIAL** — có ý tưởng khối, chưa có công thức, loss cụ thể, protocol |
| Existing code/model | Không có | **NOT STARTED** |
| Existing datasets | Tự thu đồng bộ RGB + thermal + mmWave với các kịch bản ngã/ADL | **NOT STARTED**; dạng thu thập này **bị loại** bởi ràng buộc |
| Existing baselines | Không nêu | **NOT STARTED** |
| Existing experiments | Metric: sensitivity, specificity, false alarms/24 h, alarm latency ≤ 1.5 s | **NOT STARTED** |
| Phần cứng (MLX90640, IWR6843 / HLK-LD2410, ESP32-S3, Raspberry Pi) | Có | **EXCLUDED** dạng vật lý → mô phỏng + dataset thật cùng loại cảm biến |
| Venue trong file | IEEE RIVF 2027, IEEE EMBC, IEEE Sensors Journal | Sensors Journal: Q1 (SJR 2025). RIVF, EMBC: chưa xác minh hạng CORE — **NEEDS VERIFICATION** |
| Current progress | Danh mục 5 đề tài; sinh viên vừa chốt DT-02 | **NOT STARTED** |
| Năng lực sinh viên, GPU, quota | Không có | **TBD** |
| Lỗi tài liệu | Header PDF ghi "EE136IU • COURSE SPECIFICATION & SYLLABUS" (lỗi template) | Cần sửa |

### 2.2 Các mục trong checklist nhiệm vụ không thuộc DT-02

Checklist yêu cầu kiểm tra 3DGS, Semantic 3DGS, semantic scene representation, path planning, navigation, traversability/occupancy, collision avoidance. **Không mục nào có trong file đề tài.** Roadmap dùng khái niệm tương đương và không nhắc lại các mục gốc ở phần sau:

| Mục trong checklist | Trạng thái trong file | Khái niệm tương đương trong DT-02 |
|---|---|---|
| 3DGS / Semantic 3DGS | Không có | Không có tương đương. Gần nhất: mô hình người SMPL dùng trong mô phỏng |
| Semantic scene representation | Không có | Biểu diễn cảnh trong FallTwin: phòng, vị trí cảm biến, nguồn nhiệt, thú cưng |
| Path planning / Navigation | Không có | Không có tương đương |
| Traversability / Occupancy | Không có | Bản đồ chiếm chỗ của người trong ảnh nhiệt / point cloud radar (vị trí, độ cao) |
| Collision avoidance | Không có | Không có tương đương |
| T_semantic + T_3DGS + T_planning | — | $T_{\text{thermal}} + T_{\text{radar}} + T_{\text{fusion}} + T_{\text{decision}}$ và alarm latency (Mục 12) |

---

## 3. Research Problem & Gap

### 3.1 Problem formulation

Trong cửa sổ thời gian $[t-W, t]$, student nhận:
- chuỗi ảnh nhiệt $X^{th} = \{x^{th}_i \in \mathbb{R}^{24\times 32}\}$ tại các thời điểm $\{\tau^{th}_i\}$ (tần số thấp, vd. 2–8 Hz);
- chuỗi radar $X^{rd} = \{x^{rd}_j\}$ (point cloud $\{(x, y, z, v_D, \text{SNR})\}$ hoặc micro-Doppler) tại $\{\tau^{rd}_j\}$ (vd. 8–20 Hz), thời điểm hai luồng không trùng nhau;

và dự đoán:
1. $p(\text{fall} \mid X^{th}, X^{rd})$ cùng thời điểm báo động $\hat t_{alarm}$;
2. đại lượng vật lý $\hat\phi(t)$ = [độ cao trọng tâm $h$, vận tốc thẳng đứng $v_z$, gia tốc đỉnh $a_{peak}$, góc thân $\theta$, thời gian nằm sàn $T_{ground}$].

Khi huấn luyện có thêm thông tin đặc quyền (privileged): chuỗi pose 3D $P(t)$ (từ RGB thật hoặc ground-truth mô phỏng). Ràng buộc: không dùng $P$ hay RGB khi suy luận; mô hình nằm trong ngân sách edge-class; alarm latency $\hat t_{alarm} - t_{impact} \le 1.5$ s.

### 3.2 Gap (đã kiểm tra literature 10/2026)

| # | Gap | Bằng chứng |
|---|---|---|
| G1 | Không có dataset công khai có đủ RGB + thermal low-res + mmWave **đồng bộ** với cú ngã | Taramasco et al. 2025 có thermal 32×24 + IWR6843AOP + LiDAR + IMU nhưng **không có RGB**; MM-Fi có RGB + IWR6843 nhưng **không có ngã**; TaFall 2026 (thermal 80×62) không công bố dữ liệu |
| G2 | CMKD hiện chủ yếu là chưng cất logit/feature; chưa khai thác đại lượng vật lý của cú ngã như privileged information | RF-Pose 2018 chưng cất keypoint; TaFall 2026 dùng biểu diễn cân bằng (SMoB) từ mocap nhưng chỉ với thermal, không phải radar–thermal; **NEEDS VERIFICATION** bằng systematic search |
| G3 | Fusion thermal + radar cho fall detection hiếm, và chưa xử lý hai cảm biến **khác tần số** (Taramasco: radar 8.3 Hz, thermal 2.6 Hz) cùng việc một cảm biến bị nhiễu/hỏng | P2MFDS 2025 fusion radar + rung (không thermal); Taramasco 2025 là dataset, chưa thấy phương pháp fusion bất đồng bộ — **NEEDS VERIFICATION** |
| G4 | Confounder (nguồn nhiệt, thú cưng, ngồi bệt) được nêu như vấn đề nhưng chưa có benchmark có kiểm soát | DT-02 tự nêu; TaFall nêu giới hạn "single-sensor lacks environmental context" |
| G5 | Mô hình học trên mô phỏng thường mất độ chính xác khi chạy trên dữ liệu thật | RF-Genesis (SenSys 2023), HybridSim (arXiv 2026) đều xử lý sim-to-real cho radar; với thermal low-res chưa thấy simulator công khai — **NEEDS VERIFICATION** |

### 3.3 Điều DT-02 **không** claim
- Không claim hiệu năng trên người cao tuổi thật hay trong nhà thật.
- Không claim chạy trên ESP32-S3 / Raspberry Pi; chỉ claim edge-profiled.
- Không claim "bảo vệ riêng tư" theo nghĩa hình thức (formal privacy); chỉ claim không dùng ảnh nhận dạng khi suy luận. Nếu muốn claim mạnh hơn → thêm thí nghiệm re-identification (OPTIONAL, journal).

---

## 4. Research Questions & Objectives

| RQ | Research Question | Hypothesis | Algorithm / Model | Experiment | Metric | Expected Evidence | Paper Contribution |
|---|---|---|---|---|---|---|---|
| **RQ1** | Chưng cất đại lượng vật lý từ teacher pose có giúp student thermal + radar tốt hơn học từ nhãn, logit KD, feature KD không? | H1: physics KD tăng F1 ≥ 3 điểm và giảm false alarms/24 h ≥ 30% so với feature KD trên FallTwin | PhyKD-Fall vs KD baselines | E1, E3, E4 | F1, sensitivity, specificity, FA/24 h, AUROC | Bảng chính + ablation từng loss | **C2** (Conference) |
| **RQ2** | Fusion bất đồng bộ có cổng tin cậy có tốt hơn single-modality, early/late fusion, và có xuống cấp từ từ khi một cảm biến nhiễu, hỏng, hoặc gặp confounder không? | H2: PhyKD-Fall giữ sensitivity ≥ single-modality tốt nhất khi một cảm biến hỏng; FA/24 h dưới confounder giảm ≥ 30% so với late fusion | Async fusion + reliability gate | E2, E5 | F1, FA/24 h theo loại confounder, ΔF1 khi mất modality | Đường cong theo mức nhiễu/confounder | **C2, C3** (Conference) |
| **RQ3** | Mô hình học trên FallTwin có chạy được trên dữ liệu thermal + radar thật (Taramasco 2025) không, và physics KD có thu hẹp khoảng cách sim-to-real không? | H3: zero-shot sensitivity ≥ 85%; physics KD giảm khoảng cách sim-to-real (ΔF1 sim − real) so với feature KD; few-shot (1–3 người) vượt train-from-scratch trên real | FallTwin + PhyKD-Fall; fine-tune few-shot | E6 | Sensitivity, specificity, F1 (LOSO), ΔF1 sim–real | Bảng sim-to-real | **C1, C3** (Conference: zero-shot; Journal: đầy đủ) |
| **RQ4** | CMKD trên dữ liệu RGB + radar **thật** (MM-Fi) có cải thiện nhánh radar so với chỉ học từ mô phỏng không, và có tổng quát sang radar khác (Glasgow, 5.8 GHz)? | H4: pretrain bằng CMKD thật trên MM-Fi + FallTwin cho F1 trên Taramasco cao hơn chỉ FallTwin | Real CMKD pretraining | E8, E9 | F1 trên Taramasco; accuracy trên Glasgow | Có/không chuyển giao, CI 95% | **C4** (Journal) |
| **RQ5** | Có thể nén student xuống ngân sách MCU/edge (proxy) mà vẫn đạt alarm latency ≤ 1.5 s và mất ≤ 1 điểm F1 không? | H5: INT8 + pruning giữ ΔF1 ≤ 1, latency proxy đạt | Quantization, pruning, distillation nhỏ hơn | E10 | Params, MACs, peak RAM, latency CPU 1 luồng, ΔF1, alarm latency | Pareto accuracy–cost | **C5** (Journal) |

**Objectives (đo được):**
- O1. FallTwin v1: ≥ 3 nguồn chuyển động, ≥ 8 loại ngã, ≥ 10 loại ADL, ≥ 5 loại confounder; thống kê khớp dữ liệu thật trong khoảng định trước — Tháng 3.
- O2. Teacher pose + 7 baseline student/KD trên cùng pipeline — Tháng 3.
- O3. PhyKD-Fall v2 đạt/không đạt H1–H2 có bằng chứng thống kê — Tháng 5.
- O4. Zero-shot trên Taramasco (LOSO 10 người) — Tháng 5.
- O5. Conference paper sẵn sàng nộp — cuối Sprint 13 (04/04/2027).
- O6. Journal Q1 sẵn sàng nộp — cuối Sprint 26 (03/10/2027).

---

## 5. Novelty Analysis

### 5.1 Existing methods (kiểm tra 10/2026)

| Công trình | Cảm biến | Dữ liệu | Phương pháp | Liên quan DT-02 |
|---|---|---|---|---|
| Zhao et al., CVPR 2018 — RF-Pose | RF (FMCW) | Thu riêng | Teacher thị giác → student RF, chưng cất keypoint | Nền của CMKD RGB → radar; đã cũ |
| Jin et al. — mmFall (2020) | IWR/AWR mmWave point cloud | Thu riêng | HVRAE, phát hiện ngã như bất thường + độ cao trọng tâm | Baseline radar-only; dùng độ cao trọng tâm như đặc trưng (gần ý physics) |
| Taramasco et al., *PeerJ* 2025 | MLX90640 32×24 + IWR6843AOP + LiDAR 8×8 + IMU | 10 người, 100 cú ngã, CC-BY, OSF | Dataset | **Dữ liệu thật đúng cảm biến DT-02**; tần số radar 8.3 Hz, thermal 2.6 Hz |
| Yang et al., NeurIPS 2023 — MM-Fi | RGB-D, IWR6843, LiDAR, WiFi | 40 người, 27 hành động, > 320k khung; không có ngã | Dataset + baseline | Dữ liệu thật RGB ↔ radar cho CMKD |
| Li et al., arXiv 2026 — TaFall | Thermal 80×62 | 35 người, 3,005 cú ngã; không công bố | Pose 2.5D từ thermal + biểu diễn cân bằng + pretraining | Gần nhất về ý "vật lý/cân bằng"; chỉ thermal, độ phân giải cao hơn 32×24 |
| Wang et al., arXiv 2025 — P2MFDS | mmWave + rung | Chưa công bố | Dual-stream CNN–BiLSTM | Fusion đa cảm biến riêng tư; không thermal, không KD |
| Chen et al., SenSys 2023 — RF-Genesis | mmWave mô phỏng | Mô phỏng + diffusion | Ray tracing + diffusion sinh dữ liệu | Công cụ mô phỏng radar có code |
| Xiong et al., arXiv 2026 — HybridSim | mmWave mô phỏng | mmMesh | Digital twin physics–learning | Tham chiếu sim-to-real radar |
| Alamgeer et al., 2025 — AI-generated fall data | IMU (wearable) | Text-to-motion (T2M-GPT, SATO, ParCo) | Sinh chuyển động ngã | Nguồn chuyển động ngã tổng hợp; kết quả "không luôn cải thiện" |

### 5.2 Research gap còn mở
G1–G5. Với ràng buộc simulation-only, đóng góp chắc chắn nằm ở G2, G3, G4 và đo G5 trên dữ liệu thật.

### 5.3 Proposed contribution → gap

| Contribution | Gap | Loại novelty |
|---|---|---|
| C1. FallTwin: mô phỏng đồng thời pose + thermal 32×24 + radar IWR6843 với confounder có kiểm soát và luồng ADL 24 h | G1, G4, G5 | New simulation/evaluation methodology |
| C2. Physics-descriptor distillation: teacher pose truyền đại lượng vật lý φ(t) cho student | G2 | New loss + privileged-information learning |
| C3. Fusion bất đồng bộ có cổng tin cậy cho thermal + radar | G3, G4 | New learning architecture, uncertainty-aware fusion |
| C4. CMKD thật trên MM-Fi + kiểm chứng Taramasco/Glasgow | G1, G5 | New real-world evaluation dimension (Journal) |
| C5. Nén cho edge với alarm latency ≤ 1.5 s | Ràng buộc edge | Computational efficiency (Journal) |

### 5.4 Core novelty — cái gì mới, cái gì không

**Không claim là mới:** CMKD từ thị giác sang RF; logit/feature KD; PointNet; micro-Doppler CNN; ST-GCN; modality dropout; quantization.

**Có khả năng mới (xác minh ở Sprint 1):**
1. **Chưng cất đại lượng vật lý có thể diễn giải** (độ cao trọng tâm, vận tốc rơi, góc thân, thời gian nằm sàn) từ teacher pose sang hai cảm biến riêng tư, như một dạng privileged information — student phải "đo" được cú ngã, không chỉ phân loại.
2. **Fusion bất đồng bộ** cho hai luồng khác tần số, không cần nội suy về cùng clock, kèm cổng tin cậy theo modality và tình huống confounder.
3. **Benchmark confounder có kiểm soát** (thermal: nguồn nhiệt, thú cưng, luồng khí; radar: ngồi bệt, nằm ngủ, cúi nhặt đồ) + false alarms/24 h trên luồng ADL mô phỏng.

### 5.5 Novelty verification protocol (Sprint 1–2)
- Nguồn: Scopus, Web of Science, Google Scholar, arXiv, IEEE Xplore, ACM DL; 2018–2026.
- Truy vấn:
  - `("fall detection") AND (thermal OR infrared) AND (radar OR mmWave) AND (fusion OR multimodal)`
  - `("knowledge distillation" OR "cross-modal") AND (radar OR mmWave OR thermal) AND (fall OR "activity recognition" OR pose)`
  - `("privileged information" OR "physics-informed") AND (fall OR "human activity") AND (distillation OR teacher)`
  - `(simulation OR synthetic) AND (thermal OR mmWave) AND (fall OR "human motion") AND (SMPL OR "motion capture")`
- Đầu ra: bảng ≥ 40 bài (cảm biến, dữ liệu, có ngã không, KD loại gì, fusion, sim-to-real, code).
- **Pivot:** nếu đã có bài làm physics KD cho thermal + radar → trọng tâm chuyển sang C1 (FallTwin + benchmark confounder) + C3 + C4.

---

## 6. Feasibility Assessment

| Dimension | Đánh giá | Evidence | Risk | Mitigation |
|---|---|---|---|---|
| Research Gap | 🟢 | G1 xác nhận bằng nội dung dataset Taramasco, MM-Fi, TaFall; DT-02 nêu đúng vấn đề confounder | Bài mới trong năm | Alert hằng tháng; nộp sớm |
| Novelty | 🟡 | CMKD chung đã có (RF-Pose 2018); physics KD + async fusion thermal–radar chưa thấy | Search chưa hệ thống; TaFall gần ý "vật lý" | Protocol 5.5; pivot rule |
| Algorithmic feasibility | 🟢 | φ(t) tính đóng từ pose; KD loss chuẩn; fusion bất đồng bộ cài bằng attention có mã hoá thời gian | Căn chỉnh thời gian teacher–student | Gán φ theo timestamp; nội suy teacher (không nội suy student) |
| Model feasibility | 🟢 | Student nhỏ (32×24 và ≤ vài trăm điểm radar/khung); teacher ST-GCN trên skeleton | Overfit dữ liệu thật nhỏ | Pretrain trên FallTwin; LOSO; augmentation |
| Dataset | 🟡 | Taramasco (thermal + radar thật, ngã), MM-Fi (RGB + radar thật), NTU RGB+D 120 / UR Fall (pose có ngã) | Taramasco nhỏ (100 cú ngã) → CI rộng; license NTU cần đăng ký | Bootstrap CI; LOSO; báo cáo đúng kích thước mẫu |
| Simulation | 🟡 | RF-Genesis có code; render thermal từ SMPL là phép chiếu + mô hình nhiệt đơn giản | Mô phỏng thiếu thực tế → sim-to-real kém | Hiệu chỉnh thống kê với dữ liệu thật (S5–S6); domain randomization; fallback radar proxy hình học |
| Computational | 🟡 | Student và teacher nhỏ; tốn nhất là render radar | Ray tracing radar tốn GPU | Pilot S2; cache; radar proxy hình học nếu quá chậm |
| Baseline | 🟢 | mmFall có code (radar-lab/mmfall); KD baselines chuẩn | Một số bài không có code | Tái hiện theo mô tả, ghi chú |
| Real-time | 🟢 (proxy) | Input rất nhỏ; mục tiêu 1.5 s là ở mức giây | Cửa sổ thời gian dài làm trễ báo động | Đo alarm latency trực tiếp; sliding window ngắn |
| Experimental | 🟢 | 12 experiment, mỗi cái gắn một RQ (Mục 14) | Nhiều cấu hình confounder | Thiết kế factorial rút gọn |
| Conference ≤ 6M | 🟡 | RQ1 + RQ2 (mô phỏng) + RQ3 zero-shot (thật) đủ 6–8 trang | FallTwin trễ → mọi thứ trễ | FallTwin là critical path; fallback radar proxy |
| Journal ≤ 12M | 🟡 | C4, C5 + RQ3 đầy đủ | RQ4 phụ thuộc MM-Fi xử lý được | Plan B: bỏ Glasgow, giữ MM-Fi + Taramasco |

So với DT-02 nguyên bản (cần mua MLX90640, IWR6843, ESP32-S3 và thu dữ liệu diễn ngã): dưới ràng buộc simulation-only là **🔴** ở Dataset và Experimental. Các chuyển đổi ở Mục 0 đưa đề tài về 🟡.

---

## 7. Proposed Algorithm

### 7.0 Pipeline tổng thể

```
Nguồn chuyển động (SMPL):                     Dataset thật
 Mixamo · AMASS/HumanML3D · text-to-motion      NTU RGB+D 120 / UR Fall (pose có ngã) → Teacher
 + kịch bản ngã / ADL / confounder              MM-Fi (RGB + IWR6843, không ngã) → CMKD thật (Journal)
            │                                   Taramasco 2025 (MLX90640 + IWR6843AOP, ngã) → Test sim-to-real
            ▼
   FallTwin simulator (phòng, vị trí cảm biến, confounder, luồng ADL 24 h)
     ├─ Pose 3D ground-truth P(t)              ── privileged, chỉ khi train
     ├─ Thermal renderer → x^th (24×32, 2–8 Hz, nhiễu, nguồn nhiệt, thú cưng)
     └─ Radar simulator  → x^rd (point cloud / micro-Doppler, 8–20 Hz, IWR6843 config)
            │
   ┌────────┴──────────────────────────────────────────────┐
   ▼                                                       ▼
 TEACHER (train only)                               STUDENT (train + inference)
 Pose encoder E_T (ST-GCN / Transformer)            Thermal encoder E_th (tiny CNN + temporal conv)
 → logits z_T, feature f_T                          Radar encoder  E_rd (PointNet-lite hoặc μD-CNN)
 Physics extractor → φ(t): h, v_z, a_peak, θ, T_gr  Async fusion (time-encoded cross-attention)
            │                                       Reliability gate g_th, g_rd
            │                                       → z_S, f_S, φ̂(t), p(fall), t_alarm
            └──────── KD losses: logit · feature · physics · temporal relation ───────┘
                                       │
          Đánh giá: sensitivity, specificity, F1, FA/24 h, alarm latency, sim-to-real gap, edge proxy
```

### 7.1 Algorithm A — FallTwin: mô phỏng đồng thời pose, thermal và radar

**Chuyển động.** Chuỗi SMPL $\{(\beta, \theta_t, \mathbf{t}_t)\}$ từ: (1) Mixamo animation (có các kiểu ngã), (2) AMASS/HumanML3D lọc theo mô tả text ("falls", "lies down", "sits on the floor"…), (3) text-to-motion (T2M-GPT hoặc tương đương) cho các kiểu ngã thiếu. Mỗi chuỗi gán nhãn: fall (8 kiểu: trước, sau, ngang trái/phải, trượt, ngất, từ ghế, từ giường), ADL (≥ 10: đi, ngồi ghế, ngồi bệt, nằm ngủ, cúi nhặt, đứng lên, quỳ, tập thể dục…), và $t_{impact}$.

**Cảnh.** Phòng hình hộp (kích thước ngẫu nhiên trong khoảng phòng ngủ/nhà tắm), cảm biến gắn trần hoặc tường (độ cao, góc nghiêng ngẫu nhiên trong khoảng), radar và thermal cùng vị trí (như DT-02) hoặc lệch nhau.

**Thermal renderer (MLX90640-like).** Với mỗi khung tại $\tau^{th}_i$:

$$
x^{th}(u) = \sum_{k} A_k(u)\, T_k + \Big(1 - \sum_k A_k(u)\Big) T_{bg}(u) + \epsilon(u), \quad \epsilon \sim \mathcal{N}(0, \sigma_{NETD}^2)
$$

$A_k(u)$: tỉ lệ diện tích pixel $u$ bị phủ bởi vùng cơ thể/vật thể $k$ (tính bằng rasterize mesh SMPL ở độ phân giải cao rồi average-pool về 24×32 theo FOV cảm biến); $T_k$: nhiệt độ bề mặt vùng $k$ (da, quần áo — tham số ngẫu nhiên trong khoảng giả định); $T_{bg}$: nền + gradient; $\sigma_{NETD}$ và FOV lấy từ datasheet MLX90640 (**TBD**, Sprint 3). Confounder: nguồn nhiệt cố định (ấm đun, máy sưởi, laptop), luồng khí nóng (blob thay đổi theo thời gian), thú cưng (blob nhỏ di chuyển), nắng chiếu (vùng nhiệt rộng).

**Radar simulator (IWR6843-like).** Hai mức:
- *Mức 1 (chính, nếu đủ nhanh):* RF-Genesis (code công khai) hoặc mô hình point-scatterer: lấy mẫu điểm trên bề mặt mesh nhìn thấy từ radar, RCS theo góc tới, tín hiệu IF FMCW $s(t) = \sum_n a_n \exp\big(j 2\pi (f_b^{(n)} t + f_D^{(n)} \cdot \text{chirp})\big)$ → Range-FFT, Doppler-FFT, Angle-FFT → CFAR → point cloud $(x,y,z,v_D,\text{SNR})$; micro-Doppler bằng STFT trên range bin của người.
- *Mức 2 (fallback):* radar proxy hình học — lấy mẫu điểm nhìn thấy, $v_D$ từ vận tốc đỉnh mesh chiếu lên hướng radar, nhiễu vị trí/vận tốc, dropout theo SNR, số điểm/khung theo phân bố đo được trên dữ liệu thật.

Cấu hình chirp (băng thông, số chirp, tần số khung) lấy theo cấu hình của Taramasco/MM-Fi để khớp dữ liệu thật (**TBD**, Sprint 3).

**Luồng ADL 24 h:** ghép các đoạn ADL theo lịch sinh hoạt giả định (ngủ, đi lại, ngồi, tắm) + chèn confounder, không có ngã → đo false alarms/24 h.

**Hiệu chỉnh với dữ liệu thật (Sprint 5–6):** so sánh phân bố (số điểm/khung, $v_D$, độ cao điểm; nhiệt độ pixel người/nền, kích thước blob) giữa FallTwin và Taramasco/MM-Fi; chỉnh tham số đến khi khoảng cách (vd. Wasserstein-1 hoặc KS) nằm dưới ngưỡng định trước. Domain randomization trên mọi tham số còn bất định.

```
Input : motion clip M (SMPL), scene params S, sensor configs C_th, C_rd, confounder set K
Output: {P(t), x^th_i @τ^th_i, x^rd_j @τ^rd_j, y, t_impact, φ(t)}
1  Sample S, sensor poses, timestamps τ^th (rate r_th ± jitter), τ^rd (rate r_rd ± jitter)
2  for each τ in τ^th: render mesh → A_k → x^th (+confounders K_th, noise)
3  for each τ in τ^rd: radar sim (level 1 or 2) on mesh (+multipath/noise, K_rd) → x^rd
4  P(t) ← SMPL joints; φ(t) ← PhysicsExtractor(P)
5  Randomly drop/corrupt modalities per config (sensor fault, occlusion, packet loss)
```

### 7.2 Algorithm B — Physics extractor (teacher side)

Từ pose 3D $P(t)$ (khớp SMPL hoặc keypoint 3D):
- trọng tâm $c(t)$ = trung bình có trọng số khối lượng các đoạn cơ thể; $h(t) = c_z(t)$;
- $v_z(t) = \dot h(t)$, $a_{peak}$ = max $|\ddot h|$ trong cửa sổ (đạo hàm số có làm trơn Savitzky–Golay);
- $\theta(t)$ = góc giữa vector hông → cổ và trục thẳng đứng;
- $T_{ground}(t)$ = thời gian liên tục $h(t) < h_{thr}$.

Các đại lượng này dùng được cho cả dữ liệu thật có pose (NTU, UR Fall, MM-Fi) và mô phỏng.

### 7.3 Algorithm C — Huấn luyện PhyKD-Fall

```
Stage 1  Teacher: train E_T trên pose có ngã (NTU RGB+D 120 falling + UR Fall + FallTwin pose), CE
Stage 2  Student pretrain (tùy chọn, Journal): CMKD thật trên MM-Fi — radar features ← teacher pose features
Stage 3  Distillation trên FallTwin, mỗi minibatch (X^th, X^rd, P, y, φ):
   z_T, f_T ← E_T(P) (đóng băng);  φ ← Physics(P)
   h_th ← E_th(X^th);  h_rd ← E_rd(X^rd)
   u ← AsyncFusion(h_th @τ^th, h_rd @τ^rd)        # cross-attention với time encoding γ(τ)
   g ← ReliabilityGate(u, stats(X^th), stats(X^rd))
   z_S, f_S, φ̂ ← Heads(u, g)
   L = CE(z_S, y)
     + λ_KD · τ² · KL(softmax(z_T/τ) ‖ softmax(z_S/τ))          # logit KD
     + λ_F  · ‖W f_S − f_T‖²                                     # feature KD
     + λ_φ  · Σ_t w(t) · SmoothL1(φ̂(t), φ(t))                   # physics KD (privileged)
     + λ_R  · L_rel(f_S, f_T)                                     # temporal relation KD
   Modality dropout p_md: bỏ toàn bộ X^th hoặc X^rd; corruption theo cấu hình
Stage 4  Few-shot adaptation trên dữ liệu thật (chỉ cho RQ3 few-shot; LOSO)
Stage 5  Calibration (temperature scaling), chọn ngưỡng báo động theo FA/24 h mục tiêu trên val
Stage 6  Compression (Journal): pruning + INT8 PTQ/QAT + distill sang student nhỏ hơn
```

$w(t)$ tăng trọng số quanh $t_{impact}$ (nơi φ thay đổi nhanh). $L_{rel}$: khớp ma trận tương đồng giữa các bước thời gian của $f_S$ và $f_T$.

**Inference và báo động:** cửa sổ trượt $W$ (vd. 2–4 s, quét ở E5), bước trượt bằng chu kỳ radar. Báo động khi $p(\text{fall}) > \tau_{alarm}$ **và** $\hat T_{ground}$ > ngưỡng (logic hai điều kiện giống tinh thần mmFall) — kiểm tra bằng ablation. Không lưu ảnh nhiệt/radar thô; chỉ xuất sự kiện (phù hợp "zero-storage" của DT-02).

### 7.4 Async fusion và reliability gate

Token nhiệt $\{h^{th}_i + \gamma(\tau^{th}_i)\}$ và token radar $\{h^{rd}_j + \gamma(\tau^{rd}_j)\}$ với $\gamma$ là mã hoá thời gian liên tục (sinusoidal theo giây). Cross-attention hai chiều + pooling → $u$. Cổng $g = \sigma(\text{MLP}([\text{entropy}(z_{th}), \text{entropy}(z_{rd}), q_{th}, q_{rd}]))$, với $q$ = chỉ số chất lượng (số điểm radar/khung, tỉ lệ khung thiếu, độ tương phản blob nhiệt). Đầu ra cuối: $z_S = g_{th} z_{th} + g_{rd} z_{rd} + z_{u}$ (ablation so với chỉ $z_u$).

---

## 8. Proposed Model Architecture — PhyKD-Fall

### M1 — Teacher pose encoder (train only)

| Thuộc tính | Nội dung |
|---|---|
| Input | Chuỗi keypoint 3D $P \in \mathbb{R}^{T\times J\times 3}$ (J = 17–24) |
| Output | $z_T$ (fall/ADL, có thể nhiều lớp hoạt động), $f_T \in \mathbb{R}^{D}$ theo thời gian |
| Architecture | ST-GCN nhỏ hoặc Transformer 4 lớp; so sánh ở S4 |
| Loss | CE (+ label smoothing) |
| Training | NTU RGB+D 120 (skeleton, lớp falling vs khác) + UR Fall (pose từ RGB bằng pose estimator) + FallTwin pose |
| Note | Đây là "teacher RGB" của DT-02 ở dạng pose: pose estimator (MediaPipe / YOLOv8-Pose) chạy trên RGB thật khi dataset chỉ có RGB |

### M2 — Physics extractor

| Thuộc tính | Nội dung |
|---|---|
| Input | $P(t)$ |
| Output | $\phi(t) = [h, v_z, a_{peak}, \theta, T_{ground}]$ |
| Algorithm | Mục 7.2; không có tham số học |
| Complexity | $O(T\cdot J)$ |

### M3 — Thermal encoder (student)

| Thuộc tính | Nội dung |
|---|---|
| Input | Chuỗi $24\times 32$ (chuẩn hoá theo nền), timestamps |
| Output | Token $h^{th}_i$ |
| Architecture | CNN 3–4 lớp (16–32 kênh) mỗi khung + temporal conv 1D; tùy chọn kênh chênh lệch khung (motion) |
| Complexity | Rất nhỏ; đo params/MACs ở S2 |

### M4 — Radar encoder (student)

| Thuộc tính | Nội dung |
|---|---|
| Input | Point cloud ≤ 64–128 điểm/khung $(x,y,z,v_D,\text{SNR})$ **hoặc** micro-Doppler spectrogram |
| Output | Token $h^{rd}_j$ |
| Architecture | PointNet-lite (shared MLP 64–128 + max-pool) hoặc CNN 2D nhỏ cho μD; chọn ở S5 theo kết quả trên dữ liệu thật |
| Complexity | Nhỏ |

### M5 — Async fusion + reliability gate

| Thuộc tính | Nội dung |
|---|---|
| Input | Token hai modality + timestamps + chỉ số chất lượng |
| Output | $u$, $g_{th}, g_{rd}$ |
| Architecture | 1–2 lớp cross-attention (4 head, dim 64) + MLP gate |
| Baselines thay thế | Early fusion (nội suy về cùng clock), late fusion (trung bình xác suất), concat |

### M6 — Heads

| Thuộc tính | Nội dung |
|---|---|
| Output | $z_S$ (fall/ADL), $f_S$ (để KD), $\hat\phi(t)$ |
| Loss | Mục 7.3 |

### M7 — Compression (Journal)

Pruning có cấu trúc + INT8 (ONNX Runtime PTQ; QAT nếu mất > 1 điểm) + distill sang student nhỏ hơn. Báo cáo params, MACs, peak RAM, latency CPU 1 luồng (proxy MCU), alarm latency.

---

## 9. Dataset & Simulation Strategy

### 9.1 Dữ liệu

| Dữ liệu | Vai trò | Đã xác minh | Cần xác minh (Sprint 1–2) |
|---|---|---|---|
| **Taramasco et al. 2025** (*PeerJ*, OSF DOI 10.17605/OSF.IO/YJGDV) | Test sim-to-real (RQ3); few-shot | MLX90640 32×24 (≈2.6 Hz) + IWR6843AOP (≈8.3 Hz) + LiDAR 8×8 + IMU; 10 người; 10 kiểu ngã, 100 cú ngã; CC-BY | Định dạng file, đồng bộ thời gian, có ADL ngoài đi bộ không, nhãn thời điểm ngã |
| **MM-Fi** (Yang et al., NeurIPS 2023) | CMKD thật RGB-pose → radar (Journal); hiệu chỉnh radar sim | RealSense D435 + IWR6843 + LiDAR + WiFi; 40 người; 27 hành động; > 320k khung; keypoint 2D/3D | License; định dạng point cloud; tần số khung |
| **NTU RGB+D 120** (Liu et al., TPAMI 2020) | Teacher: skeleton có lớp *falling* | Bộ dữ liệu phổ biến, có lớp ngã | Thủ tục đăng ký tải; license nghiên cứu |
| **UR Fall Detection** (Kwolek & Kepski 2014) | Teacher: RGB/depth có ngã → pose bằng pose estimator | Bộ dữ liệu phổ biến | Link tải, license |
| **Glasgow "Radar signatures of human activities"** (Fioranelli et al., 2019) | Test chéo cảm biến radar (Journal, OPTIONAL) | Có trong literature; FMCW, có hoạt động ngã | Tần số radar, số bản ghi, link tải, license |
| **Low-resolution thermal dataset** (BuildSys'21, Zenodo, CC-BY) | Thống kê nền/vật nóng 32×24 cho hiệu chỉnh thermal sim | 32×24, 1,770 ảnh có nhãn, CC-BY-4.0 | Có thực sự cùng loại cảm biến không |
| Mixamo, AMASS / HumanML3D | Nguồn chuyển động cho FallTwin | Mixamo đã được dùng tạo dataset ngã tổng hợp (Zenodo 2026); HumanML3D gồm 13,308 chuỗi từ AMASS | Số chuỗi có ngã; license dùng cho nghiên cứu |
| RF-Genesis (code GitHub) | Radar simulator mức 1 | Code công khai (SenSys'23) | Chạy được trên GPU trường; tốc độ |

### 9.2 Chia tập

| Tập | Nguồn | Mục đích |
|---|---|---|
| Development | FallTwin (subject/motion clip nhóm A, cảnh nhóm A) + NTU/UR Fall (teacher) | Train teacher, student |
| Validation | FallTwin nhóm B (clip, cảnh, cấu hình cảm biến khác) | Siêu tham số, ngưỡng báo động |
| Test (sim) | FallTwin nhóm C + luồng ADL 24 h | RQ1, RQ2 |
| Test (sim, confounder) | FallTwin C với từng confounder riêng | RQ2 |
| Test (real) | Taramasco, LOSO 10 người | RQ3 |
| Few-shot (real) | Taramasco: k = 1, 2, 3 người dùng để adapt, còn lại test | RQ3 |
| Real CMKD | MM-Fi theo split chính thức | RQ4 |
| Cross-sensor | Glasgow | RQ4 (OPTIONAL) |

**Chống leakage:** không trùng clip chuyển động (và các biến thể của cùng clip) giữa train/test; split theo người cho dữ liệu thật; không dùng dữ liệu Taramasco để chọn siêu tham số của zero-shot.

### 9.3 Ground truth trong mô phỏng

| Ground truth | Nguồn |
|---|---|
| Nhãn ngã/ADL, $t_{impact}$ | Kịch bản chuyển động |
| Pose 3D, φ(t) | SMPL |
| Vị trí, loại confounder | Cấu hình cảnh |
| Lỗi cảm biến (hỏng, mất khung) | Cấu hình FallTwin |

---

## 10. Baseline Strategy

| ID | Method | Paper | Code | Độ phức tạp | Metric | Hạn chế dự kiến | Vai trò |
|---|---|---|---|---|---|---|---|
| B0 | Teacher pose (upper bound, dùng thông tin đặc quyền) | ST-GCN-style | Tự cài / pyskl | Thấp | F1 | Không riêng tư | Trần tham chiếu |
| B1 | Thermal-only student (không KD) | — | Tự cài | Thấp | F1, FA/24 h | Nhầm nguồn nhiệt | Single-modality |
| B2 | Radar-only student (không KD) | — | Tự cài | Thấp | F1, FA/24 h | Nhầm ngồi bệt | Single-modality |
| B3 | mmFall (HVRAE, anomaly + độ cao trọng tâm) | Jin et al. 2020 | github.com/radar-lab/mmfall | Trung bình | F1 | Chỉ radar | Baseline radar đã công bố |
| B4 | Late fusion thermal + radar (trung bình xác suất) | — | Tự cài | Thấp | F1, FA/24 h | Không xử lý bất đồng bộ | Fusion đơn giản |
| B5 | Early fusion (nội suy cùng clock + concat) | — | Tự cài | Thấp | F1 | Sai lệch do nội suy | Fusion phổ biến |
| B6 | Logit KD (Hinton et al. 2015) | — | Tự cài | Thấp | F1 | Chỉ chuyển "dark knowledge" | KD chuẩn |
| B7 | Feature KD (FitNets-style) / RF-Pose-style | Romero et al. 2015; Zhao et al. 2018 | Tự cài | Trung bình | F1 | Không ràng buộc vật lý | CMKD chuẩn |
| B8 | Contrastive Representation Distillation (CRD) | Tian et al., ICLR 2020 | Code công khai (cần xác minh) | Trung bình | F1 | — | KD mạnh hơn |
| B9 | ModDrop cho B4/B5 | Neverova et al. | Tự cài | Thấp | ΔF1 khi mất modality | Không có cổng tin cậy | Robustness baseline |

**Backup:** B3 không chạy được trên định dạng dữ liệu của ta → dùng phiên bản đơn giản (anomaly + centroid height) tự cài, ghi rõ. B8 không có code dùng được → bỏ, giữ B6, B7.

---

## 11. Computational Plan

Số liệu là **ước lượng lập kế hoạch**, thay bằng số đo ở Sprint 2.

| Hạng mục | VRAM (ước lượng) | Thời gian (ước lượng) | Số lần | GPU-h |
|---|---|---|---|---|
| Render FallTwin thermal (rasterize SMPL) | < 4 GB | ~0.05–0.2 s/khung | ~1–2 triệu khung | ~40 |
| Radar sim mức 1 (RF-Genesis) | 6–12 GB | **TBD** — đo ở pilot | ~1 triệu khung | ~100–200 (nếu quá chậm → mức 2, ~20) |
| Teacher (ST-GCN trên NTU skeleton + FallTwin) | 4–6 GB | 2–4 h | 3 seed × 2 kiến trúc | ~20 |
| Student + KD (FallTwin) | 2–4 GB | 0.5–1.5 h | ~10 phương pháp × 5 seed × 3 cấu hình | ~120 |
| Robustness/confounder sweep | 2–4 GB | 10–20 phút | ~300 | ~70 |
| Zero/few-shot trên Taramasco | < 2 GB | phút | ~200 | ~10 |
| Overhead (+~20%) | | | | ~70 |
| **Conference (Tháng 1–6)** | | | | **~350–450** |
| Journal: MM-Fi CMKD, Glasgow, compression, sensitivity, mở rộng FallTwin | | | | +300–400 |
| **Tổng 12 tháng** | | | | **~650–850** |

**Pilot benchmark (Sprint 2, bắt buộc):**
```
5 clip chuyển động (2 ngã, 3 ADL) × 1 cảnh
   ↓ render thermal 24×32 và radar (thử cả RF-Genesis và proxy hình học)
   ↓ đo: thời gian/khung, VRAM, dung lượng lưu trữ
   ↓ train student thermal + radar 5 epoch trên dữ liệu pilot; đo s/epoch, VRAM
   ↓ đo latency student batch-1: GPU, CPU 1 và 4 luồng (ONNX Runtime)
   ↓ ngoại suy; chọn mức radar sim; chốt quy mô FallTwin
```

---

## 12. Real-time Simulation Plan (edge-profiled)

DT-02 yêu cầu báo động ≤ 1.5 s sau khi chạm đất. Đo trên dòng thời gian mô phỏng (và trên Taramasco nếu có nhãn thời điểm):

$$
T_{alarm} = \underbrace{(t_{decide} - t_{impact})}_{\text{phụ thuộc cửa sổ } W \text{ và logic}} + T_{thermal} + T_{radar} + T_{fusion} + T_{decision}
$$

| Thành phần | Mục tiêu (giả định) | Cách đo |
|---|---|---|
| $t_{decide} - t_{impact}$ | ≤ 1.2 s | Mô phỏng streaming, sliding window |
| $T_{thermal} + T_{radar} + T_{fusion}$ | ≤ 50 ms CPU 1 luồng (proxy MCU-class) | ONNX Runtime `intra_op_num_threads=1`, 1,000 lần |
| Ngân sách mô hình | ≤ 300k params, ≤ 50 MMACs/quyết định, peak RAM ≤ 512 KB INT8 (giả định gần ESP32-S3 — chỉ để định hướng, **không claim**) | fvcore + đếm tensor |
| **Alarm latency tổng** | **≤ 1.5 s** (DT-02) | Trung vị, P95 |
| Báo cáo kèm | GPU latency, throughput | `eval/latency.py` |

**Real-time gate cuối Tháng 3 (Sprint 6).** Không đạt → giảm $W$, giảm kênh, INT8, bỏ cross-attention thay bằng gated late fusion, cache token theo modality.

---

## 13. Evaluation Framework

| Nhóm | Metric | RQ |
|---|---|---|
| Phát hiện ngã | Sensitivity (recall), specificity, precision, F1, AUROC | RQ1–RQ4 |
| Báo động giả | False alarms / 24 h trên luồng ADL mô phỏng; FA theo loại confounder | RQ1, RQ2 |
| Độ trễ | Alarm latency (trung vị, P95), % cú ngã báo động ≤ 1.5 s | RQ1, RQ5 |
| Robustness | ΔF1 khi mất 1 modality, khi nhiễu tăng, khi lệch thời gian | RQ2 |
| Sim-to-real | F1 real (LOSO), ΔF1 sim − real, đường cong few-shot | RQ3, RQ4 |
| Chất lượng physics | MAE của $\hat h$, $\hat v_z$, $\hat\theta$, $\hat T_{ground}$ so với φ teacher | RQ1 |
| Edge-profiled | Params, MACs, peak RAM, latency CPU 1 luồng, ΔF1 sau INT8 | RQ5 |
| Riêng tư (OPTIONAL) | Re-identification accuracy từ embedding student | Journal |

Metric 3DGS / planning trong checklist: **không dùng**.

**Thống kê:** 5 seed cho mô phỏng; LOSO 10 fold cho Taramasco (báo cáo trung bình ± SD theo người); CI 95% bootstrap theo người; Wilcoxon signed-rank theo cặp; hiệu chỉnh Holm. Do Taramasco chỉ có 100 cú ngã, mọi kết luận trên dữ liệu thật phải kèm CI và cảnh báo kích thước mẫu.

---

## 14. Experiment Matrix

| ID | Experiment | RQ | Biến độc lập | Cố định | Metric | Paper | Sprint |
|---|---|---|---|---|---|---|---|
| E0 | Pilot compute + mức radar sim | — | Simulator mức 1 vs 2 | 5 clip | Thời gian, VRAM | — | S2 |
| E1 | Baseline student & KD | RQ1 | B1–B9 | FallTwin sạch | F1, FA/24 h, latency | Conf | S7 |
| E2 | Robustness & confounder của baseline | RQ2 | Loại/mức confounder; mất modality; lệch thời gian | B4, B5, B9 | ΔF1, FA/24 h | Conf | S8 |
| E3 | PhyKD-Fall vs tất cả | RQ1, RQ2 | Method | FallTwin + confounder | F1, FA/24 h, latency, physics MAE | Conf | S10 |
| E4 | Ablation | RQ1, RQ2 | − physics KD, − feature KD, − logit KD, − relation KD, − async (thay early fusion), − gate, − modality dropout, − logic hai điều kiện | | F1, FA/24 h | Conf | S11 |
| E5 | Sensitivity | RQ1, RQ5 | λ_φ, τ, $W$, tần số thermal (2/4/8 Hz), tần số radar | | F1, latency | Conf (rút gọn) / Journal | S12, S16 |
| E6 | Sim-to-real zero-shot & few-shot (Taramasco) | RQ3 | Method; k = 0/1/2/3 người | LOSO | Sensitivity, specificity, F1, ΔF1 | Conf (zero-shot) / Journal (đầy đủ) | S9–S12, S17 |
| E7 | Realism ablation của FallTwin | RQ3 | Bỏ domain randomization; bỏ hiệu chỉnh thống kê; radar mức 1 vs 2 | | F1 real | Journal | S18 |
| E8 | CMKD thật trên MM-Fi | RQ4 | Có/không pretrain MM-Fi | | F1 Taramasco; pose-feature MAE | Journal | S15–S19 |
| E9 | Cross-sensor radar (Glasgow) | RQ4 | — | | Accuracy, F1 | Journal (OPTIONAL) | S19 |
| E10 | Compression | RQ5 | FP32/INT8, pruning, student nhỏ hơn | | ΔF1, latency, RAM | Journal | S20–S21 |
| E11 | Diễn giải physics | RQ1 | — | | Tương quan $\hat\phi$ với φ; ví dụ lỗi | Journal | S21 |
| E12 | Riêng tư (re-ID từ embedding) | — | — | | Re-ID accuracy | Journal (OPTIONAL) | S21 |

---

## 15. 12-Month Roadmap

### 15.1 Backward planning

```
Q1 Journal (S26)
  ↓ cần: C1–C5; sim-to-real đầy đủ (zero/few-shot); CMKD thật (MM-Fi); confounder; edge-profiled compression
Required experiments: E1–E11 (E9, E12 optional)
  ↓
Final model: PhyKD-Fall v2 (+ M7 compression)
  ↓
Algorithm development: baselines (S5–S6) → v1 = CMKD theo DT-02 gốc (logit/feature KD + early fusion) → v2 = + physics KD + async fusion + gate (S7–S11) → optimization (S20–S21)
  ↓
FallTwin v1 đã hiệu chỉnh với dữ liệu thật (S3–S5); Taramasco/MM-Fi pipeline (S2, S9, S14)
  ↓
Research gap đã xác minh (S1–S2)
```

Task **OPTIONAL** (không tạo evidence cho RQ chính): ứng dụng cảnh báo cho người thân, dashboard, LoRaWAN/Wi-Fi messaging, mô phỏng năng lượng pin, Glasgow (E9), re-ID (E12).

### 15.2 Phases

| Phase | Tháng | Sprint | Mục tiêu | Evidence |
|---|---|---|---|---|
| P1 — Gap, dữ liệu, mô phỏng | M1–M2 | S1–S4 | Novelty; tải và audit Taramasco/MM-Fi/NTU/UR Fall; pilot; FallTwin v0; teacher | Lit matrix, data card, E0, FallTwin v0 |
| P2 — Student & baseline (DT-02 v1) | M2–M3 | S5–S6 | Encoder thermal/radar; 9 baseline; hiệu chỉnh FallTwin v1; real-time gate | Bảng sơ bộ, latency |
| P3 — Proposed method (v2) | M4–M5 | S7–S11 | Physics KD + async fusion + gate; zero-shot Taramasco; E1–E4 | Bảng chính, ablation |
| P4 — Conference paper | M6 | S12–S13 | E5 rút gọn, E6 zero-shot đầy đủ; viết, nộp | Paper |
| P5 — Journal extension | M7–M8 | S14–S17 | CMKD thật MM-Fi; few-shot; FallTwin v2; sensitivity | E5, E6, E8 phần 1 |
| P6 — Large-scale experiments | M9–M10 | S18–S22 | Realism ablation; E8 cuối; compression; diễn giải | E7, E8, E10, E11 |
| P7 — Journal paper | M11–M12 | S23–S26 | Viết, review nội bộ, nộp | Manuscript + code |

### 15.3 Lịch theo tháng

| Tháng | Sprint | Thời gian | Gate |
|---|---|---|---|
| M1 | S1–S2 | 05/10 – 01/11/2026 | Research & Novelty Gate (cuối S2) |
| M2 | S3–S4 | 02/11 – 29/11/2026 | — |
| M3 | S5–S6 | 30/11 – 27/12/2026 | Simulation-realism check (cuối S5); Prototype + Real-time Gate (cuối S6) |
| M4 | S7–S9 | 28/12/2026 – 07/02/2027 | IJCNN go/no-go (20/01); Tết ≈ đầu 02/2027 → S9 giảm tải |
| M5 | S10–S11 | 08/02 – 07/03/2027 | Conference Research Gate (cuối S10); Conference Readiness (cuối S11) |
| M6 | S12–S13 | 08/03 – 04/04/2027 | **Conference Milestone** (cuối S13) |
| M7 | S14–S15 | 05/04 – 02/05/2027 | — |
| M8 | S16–S17 | 03/05 – 30/05/2027 | Journal Extension Gate (cuối S17) |
| M9 | S18–S19 | 31/05 – 27/06/2027 | — |
| M10 | S20–S22 | 28/06 – 08/08/2027 | Journal Experiment Gate (cuối S22) |
| M11 | S23–S24 | 09/08 – 05/09/2027 | — |
| M12 | S25–S26 | 06/09 – 03/10/2027 | **Journal Milestone** (cuối S26) |

---

## 16. Biweekly Sprints (26 sprint)

**Cấu trúc repo `phykd_fall/`:**

```
data/     taramasco.py (TaramascoDS) · mmfi.py (MMFiDS) · ntu_skeleton.py · urfall.py · splits.py (loso_splits)
sim/      motion_lib.py (MotionLibrary: Mixamo/AMASS/T2M) · scene.py (SceneSampler) · thermal_render.py (ThermalRenderer)
          · radar_sim.py (RadarSimL1 [RF-Genesis wrapper], RadarSimL2 [geometric proxy]) · confounders.py · adl_stream.py · calibrate_stats.py
physics/  extractor.py (PhysicsExtractor: com_height, vz, a_peak, torso_angle, t_ground)
models/   teacher.py (STGCNTeacher, PoseTransformer) · thermal_enc.py (ThermalEncoder) · radar_enc.py (PointNetLite, MicroDopplerCNN)
          · fusion.py (EarlyFusion, LateFusion, AsyncCrossAttnFusion, ReliabilityGate) · heads.py · phykd.py (PhyKDFall)
losses/   kd.py (logit_kd, feature_kd, physics_kd, relation_kd, crd)
train/    train_teacher.py · train_student.py · adapt_fewshot.py · calibrate.py · compress.py
eval/     metrics.py (sens, spec, f1, fa_per_24h, alarm_latency, physics_mae) · stats.py (bootstrap_ci, wilcoxon_holm) · latency.py · stream_eval.py
configs/  Hydra YAML · tests/ pytest · reports/ sprint_XX.md, figures/, tables/
```
Phụ thuộc: PyTorch, smplx, trimesh/pyrender (hoặc nvdiffrast), numpy/scipy, RF-Genesis (nếu dùng), pyskl hoặc tự cài ST-GCN, MediaPipe / Ultralytics (pose cho UR Fall), hydra-core, pandas, scikit-learn, onnx, onnxruntime, fvcore, pytest, MLflow (local).

**Quy ước:** mỗi sprint kết thúc bằng `reports/sprint_XX.md` (≤ 2 trang) + demo 30 phút với cố vấn. Con số trong "Expected results" là **mục tiêu**, không phải kết quả.

---

### Sprint 1 — 05/10 → 18/10/2026 · M1 · Onboarding, novelty, xin dữ liệu
- **Objective:** Xác minh gap/novelty; gửi yêu cầu/tải dữ liệu; dựng môi trường.
- **Research tasks:** Systematic search theo 5.5 (≥ 25 bài); đọc kỹ Zhao et al. 2018 (RF-Pose), Taramasco et al. 2025, MM-Fi 2023, TaFall 2026, mmFall; kiểm tra license Taramasco (CC-BY), MM-Fi, NTU RGB+D 120, UR Fall.
- **Algorithm/Model tasks:** Sinh viên viết lại formulation Mục 3.1 và định nghĩa φ(t) bằng lời + công thức.
- **Coding tasks:** Repo + pytest + pre-commit. `data/taramasco.py::TaramascoDS` (OSF → (thermal frames, radar frames, timestamps, label, subject)); test: đọc 1 bản ghi, kiểm tra tần số thực tế.
- **Simulation tasks:** Data audit Taramasco: số bản ghi/người, tần số từng cảm biến, nhãn thời điểm ngã có hay không.
- **Expected results:** Lit matrix ≥ 25; data card v0; đăng ký NTU RGB+D 120 đã gửi; bài tập PyTorch (train CNN nhỏ trên ảnh nhiệt Taramasco: ngã vs không) chạy được.
- **Milestone:** Môi trường + dữ liệu thật đầu tiên.
- **Deliverables:** `lit_matrix.xlsx` v0, `data_card.md` v0, repo, `reports/sprint_01.md`.
- **Risk & Plan B:** Không tải được Taramasco → liên hệ tác giả; song song tìm dataset thermal/radar ngã khác (Mục 21).

### Sprint 2 — 19/10 → 01/11/2026 · M1 · Pilot FallTwin & physics extractor
- **Objective:** Đo chi phí mô phỏng; cài physics extractor; chọn mức radar sim.
- **Research tasks:** Lit matrix ≥ 40; đọc RF-Genesis, HybridSim, Alamgeer et al. 2025 (synthetic falls); datasheet MLX90640 (FOV, NETD, tần số), cấu hình IWR6843 trong Taramasco/MM-Fi.
- **Algorithm/Model tasks:** Chốt danh sách 8 kiểu ngã, ≥ 10 ADL, ≥ 5 confounder; định nghĩa ngưỡng $h_{thr}$ cho $T_{ground}$.
- **Coding tasks:** `physics/extractor.py::PhysicsExtractor(joints, fps) -> dict` (test trên chuỗi tổng hợp rơi tự do: $v_z$ đúng công thức); `sim/thermal_render.py::ThermalRenderer` bản thô; thử `RadarSimL1` (RF-Genesis) và `RadarSimL2` (proxy); `eval/latency.py::benchmark`.
- **Simulation tasks:** E0: 5 clip × 1 cảnh; đo thời gian/khung, VRAM, dung lượng.
- **Expected results:** Số đo E0; quyết định mức radar sim; bảng tham số cảm biến.
- **Milestone:** 🔶 **Research & Novelty Gate (Month 1)**.
- **Deliverables:** `pilot_benchmark.md`, `sensor_params.yaml`, `lit_matrix.xlsx` v1.
- **Risk & Plan B:** RF-Genesis không chạy/quá chậm → RadarSimL2 làm chính, RF-Genesis chỉ cho tập nhỏ để so sánh (E7).

### Sprint 3 — 02/11 → 15/11/2026 · M2 · FallTwin v0: chuyển động + thermal
- **Objective:** Thư viện chuyển động và renderer nhiệt hoàn chỉnh có confounder.
- **Research tasks:** Đặc tả FallTwin (2 trang): giả định nhiệt độ cơ thể/quần áo, mô hình confounder, giới hạn.
- **Algorithm/Model tasks:** Lọc AMASS/HumanML3D theo text; sinh thêm ngã bằng text-to-motion cho kiểu thiếu; retarget Mixamo sang SMPL.
- **Coding tasks:** `sim/motion_lib.py::MotionLibrary(sources).sample(label)`; `sim/scene.py::SceneSampler`; `sim/thermal_render.py::ThermalRenderer(fov, res=(24,32), netd, fps)`; `sim/confounders.py` (HeatSource, HotAirflow, Pet, SunPatch); tests: pixel người ấm hơn nền, confounder đúng vị trí, tần số khung đúng.
- **Simulation tasks:** Sinh 500 clip thử; xem trực quan 50 mẫu.
- **Expected results:** Thống kê số clip theo kiểu ngã/ADL; ảnh nhiệt mô phỏng nhìn hợp lý so với Taramasco.
- **Milestone:** Giao diện FallTwin đóng băng.
- **Deliverables:** `falltwin_spec.md`, 500 clip, hình so sánh thermal sim vs real.
- **Risk & Plan B:** Ít chuyển động ngã thật → tăng Mixamo + text-to-motion; ghi rõ tỉ lệ nguồn.

### Sprint 4 — 16/11 → 29/11/2026 · M2 · Radar sim + teacher
- **Objective:** Radar mô phỏng chạy ở quy mô dataset; teacher pose huấn luyện xong.
- **Research tasks:** Đọc ST-GCN, Hinton KD, FitNets.
- **Algorithm/Model tasks:** Teacher ST-GCN vs Transformer nhỏ trên NTU (falling vs khác) + UR Fall (pose từ RGB) + FallTwin pose.
- **Coding tasks:** `sim/radar_sim.py` hoàn chỉnh (point cloud + micro-Doppler); `sim/adl_stream.py::ADLStream(hours=24)`; `models/teacher.py`; `train/train_teacher.py`; tests: Doppler dấu đúng khi người tiến/lùi; số điểm/khung trong khoảng cấu hình.
- **Simulation tasks:** FallTwin v0: ~5,000 clip + 20 luồng ADL 24 h (chia A/B/C).
- **Expected results:** Teacher F1 trên test pose (báo cáo đúng số đo); FallTwin v0 hoàn chỉnh.
- **Milestone:** Teacher + FallTwin v0.
- **Deliverables:** Checkpoint teacher, FallTwin v0 index, bảng teacher.
- **Risk & Plan B:** NTU chưa được cấp quyền → teacher dùng UR Fall + FallTwin pose + MM-Fi (ADL).

### Sprint 5 — 30/11 → 13/12/2026 · M3 · Student encoders + hiệu chỉnh FallTwin v1
- **Objective:** Student single-modality và hai fusion đơn giản; FallTwin khớp thống kê dữ liệu thật.
- **Research tasks:** Chọn metric khoảng cách phân bố (Wasserstein-1/KS) và ngưỡng chấp nhận.
- **Algorithm/Model tasks:** M3 thermal encoder, M4 radar encoder (PointNet-lite vs μD-CNN); B1, B2, B4, B5.
- **Coding tasks:** `models/thermal_enc.py`, `models/radar_enc.py`, `models/fusion.py::EarlyFusion, LateFusion`; `sim/calibrate_stats.py::compare(sim, real) -> report`; `eval/metrics.py::sens, spec, f1, fa_per_24h`.
- **Simulation tasks:** So sánh thống kê FallTwin vs Taramasco/MM-Fi; chỉnh tham số; train B1, B2, B4, B5 (1 seed).
- **Expected results:** Báo cáo hiệu chỉnh (trước/sau); F1 sơ bộ B1, B2, B4, B5 trên sim và zero-shot thử trên Taramasco.
- **Milestone:** 🔶 **Simulation-realism check**.
- **Deliverables:** `calibration_report.md`, FallTwin v1, `results/prototype_v0.csv`.
- **Risk & Plan B:** Khoảng cách phân bố lớn → domain randomization rộng hơn; giảm phụ thuộc chi tiết (dùng đặc trưng chuẩn hoá theo nền).

### Sprint 6 — 14/12 → 27/12/2026 · M3 · KD baselines + real-time gate
- **Objective:** Đủ baseline; đo edge-profiled latency.
- **Research tasks:** Đọc CRD, ModDrop, mmFall code.
- **Algorithm/Model tasks:** B3 mmFall, B6 logit KD, B7 feature KD, B8 CRD, B9 ModDrop; **v1 = CMKD theo DT-02 gốc** (logit + feature KD, early fusion).
- **Coding tasks:** `losses/kd.py::logit_kd, feature_kd, crd`; `eval/stream_eval.py::alarm_latency`; `eval/latency.py` cho student.
- **Simulation tasks:** B1–B9 + v1 trên FallTwin v1 (1 seed); đo $T_{alarm}$ và latency CPU 1 luồng.
- **Expected results:** Mọi baseline chạy end-to-end; latency so với mục tiêu Mục 12.
- **Milestone:** 🔶 **Prototype Gate + Real-time Gate (Month 3)**.
- **Deliverables:** `results/baselines_v1.csv`, `latency_report.md`.
- **Risk & Plan B:** mmFall không chạy trên định dạng mới → bản tự cài đơn giản; latency vượt → giảm $W$, giảm kênh.

### Sprint 7 — 28/12/2026 → 10/01/2027 · M4 · E1 + cài PhyKD-Fall
- **Objective:** Kết quả RQ1 cho baseline; cài physics KD và async fusion.
- **Research tasks:** Nháp Related Work (1 trang).
- **Algorithm/Model tasks:** v2 = physics KD + relation KD + AsyncCrossAttnFusion + ReliabilityGate + modality dropout.
- **Coding tasks:** `losses/kd.py::physics_kd(phi_hat, phi, w), relation_kd`; `models/fusion.py::AsyncCrossAttnFusion(time_enc), ReliabilityGate`; `models/phykd.py::PhyKDFall`; tests: thiếu một modality vẫn chạy; time encoding đúng thứ tự.
- **Simulation tasks:** E1: B1–B9 + v1 × 3 seed trên FallTwin v1.
- **Expected results:** Bảng E1; FA/24 h của từng baseline.
- **Milestone:** Baseline results đóng băng.
- **Deliverables:** Bảng E1, hình FA/24 h.
- **Risk & Plan B:** KD baselines không hơn B4/B5 → kiểm tra teacher; nếu teacher yếu thì cải thiện teacher trước.

### Sprint 8 — 11/01 → 24/01/2027 · M4 · E2 + PhyKD-Fall kết quả đầu
- **Objective:** Robustness/confounder của baseline; kết quả đầu của v2.
- **Research tasks:** Kiểm tra điều kiện nộp IJCNN 2027 (deadline 31/01/2027).
- **Algorithm/Model tasks:** Tune λ_φ, τ trên val.
- **Coding tasks:** Config sweep confounder `configs/e2/*.yaml`; `eval/stats.py::bootstrap_ci, wilcoxon_holm`.
- **Simulation tasks:** E2 (B4, B5, B9, v1 × confounder × mất modality × lệch thời gian, 3 seed); v2 trên cùng cấu hình.
- **Expected results:** FA/24 h theo confounder; v2 so với baseline tốt nhất.
- **Milestone:** 🔶 **IJCNN go/no-go** (20/01/2027): GO khi v2 vượt baseline tốt nhất về F1 và FA/24 h có ý nghĩa thống kê trên FallTwin.
- **Deliverables:** Bảng E2; bản thảo 4 trang.
- **Risk & Plan B:** v2 không hơn → ablation sớm; NO-GO là mặc định an toàn.

### Sprint 9 — 25/01 → 07/02/2027 · M4 · Buffer Tết + zero-shot Taramasco
- **Objective:** Pipeline đánh giá dữ liệu thật; logic báo động. Giảm tải do Tết.
- **Research tasks:** (Nếu GO) hoàn thiện và nộp IJCNN.
- **Algorithm/Model tasks:** Logic báo động hai điều kiện (p(fall) + $\hat T_{ground}$); chọn ngưỡng trên FallTwin val.
- **Coding tasks:** `data/splits.py::loso_splits`; `eval/stream_eval.py` cho Taramasco; tests: không người nào xuất hiện ở cả train/test.
- **Simulation tasks:** Zero-shot B1–B9, v1, v2 trên Taramasco (LOSO, 1 seed).
- **Expected results:** Sensitivity/specificity zero-shot đầu tiên.
- **Milestone:** Pipeline real-test chạy.
- **Deliverables:** `results/zeroshot_v0.csv`.
- **Risk & Plan B:** Zero-shot quá thấp (< 60% sensitivity) → báo cố vấn; kiểm tra lệch cấu hình cảm biến; tăng domain randomization trước S10.

### Sprint 10 — 08/02 → 21/02/2027 · M5 · E3 đầy đủ
- **Objective:** Kết quả chính của Conference.
- **Research tasks:** Chốt venue (Mục 22) theo deadline công bố.
- **Algorithm/Model tasks:** Chốt siêu tham số v2 trên val.
- **Coding tasks:** `scripts/run_e3.sh`; `tables/main_table.tex` tự sinh.
- **Simulation tasks:** E3: v2 vs B1–B9, v1 × confounder × 5 seed; physics MAE.
- **Expected results:** Bảng chính có CI 95% và p-value Holm.
- **Milestone:** 🔶 **Conference Research Gate**.
- **Deliverables:** Main table, hình FA/24 h vs sensitivity.
- **Risk & Plan B:** H1 chỉ đúng một phần → thu hẹp claim (vd. physics KD giảm báo động giả nhưng không tăng sensitivity).

### Sprint 11 — 22/02 → 07/03/2027 · M5 · Ablation
- **Objective:** Mỗi thành phần của v2 có đóng góp đo được.
- **Research tasks:** Phân tích lỗi theo kiểu ngã, loại confounder, modality.
- **Algorithm/Model tasks:** E4; chỉnh v2 nếu có hypothesis rõ.
- **Coding tasks:** Config ablation; `eval/analysis.py::gate_vs_confounder`.
- **Simulation tasks:** E4 (5 seed).
- **Expected results:** Thành phần không đóng góp bị loại khỏi mô hình và claim.
- **Milestone:** 🔶 **Conference Readiness**.
- **Deliverables:** Bảng ablation; draft 6 trang.
- **Risk & Plan B:** Async fusion không hơn early fusion → giữ early fusion, báo cáo trung thực.

### Sprint 12 — 08/03 → 21/03/2027 · M6 · Zero-shot đầy đủ, sensitivity, viết
- **Objective:** Bằng chứng trên dữ liệu thật cho conference.
- **Research tasks:** Intro, related work, discussion, limitations (simulation-only, Taramasco nhỏ, không có người cao tuổi).
- **Algorithm/Model tasks:** E5 rút gọn ($W$, λ_φ); E6 zero-shot (5 seed, LOSO).
- **Coding tasks:** Script vẽ mọi hình từ CSV.
- **Simulation tasks:** E5, E6 zero-shot.
- **Expected results:** Bảng sim-to-real; ΔF1 sim − real theo phương pháp.
- **Milestone:** Full draft v1.
- **Deliverables:** Paper draft v1.
- **Risk & Plan B:** Zero-shot yếu → báo cáo như phát hiện về khoảng cách sim-to-real; few-shot đưa lên sớm nếu kịp.

### Sprint 13 — 22/03 → 04/04/2027 · M6 · Conference submission package
- **Objective:** Paper sẵn sàng nộp.
- **Research tasks:** Review nội bộ (cố vấn + 1 đồng nghiệp).
- **Algorithm/Model tasks:** Code freeze.
- **Coding tasks:** Làm sạch repo, README, config; release FallTwin (code + cấu hình, không phân phối lại dữ liệu có license riêng).
- **Simulation tasks:** Chạy lại toàn bộ từ config đóng băng.
- **Expected results:** Số liệu tái lập nằm trong CI.
- **Milestone:** 🟢 **CONFERENCE MILESTONE**.
- **Deliverables:** PDF, supplementary, tag `v1.0-conf`.
- **Risk & Plan B:** Venue chưa mở → giữ bản, nộp venue kế tiếp.

### Sprint 14 — 05/04 → 18/04/2027 · M7 · MM-Fi pipeline + few-shot protocol
- **Objective:** Chuẩn bị CMKD thật và few-shot.
- **Research tasks:** Chính sách bài mở rộng của journal mục tiêu.
- **Algorithm/Model tasks:** Thiết kế CMKD trên MM-Fi: teacher pose (keypoint MM-Fi) → radar student feature.
- **Coding tasks:** `data/mmfi.py::MMFiDS`; `train/adapt_fewshot.py`.
- **Simulation tasks:** Audit MM-Fi (tần số radar, điểm/khung) so với Taramasco.
- **Expected results:** Pipeline MM-Fi chạy.
- **Milestone:** —
- **Deliverables:** `mmfi_card.md`, protocol few-shot.
- **Risk & Plan B:** Cấu hình radar MM-Fi khác Taramasco nhiều → chuẩn hoá point cloud; báo cáo khác biệt.

### Sprint 15 — 19/04 → 02/05/2027 · M7 · CMKD thật (E8 phần 1)
- **Objective:** Pretrain radar branch bằng CMKD thật.
- **Research tasks:** Đọc lại MM-Fi baselines.
- **Algorithm/Model tasks:** Pretrain trên MM-Fi → fine-tune FallTwin → test Taramasco.
- **Coding tasks:** `train/train_student.py --pretrain mmfi`.
- **Simulation tasks:** E8 phần 1 (3 seed).
- **Expected results:** F1 Taramasco có/không pretrain MM-Fi.
- **Milestone:** —
- **Deliverables:** Bảng E8 v0.
- **Risk & Plan B:** Không cải thiện → báo cáo; thử chỉ dùng MM-Fi cho hiệu chỉnh FallTwin.

### Sprint 16 — 03/05 → 16/05/2027 · M8 · FallTwin v2 + sensitivity đầy đủ
- **Objective:** Mở rộng mô phỏng; độ nhạy tham số.
- **Research tasks:** Ghi lại tất cả giả định của FallTwin (bảng tham số + nguồn).
- **Algorithm/Model tasks:** Thêm phòng/vị trí cảm biến, kiểu ngã hiếm, người nhiều kích thước.
- **Coding tasks:** Mở rộng `SceneSampler`, `MotionLibrary`.
- **Simulation tasks:** E5 đầy đủ (λ_φ, τ, $W$, tần số thermal/radar).
- **Expected results:** Vùng tham số ổn định.
- **Milestone:** —
- **Deliverables:** FallTwin v2, hình sensitivity.
- **Risk & Plan B:** Tăng quy mô quá tốn GPU → giữ v1, chỉ thêm biến thể quan trọng.

### Sprint 17 — 17/05 → 30/05/2027 · M8 · Few-shot đầy đủ (E6)
- **Objective:** RQ3 hoàn chỉnh.
- **Research tasks:** Bảng "mới trong journal so với conference".
- **Algorithm/Model tasks:** Few-shot k = 1/2/3 người; so sánh với train-from-scratch trên real.
- **Coding tasks:** Config E6 few-shot.
- **Simulation tasks:** E6 đầy đủ (5 seed, LOSO).
- **Expected results:** Đường cong few-shot.
- **Milestone:** 🔶 **Journal Extension Gate (Month 8)**.
- **Deliverables:** Kết quả E6, bảng "new vs conference".
- **Risk & Plan B:** Phần mới < 30% → đẩy E10 sớm hoặc thêm E9.

### Sprint 18 — 31/05 → 13/06/2027 · M9 · Realism ablation (E7)
- **Objective:** Thành phần nào của FallTwin quan trọng cho sim-to-real.
- **Research tasks:** Phân tích lỗi trên dữ liệu thật.
- **Algorithm/Model tasks:** Không đổi mô hình.
- **Coding tasks:** Config E7.
- **Simulation tasks:** E7: bỏ domain randomization / bỏ hiệu chỉnh / radar mức 1 vs 2 / bỏ confounder khi train.
- **Expected results:** Bảng đóng góp của từng thành phần mô phỏng.
- **Milestone:** —
- **Deliverables:** Bảng E7.
- **Risk & Plan B:** Khác biệt không có ý nghĩa → báo cáo; giữ cấu hình đơn giản nhất.

### Sprint 19 — 14/06 → 27/06/2027 · M9 · E8 cuối + E9 (optional)
- **Objective:** Hoàn tất RQ4.
- **Research tasks:** Kiểm tra Glasgow dataset (tần số, định dạng).
- **Algorithm/Model tasks:** Radar branch test trên Glasgow (micro-Doppler) nếu tương thích.
- **Coding tasks:** `data/glasgow.py` (OPTIONAL).
- **Simulation tasks:** E8 (5 seed); E9.
- **Expected results:** Bảng RQ4.
- **Milestone:** —
- **Deliverables:** Bảng E8, E9.
- **Risk & Plan B:** Glasgow không tương thích (5.8 GHz, chỉ μD) → bỏ E9.

### Sprint 20 — 28/06 → 11/07/2027 · M10 · Compression (E10 phần 1)
- **Objective:** Student nằm trong ngân sách edge.
- **Research tasks:** Chọn kỹ thuật pruning/quantization phù hợp ONNX Runtime.
- **Algorithm/Model tasks:** Pruning có cấu trúc + INT8 PTQ; distill sang student nhỏ hơn.
- **Coding tasks:** `train/compress.py`; `tools/export_onnx.py`; `tools/quantize_int8.py`.
- **Simulation tasks:** E10 phần 1.
- **Expected results:** ΔF1 ≤ 1 ở INT8 (mục tiêu).
- **Milestone:** —
- **Deliverables:** Checkpoint nén, ONNX.
- **Risk & Plan B:** INT8 mất > 1 điểm → QAT ngắn.

### Sprint 21 — 12/07 → 25/07/2027 · M10 · E10 phần 2 + E11 (+ E12)
- **Objective:** Hoàn tất bằng chứng journal.
- **Research tasks:** Diễn giải φ̂ theo kiểu ngã.
- **Algorithm/Model tasks:** (OPTIONAL) re-ID attack trên embedding student.
- **Coding tasks:** `eval/analysis.py::physics_examples`; (OPTIONAL) `eval/reid.py`.
- **Simulation tasks:** E10 latency đầy đủ, E11, (E12).
- **Expected results:** Bảng/hình cuối.
- **Milestone:** —
- **Deliverables:** Bảng/hình journal.
- **Risk & Plan B:** Chậm → bỏ E12, dùng S22 làm buffer.

### Sprint 22 — 26/07 → 08/08/2027 · M10 · Consolidation & freeze
- **Objective:** Đóng băng thực nghiệm.
- **Research tasks:** Mọi claim có bảng/hình + CI.
- **Algorithm/Model tasks:** Không.
- **Coding tasks:** `scripts/reproduce_all.sh`.
- **Simulation tasks:** Lấp seed thiếu, CI rộng.
- **Expected results:** Mọi con số tái lập.
- **Milestone:** 🔶 **Journal Experiment Gate (Month 10)**.
- **Deliverables:** `results_final/`, tag `v2.0-exp-freeze`.
- **Risk & Plan B:** Thiếu experiment không thiết yếu → future work.

### Sprint 23 — 09/08 → 22/08/2027 · M11 · Viết journal (1)
- **Objective:** Intro, related work, method, FallTwin.
- **Research tasks:** Cập nhật literature 2027.
- **Algorithm/Model tasks:** Mô tả hình thức physics KD và async fusion.
- **Coding tasks:** Hình kiến trúc, hình FallTwin.
- **Simulation tasks:** Không.
- **Expected results:** 50% manuscript.
- **Milestone:** —
- **Deliverables:** Sections 1–4.
- **Risk & Plan B:** Bài mới trùng → thêm so sánh nếu có code.

### Sprint 24 — 23/08 → 05/09/2027 · M11 · Viết journal (2)
- **Objective:** Experiments, discussion, threats to validity, supplementary.
- **Research tasks:** Threats to validity: mô phỏng, Taramasco nhỏ và người trẻ, không có người cao tuổi, không có edge thật.
- **Algorithm/Model tasks:** Không.
- **Coding tasks:** Bảng LaTeX tự sinh.
- **Simulation tasks:** Không.
- **Expected results:** Full draft v1.
- **Milestone:** Full draft.
- **Deliverables:** Manuscript v1 + supplementary.
- **Risk & Plan B:** Quá dài → chuyển chi tiết sang supplementary.

### Sprint 25 — 06/09 → 19/09/2027 · M12 · Review nội bộ & sửa
- **Objective:** Đạt chất lượng Q1.
- **Research tasks:** Review nội bộ theo chuẩn reviewer/AE.
- **Algorithm/Model tasks:** Chỉ sửa khi phát hiện lỗi thực nghiệm.
- **Coding tasks:** Release code + FallTwin.
- **Simulation tasks:** Tối đa 1 experiment nhỏ nếu review yêu cầu.
- **Expected results:** Manuscript v2.
- **Milestone:** —
- **Deliverables:** v2, cover letter nháp, highlights.
- **Risk & Plan B:** Lỗi lớn → dời 2 tuần (S26).

### Sprint 26 — 20/09 → 03/10/2027 · M12 · Journal submission
- **Objective:** Nộp journal Q1.
- **Research tasks:** Định dạng, disclosure bản conference, data/code availability.
- **Algorithm/Model tasks:** Không.
- **Coding tasks:** Tag `v3.0-journal`, DOI Zenodo.
- **Simulation tasks:** Không.
- **Expected results:** Đã nộp.
- **Milestone:** 🟢 **JOURNAL MILESTONE**.
- **Deliverables:** Manuscript, cover letter, supplementary, code DOI; ≥ 70% nội dung dùng lại cho khóa luận.
- **Risk & Plan B:** Desk reject → nộp journal dự phòng trong 2 tuần (Mục 23).

---

## 17. Algorithm Development Plan

| Version | Sprint | Problem addressed | Algorithm change | Expected improvement (hypothesis) | Experiment | Success criteria |
|---|---|---|---|---|---|---|
| Baseline | S5–S6 | Cần mốc so sánh | B1–B9 | — | E1 | Mọi baseline chạy; 2 lần chạy lệch < 1 điểm F1 |
| Baseline enhancement | S6–S7 | Baseline yếu do setup | Calibration, ModDrop, tuning cùng ngân sách | So sánh công bằng | E1, E2 | Baseline sau tuning ≥ trước |
| **Proposed v1** = CMKD theo DT-02 gốc | S6–S7 | Student riêng tư thiếu tri thức tư thế | Logit + feature KD từ teacher pose; early fusion | v1 > B1, B2, B4 về F1 | E1 | Δ có ý nghĩa thống kê |
| Ablation v1 | S8 | v1 có báo động giả cao với confounder? có lỗi do nội suy thời gian? | Chạy v1 dưới confounder, lệch thời gian, mất modality | Xác định điểm yếu | E2 | Nguồn lỗi được định lượng |
| **Proposed v2** = PhyKD-Fall | S7–S10 | Thiếu ràng buộc vật lý; fusion bất đồng bộ; confounder | + physics KD + relation KD + async fusion + reliability gate + modality dropout | F1 ↑, FA/24 h ↓, robust khi mất modality (H1, H2) | E3 | H1 và H2 được ủng hộ trên FallTwin |
| Ablation v2 | S11 | Thành phần nào cần? | Bỏ từng thành phần (E4) | Mỗi thành phần có đóng góp | E4 | Δ có ý nghĩa (Holm p < 0.05) ở F1 hoặc FA/24 h |
| Optimization | S20–S21 | Ngân sách edge | Pruning, INT8, student nhỏ hơn | Latency ↓, ΔF1 ≤ 1 | E10 | Đạt Mục 12 |
| Final | S22 | — | Đóng băng | — | E1–E11 | Mọi claim có bằng chứng + CI |

---

## 18. Model Development Plan

| Hạng mục | Quyết định | Hypothesis gắn kèm |
|---|---|---|
| Architecture | Teacher pose (M1) + physics extractor (M2) + student thermal (M3) + radar (M4) + async fusion/gate (M5) + heads (M6) | Physics KD giúp student "đo" cú ngã (H1) |
| Input/output | Thermal 24×32 @2–8 Hz; radar ≤ 128 điểm/khung @8–20 Hz; cửa sổ $W$ 2–4 s → p(fall), φ̂, t_alarm | $W$ ngắn giảm latency nhưng giảm F1 (E5) |
| Feature representation | Token theo khung + mã hoá thời gian liên tục | Không nội suy student tránh sai lệch (E4: async vs early) |
| Losses | CE + logit KD + feature KD + physics KD + relation KD | Mỗi loss có dòng trong E4 |
| Training strategy | Teacher → (MM-Fi pretrain, journal) → distill trên FallTwin → (few-shot real) → calibration | — |
| Validation strategy | FallTwin nhóm B (clip, cảnh, cảm biến khác); không dùng Taramasco cho tuning zero-shot | — |
| Hyperparameters (khởi tạo, giả định) | AdamW lr 1e-3 (student), wd 1e-4; batch 64; τ ∈ {2, 4}; λ_KD, λ_F, λ_φ ∈ {0.1, 0.5, 1}; $p_{md}$ ∈ {0.1, 0.3}; $W$ ∈ {2, 3, 4} s | Grid nhỏ/Optuna ≤ 30 trial mỗi phương pháp, cùng ngân sách cho baseline |
| Data augmentation | Thermal: nhiễu, dịch nhiệt độ nền, flip, confounder; radar: jitter điểm, dropout điểm, nhiễu Doppler, xoay quanh trục đứng; thời gian: jitter timestamp, mất khung | Augmentation thời gian giảm ΔF1 khi lệch thời gian (E4) |
| Ablation | E4 | — |
| Model complexity | Student ≤ 300k params, ≤ 50 MMACs/quyết định (giả định) | RQ5 |
| Inference latency | Mục 12 | — |

**Quy tắc:** không thêm module nếu không có hypothesis và experiment. Đã loại trước: diffusion sinh dữ liệu radar, LLM giải thích, Transformer lớn cho student, mô phỏng năng lượng.

---

## 19. Milestones & Feasibility Gates

| Gate | Thời điểm | GREEN | YELLOW | RED → hành động |
|---|---|---|---|---|
| Research & Novelty (M1) | Cuối S2 · 01/11/2026 | Lit matrix ≥ 40; không bài trùng C2 + C3; Taramasco + MM-Fi tải được; pilot xong; sinh viên đạt bài PyTorch | Trùng một phần | Trùng C2 + C3 → pivot 5.5; không có Taramasco → Plan B dữ liệu (Mục 21) |
| Simulation-realism | Cuối S5 · 13/12/2026 | Khoảng cách phân bố sim–real dưới ngưỡng định trước cho ≥ 4/5 thống kê | 2–3/5 | ≤ 1/5 → radar proxy + domain randomization rộng; xem lại renderer nhiệt |
| Prototype (M2–M3) | Cuối S6 · 27/12/2026 | FallTwin v1; teacher; B1–B9 + v1 end-to-end; bảng sơ bộ | Thiếu B3/B8 | Chưa end-to-end → dồn 1 sprint sửa; IJCNN mặc định NO-GO |
| Real-time (M3) | Cuối S6 | Alarm latency trung vị ≤ 1.5 s; latency CPU 1 luồng ≤ 50 ms | Một trong hai | Không đạt → giảm $W$, kênh, thay fusion |
| IJCNN go/no-go | 20/01/2027 | v2 > baseline tốt nhất có ý nghĩa | — | NO-GO |
| Conference Research (M4–5) | Cuối S10 · 21/02/2027 | H1, H2 ủng hộ có CI; zero-shot có số đo | Một phần | Bác bỏ → contribution chính chuyển sang FallTwin + benchmark confounder + phát hiện sim-to-real |
| Conference Readiness (M5) | Cuối S11 · 07/03/2027 | Algorithm, baselines, main exp, ablation, zero-shot, draft | Thiếu ablation phụ | Thiếu main table → bỏ E5 khỏi paper |
| **Conference Milestone (M6)** | Cuối S13 · 04/04/2027 | Paper ready/submitted | Ready, chờ deadline | Nộp venue kế tiếp |
| Journal Extension (M8) | Cuối S17 · 30/05/2027 | ≥ 2 contribution mới (few-shot, CMKD thật, compression) và ≥ 30% nội dung mới (quy ước nội bộ; kiểm chính sách journal) | 1 | 0 → đẩy E10 + E7 làm trọng tâm |
| Journal Experiment (M10) | Cuối S22 · 08/08/2027 | E1–E11 xong: robustness, generalization, ablation, efficiency, real-time | Thiếu E11 | Thiếu E8 → Plan B RQ4 |
| **Journal Milestone (M12)** | Cuối S26 · 03/10/2027 | Q1 manuscript submitted | Chờ đồng tác giả | — |

---

## 20. Critical Path

```
Novelty + dữ liệu thật (S1–S2)
   ↓
Physics extractor + pilot sim (S2)
   ↓
FallTwin v0: chuyển động + thermal (S3) → radar + ADL 24 h (S4)  ║ song song: teacher (S4)
   ↓                                                              ║
Hiệu chỉnh FallTwin v1 với Taramasco/MM-Fi (S5) ◄═════════════════╝
   ↓
Baselines + v1 (S5–S6) → E1, E2 (S7–S8) → PhyKD-Fall v2 → E3 (S10) → Ablation (S11)
   ↓                          ║ song song: zero-shot pipeline Taramasco (S9)
Zero-shot đầy đủ (S12) ◄══════╝
   ↓
Conference paper (S12–S13)
   ↓
MM-Fi CMKD (S14–S15) · Few-shot (S17) · Realism ablation (S18) · Compression (S20–S21)
   ↓
Freeze (S22) → Journal writing (S23–S26)
```

| Loại | Nội dung |
|---|---|
| Critical tasks | Dữ liệu thật tải được; FallTwin + hiệu chỉnh; teacher; baselines; v2; E3; zero-shot Taramasco |
| Dependencies | Student cần FallTwin; physics KD cần teacher + extractor; zero-shot cần pipeline Taramasco; E8 cần MM-Fi |
| Parallel tasks | Teacher song song FallTwin; zero-shot pipeline song song v2; related work song song thực nghiệm |
| Bottlenecks | (1) độ thực tế của radar sim; (2) kích thước Taramasco; (3) GPU nếu dùng ray tracing; (4) viết tiếng Anh |
| Buffer | S9 (Tết), một phần S13, S22, một phần S26 ≈ 3 sprint |

---

## 21. Risk & Contingency

| Risk | Trigger | Plan A | Plan B |
|---|---|---|---|
| Novelty yếu | Bài trùng physics KD + thermal–radar ở S1–S2 hoặc trong năm | Nhấn FallTwin + benchmark confounder + sim-to-real | Chuyển thành benchmark có hệ thống (C1 + C4) |
| Mô phỏng nặng | Radar ray tracing > ngân sách GPU | Giảm số khung, cache | Radar proxy hình học (mức 2) làm chính |
| Mô phỏng thiếu thực tế | Simulation-realism check RED | Hiệu chỉnh tham số, domain randomization | Few-shot trên dữ liệu thật làm kết quả chính; FallTwin chỉ là pretraining |
| Model không hội tụ | Val loss không giảm sau 10 epoch | Giảm lr, kiểm tra dữ liệu, chuẩn hoá thermal | Student đơn giản hơn (late fusion + KD) |
| Teacher yếu | Teacher F1 thấp trên pose test | Thêm dữ liệu pose (NTU, MM-Fi ADL) | Dùng φ(t) trực tiếp (không cần teacher network) làm privileged target |
| Baseline không tái lập | > 1 sprint cho một baseline | Debug với code gốc | Baseline thay thế (Mục 10) |
| KD không cải thiện | v2 ≤ v1 ở E3 | Ablation tìm nguyên nhân | Claim hẹp: physics KD giúp diễn giải + giảm FA dù F1 ngang |
| Real-time không đạt | Alarm latency > 1.5 s | Giảm $W$, logic sớm | Student nhỏ hơn, bỏ cross-attention |
| Dataset thật không tải được / không dùng được | Taramasco lỗi định dạng hoặc thiếu nhãn thời điểm | Liên hệ tác giả | Dùng dataset thermal hoặc radar ngã khác (tìm ở S1–S2); RQ3 tách thành real-thermal và real-radar riêng |
| Taramasco quá nhỏ | CI quá rộng để kết luận | Báo cáo theo người, bootstrap | Bổ sung test radar trên dataset khác; giảm claim |
| Conference evidence yếu | Gate S10 YELLOW/RED | Experiment trọng tâm | Thu hẹp contribution |
| Journal novelty yếu | Gate S17 RED | Thêm E7 + E10 | Chiều đánh giá mới: re-ID privacy (E12) |
| GPU hạn chế | < 20 GPU-h/tuần | Radar proxy, ít seed ở sweep phụ | 3 seed cho sweep phụ |
| Sinh viên chậm | 2 sprint liên tiếp trượt deliverable | Họp tuần, pair coding | Bỏ E9, E12, MM-Fi pretraining |

**Kill criteria:**
- K1. Cuối S2: đã có bài làm đủ physics KD + async fusion thermal–radar → bỏ C2 như contribution chính.
- K2. Cuối S5: FallTwin không khớp dữ liệu thật ở bất kỳ thống kê nào sau 2 vòng hiệu chỉnh → FallTwin chỉ dùng pretraining; trọng tâm chuyển sang few-shot thật.
- K3. Cuối S10: v2 không tốt hơn v1 ở cả F1 lẫn FA/24 h → dừng v2; paper dựa trên FallTwin + benchmark.
- K4. Cuối S12: zero-shot sensitivity < 60% và few-shot không cải thiện → không claim sim-to-real; journal tập trung mô phỏng + phân tích khoảng cách.
- K5. Bất kỳ lúc nào phát hiện leakage (cùng clip/cùng người ở train và test) → dừng experiment liên quan, sửa, chạy lại.

---

## 22. Conference Strategy

| Venue | Rank (nguồn) | Thời gian / địa điểm | Deadline | Phù hợp | Trạng thái |
|---|---|---|---|---|---|
| **IEEE ICIP 2027** (ưu tiên) | CORE2023: **B** (portal.core.edu.au) | 29/11 – 03/12/2027, Singapore | **Chưa công bố** (kiểm tra 30/09/2026) | Image/signal processing; thermal + radar + KD | Kiểm deadline ở S10 |
| IJCNN 2027 (sớm, có điều kiện) | CORE2023: **B** | 14–18/06/2027, Cape Town | **31/01/2027** (6 trang IEEE); notification 15/03/2027 | Neural networks, KD, multimodal | Chỉ nộp nếu go/no-go (S8) = GO |
| ICONIP 2027 | **NEEDS VERIFICATION** | TBD | TBD | Neural information processing | Kiểm ở S10 |
| IEEE EMBC 2027 (trong DT-02) | Chưa xác minh hạng CORE (hội nghị y sinh) | TBD | TBD | Rất hợp ứng dụng chăm sóc sức khỏe | Phương án phụ nếu không cần hạng CORE B |
| IEEE RIVF 2027 (trong DT-02) | Chưa thấy bằng chứng CORE B | — | — | Hội nghị trong nước | Không khuyến nghị cho mục tiêu "rank B trở lên" |

CORE đã chuyển thành ICORE (có ICORE2026). Rank CORE2023 phải đối chiếu lại với ICORE2026 trước khi chốt (S10).

**Nội dung Conference (6–8 trang):** C1 (FallTwin, rút gọn), C2 + C3 (PhyKD-Fall), E1–E4 trên FallTwin, E6 zero-shot trên Taramasco, E5 rút gọn. Limitations: simulation-only, dataset thật nhỏ và người trẻ, edge-profiled.

---

## 23. Journal Strategy

| Journal | Q (nguồn, năm) | Publisher / OA | APC | Phù hợp | Yêu cầu dự kiến |
|---|---|---|---|---|---|
| **IEEE Journal of Biomedical and Health Informatics** (ưu tiên 1) | Q1 — SJR 2025 = 1.624; Q1 ở Computer Science Applications, Health Informatics, Electrical and Electronic Engineering… (scimagojr.com) | IEEE, hybrid | Chỉ khi chọn OA; mức phí **TBD** | Rất cao: giám sát sức khỏe người cao tuổi, cảm biến riêng tư | Dữ liệu thật, so sánh mạnh, thảo luận lâm sàng/đạo đức |
| **IEEE Internet of Things Journal** (ưu tiên 2) | Q1 — SJR 2025 = 2.144; Q1 ở 6 category | IEEE, hybrid | Scimago ghi APC ước tính USD 4,107 (2025) cho OA; route không OA **TBD** | Cao: edge AIoT, cảm biến | Edge efficiency, hệ thống |
| **IEEE Sensors Journal** (dự phòng; có trong DT-02) | Q1 — SJR 2025 = 0.947; Q1 ở Electrical and Electronic Engineering, Instrumentation | IEEE, hybrid | **TBD** | Cao: thermal + radar | Xử lý tín hiệu cảm biến |

**Chiến lược:** E6/E8 (dữ liệu thật) rõ → JBHI hoặc IoT-J; nếu sim-to-real yếu → Sensors Journal với trọng tâm mô phỏng + phân tích tín hiệu. Kiểm chính sách bài mở rộng từ conference trước S17. Quartile kiểm lại khi SJR/JCR 2026 công bố. Mặc định route không OA để không phát sinh APC.

---

## 24. Final Feasibility Report

| Category | Status | Evidence | Risk | Mitigation | Confidence |
|---|---|---|---|---|---|
| Research Gap | 🟢 | Không có dataset RGB + thermal + radar có ngã; confounder chưa có benchmark | Bài mới | Alert, nộp sớm | Cao |
| Novelty | 🟡 | CMKD chung đã có; physics KD + async thermal–radar chưa thấy | Search chưa hệ thống; TaFall gần ý | Protocol 5.5, K1 | Trung bình |
| Algorithm | 🟢 | φ(t) dạng đóng; KD chuẩn | Căn chỉnh thời gian | Timestamp + mã hoá thời gian | Cao |
| Model | 🟢 | Student, teacher nhỏ | Overfit dữ liệu thật nhỏ | Pretrain sim, LOSO | Cao |
| Dataset | 🟡 | Taramasco (đúng cảm biến DT-02), MM-Fi, NTU, UR Fall | Taramasco nhỏ; NTU cần đăng ký | CI theo người; teacher thay thế | Trung bình |
| Simulation | 🟡 | RF-Genesis có code; thermal renderer đơn giản | Thiếu thực tế | Hiệu chỉnh + randomization + radar proxy | Trung bình |
| Computation | 🟡 | ~350–450 / ~650–850 GPU-h (ước lượng) | Radar sim tốn | Pilot S2; proxy | Trung bình |
| Baseline | 🟢 | mmFall có code; KD chuẩn | CRD code | Bỏ nếu không chạy | Cao |
| Real-time | 🟢 (proxy) | Input rất nhỏ | Cửa sổ dài | Đo alarm latency trực tiếp | Cao |
| Conference ≤ 6M | 🟡 | FallTwin + E1–E4 + zero-shot thật | FallTwin trễ | Critical path, fallback | Trung bình |
| Journal ≤ 12M | 🟡 | Few-shot, MM-Fi CMKD, compression, realism ablation | Sim-to-real yếu | Plan B journal | Trung bình–thấp (phụ thuộc năng lực sinh viên) |

**Kết luận: 🟡 FEASIBLE WITH CONDITIONS** — với điều kiện C1–C4 (Mục 1) và các chuyển đổi ở Mục 0. DT-02 nguyên bản (mua cảm biến, thu dữ liệu diễn ngã tại lab) dưới ràng buộc simulation-only là **🔴 NOT CURRENTLY FEASIBLE**.

"Ready/submitted" nằm trong tầm kiểm soát; "accepted" thì không. Roadmap cam kết cái trước.

---

## 25. Success Criteria

| Mốc | Tiêu chí đo được |
|---|---|
| Tháng 1 | Lit matrix ≥ 40; novelty gate GREEN/YELLOW; Taramasco + MM-Fi đã tải và audit; pilot có số đo |
| Tháng 3 | FallTwin v1 qua simulation-realism check; teacher + 9 baseline + v1 end-to-end; latency report |
| Tháng 5 | E3 đầy đủ 5 seed có CI; ablation E4; zero-shot Taramasco có số đo |
| Tháng 6 | Conference paper hoàn chỉnh, tái lập từ `v1.0-conf`; nộp venue CORE B+ sớm nhất khả dụng |
| Tháng 8 | Few-shot đầy đủ; MM-Fi CMKD có kết quả; ≥ 2 contribution mới so với conference |
| Tháng 10 | E1–E11 đóng băng; `reproduce_all.sh` chạy lại toàn bộ |
| Tháng 12 | Journal Q1 đã nộp; code + FallTwin công khai có DOI; nội dung đủ cho khóa luận |
| Khoa học | Mọi claim có bảng/hình + CI 95%; kết quả thật báo cáo theo người; limitations nêu rõ simulation-only, dataset thật nhỏ, edge-profiled |
| Năng lực sinh viên | Tự trình bày được: vì sao CMKD đơn thuần chưa đủ mới, physics KD hoạt động thế nào, và khoảng cách sim-to-real được đo ra sao |

---

## Phụ lục A — TBD cần kiểm chứng

| # | Mục | Cách kiểm chứng | Sprint |
|---|---|---|---|
| T1 | Cấu hình GPU, quota | Phòng lab; `nvidia-smi`; E0 | S1–S2 |
| T2 | Năng lực PyTorch sinh viên | Bài tập có chấm | S1 |
| T3 | Định dạng, nhãn thời điểm ngã, ADL trong Taramasco | Tải OSF và đọc | S1 |
| T4 | License + quyền tải MM-Fi, NTU RGB+D 120, UR Fall | Trang dataset | S1 |
| T5 | FOV, NETD, tần số MLX90640; cấu hình chirp IWR6843 của Taramasco/MM-Fi | Datasheet, bài gốc | S2 |
| T6 | Số chuỗi ngã trong AMASS/HumanML3D; license Mixamo cho nghiên cứu | Tải và lọc | S2–S3 |
| T7 | RF-Genesis chạy được trên GPU trường | Thử | S2 |
| T8 | Mô hình nhiệt độ bề mặt cơ thể/quần áo | Tài liệu nhiệt học/thermography | S3 |
| T9 | Glasgow dataset: tần số, định dạng, license | Trang dataset | S19 |
| T10 | Deadline ICIP 2027, ICONIP 2027, EMBC 2027; rank ICORE2026 | Trang venue, portal ICORE | S10 |
| T11 | APC route không OA của JBHI, IoT-J, Sensors J; chính sách bài mở rộng | Trang journal | S14–S17 |
| T12 | Venue của mmFall và bài "Privacy-Preserving Fall Detection with Deep Learning on mmWave Radar Signal" | IEEE Xplore | S1 |

## Phụ lục B — Nguồn đã kiểm tra (30/09–01/10/2026)

- Zhao M. et al. (2018). Through-Wall Human Pose Estimation Using Radio Signals. CVPR. https://openaccess.thecvf.com/content_cvpr_2018/html/Zhao_Through-Wall_Human_Pose_CVPR_2018_paper.html
- Taramasco C. et al. (2025). Multimodal dataset for sensor fusion in fall detection. *PeerJ*. https://peerj.com/articles/19004/ · dữ liệu: https://doi.org/10.17605/OSF.IO/YJGDV
- Yang J. et al. (2023). MM-Fi: Multi-Modal Non-Intrusive 4D Human Dataset for Versatile Wireless Sensing. NeurIPS Datasets & Benchmarks. https://arxiv.org/abs/2305.10345 · https://ntu-aiot-lab.github.io/mm-fi
- Li C. et al. (2026). TaFall: Balance-Informed Fall Detection via Passive Thermal Sensing. arXiv:2604.09693. https://arxiv.org/html/2604.09693
- Wang et al. (2025). P2MFDS: A Privacy-Preserving Multimodal Fall Detection System for Elderly People in Bathroom Environments. arXiv:2506.17332. https://arxiv.org/abs/2506.17332
- mmFall (4D mmWave + HVRAE). Code: https://github.com/radar-lab/mmfall · Privacy-Preserving Fall Detection with Deep Learning on mmWave Radar Signal (IEEE). https://ieeexplore.ieee.org/document/8965661/
- Chen X. et al. (2023). RF Genesis: Zero-Shot Generalization of mmWave Sensing through Simulation-Based Data Synthesis and Generative Diffusion Models. SenSys. https://dx.doi.org/10.1145/3625687.3625798 · https://rfgen.xingyuchen.me/
- Xiong W. et al. (2026). HybridSim: A Physics–Learning Hybrid Digital Twin for mmWave Human Sensing. arXiv:2607.15806. https://arxiv.org/html/2607.15806
- Lai Z. et al. RadarLLM (synthetic mmWave point clouds from HumanML3D). https://arxiv.org/html/2504.09862v2
- Alamgeer S., Souissi Y., Ngu A.H.H. (2025). AI-Generated Fall Data: Assessing LLMs and Diffusion Model for Wearable Fall Detection. *Sensors*. https://www.mdpi.com/1424-8220/25/16/5144
- Synthetic LiDAR Dataset for Human Fall Detection (Blender + Mixamo), Zenodo 2026. https://zenodo.org/records/19597219
- Low-resolution infrared thermal dataset (32×24), BuildSys'21, Zenodo, CC-BY-4.0. https://zenodo.org/records/5574233
- SimHumalator (radar simulator từ motion capture). https://github.com/Shellyvishwakarma/SimHumaLator
- Fioranelli F., Shah S.A. et al. Radar signatures of human activities (University of Glasgow). https://www.semanticscholar.org/paper/Radar-signatures-of-human-activities-Fioranelli-Shah/8143537666776714f8f80931c4400c89160983c8
- UP-Fall Detection Dataset (Martínez-Villaseñor et al., *Sensors* 2019). https://www.researchgate.net/publication/332730828_UP-Fall_Detection_Dataset_A_Multimodal_Approach
- CORE: IJCNN https://portal.core.edu.au/conf-ranks/685/ · ICIP https://portal.core.edu.au/conf-ranks/654/
- IJCNN 2027 CFP https://ijcnn.org/2027/authors/call-for-papers · ICIP 2027 https://2027.ieeeicip.org/
- SJR: IEEE JBHI https://www.scimagojr.com/journalsearch.php?q=21100256982&tip=sid · IEEE IoT-J https://www.scimagojr.com/journalsearch.php?q=21100338350&tip=sid · IEEE Sensors Journal https://www.scimagojr.com/journalsearch.php?q=15047&tip=sid

Phương pháp/dataset nhắc theo tên nhưng chưa mở bài gốc trong lần kiểm tra này (cần trích dẫn chính xác khi viết): NTU RGB+D 120 (Liu et al., TPAMI 2020), UR Fall (Kwolek & Kepski 2014), ST-GCN (Yan et al., AAAI 2018), Hinton et al. 2015 (KD), FitNets (Romero et al., ICLR 2015), CRD (Tian et al., ICLR 2020), ModDrop (Neverova et al.), Learning Using Privileged Information (Vapnik & Vashist 2009), PointNet (Qi et al., CVPR 2017), SMPL (Loper et al. 2015), AMASS (Mahmood et al., ICCV 2019), HumanML3D (Guo et al., CVPR 2022), T2M-GPT (Zhang et al., CVPR 2023), MediaPipe, YOLOv8-Pose.
