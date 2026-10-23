# Production Cost Benchmark

| Metadata | Value |
|---|---|
| Status | RESEARCH REPORT — NOT AUTHORITY |
| Research date | 2026-10-23 |
| Task | `docs/tasks/P0-research-bootstrap.md` |

Nhãn bằng chứng: xem `ANIMATION_WORKFLOW_RESEARCH.md` §0. **Không có lần sinh trả phí nào được chạy.** Mọi giá lấy từ trang công khai hoặc nguồn thứ cấp tại ngày nghiên cứu; giá AI video thay đổi theo tháng, phải kiểm lại trước khi chi. Ngân sách thử nghiệm mục tiêu 30–60 USD/tháng chỉ là mục tiêu, **không phải authorization chi tiêu**.

## 1. Phần cứng

| Máy | Thông tin | Nguồn | Vai trò |
|---|---|---|---|
| Laptop dev (máy đang dùng) | Intel Core i5-1135G7 (4 nhân), Intel Iris Xe, 16 GB RAM, Windows 11 + WSL | [O] | Dev, test, FFmpeg render 2D, TTS CPU. **Không** chạy được i2v local |
| GPU node "RTX 3090" | 24 GB VRAM; dùng chung với Ollama (`qwen3:30b` / `qwen3:14b`) của youtube-auto-short | [O] tài liệu youtube-auto-short (`docs/guides/enhance-worker-windows.md`, CP1 §11) | Ứng viên i2v local / image-edit local. **Chưa xác nhận cho project này** |
| GPU node "RTX 3050" | VRAM không ghi (thường 8 GB bản desktop) | [O] tài liệu; VRAM [A] | Đủ cho TTS / image model nhỏ; không đủ cho Wan 14B [A] |
| VM server | nhiều CPU (tài liệu ghi `-n auto` = 24 CPU; Whisper CPU 48 nhân) | [O] tài liệu | Renderer FFmpeg, web UI, orchestration |

HUMAN LEAD cho biết sẽ đưa project lên server sau (2026-10-23). Decision D-07: xác nhận GPU nào dùng được cho project, lịch dùng chung với Ollama / enhance worker.

## 2. Bảng giá (đơn vị USD)

### 2.1 Premium image-to-video

| Provider / model | Hình thức | Giá | Nguồn |
|---|---|---|---|
| Kling 3.0 | API trả trước | 0,084/s (720p, không audio); 0,112/s (1080p); 4K 0,42/s | [S] cloudzero, shhots |
| Kling (web) | Subscription | Standard khoảng 7–10/tháng, 660 credit; 720p khoảng 6 credit/s → khoảng 110 s/tháng; free khoảng 66 credit/ngày | [S] nhiều nguồn mâu thuẫn |
| Runway Gen-4.5 | API | 0,12/s (12 credit/s; 1 credit API = 0,01) | [S] |
| Runway Gen-4 Turbo | API | 0,05/s | [S] |
| Runway (web) | Subscription | Standard 15/tháng (625 credit, khoảng 52 s Gen-4.5); Pro 35 (2.250 credit) | [S] |
| Veo 3.1 Fast | Gemini API | 0,10/s 720p, 0,12/s 1080p (có audio) | [S] benchlm |
| Veo 3.1 Lite | Gemini API | 0,05/s 720p | [S] |
| Hailuo 2.3 Fast | MiniMax API | 0,19 / clip 768p 6 s (khoảng 0,032/s) | [S] theo trích dẫn bảng giá platform.minimax.io |
| Hailuo 2.3 | MiniMax API | 0,28 / clip 768p 6 s | [S] |
| Seedance 2.0 / Fast / Mini | BytePlus API | 0,15 / 0,12 / 0,08 mỗi giây ở 720p | [S] |
| Figma Weave | Credit đa model | Free 150 credit; Starter 24/tháng 1.500 credit; một lượt video 2–857 credit tùy model | [C] weave.figma.com |

### 2.2 Ảnh (keyframe, character sheet)

| Lựa chọn | Giá | Nguồn |
|---|---|---|
| Qwen-Image-Edit-2511 local | 0 (điện + thời gian GPU) | [S] license Apache-2.0 |
| Nano Banana 2.1 (Gemini API) | khoảng 0,034 (1K) – 0,076 (4K) / ảnh; batch khoảng 50% | [S] mâu thuẫn |
| Nano Banana Pro | 0,134 / ảnh 1K–2K | [S] |
| FLUX.1 Kontext [dev] hosted | khoảng 0,0105 / ảnh 1024² | [S] runware |

### 2.3 Giọng nói, phần mềm, chi phí local

| Hạng mục | Chi phí | Ghi chú |
|---|---|---|
| VieNeu-TTS v3 Turbo local | 0 | [S] Apache-2.0; v4 chỉ API |
| TTS trả phí (ElevenLabs, Google, FPT.AI…) | **chưa nghiên cứu giá** | để E4 quyết có cần không |
| Cartoon Animator 5 | khoảng 149 một lần | [S] |
| Live2D Cubism | 0 cho cá nhân / doanh nghiệp < 10 triệu yên doanh thu | [C] |
| Điện cho i2v local | khoảng 0,35 kW × 5 phút ≈ 0,03 kWh/clip ≈ < 0,01 USD/clip | [A] giá điện khoảng 3.000 VND/kWh; thời gian clip [S] |

Chi phí thật của local là **thời gian GPU và tranh chấp với Ollama**, không phải tiền điện.

## 3. Giả định mô hình chi phí

| Tham số | Giá trị | Nhãn |
|---|---|---|
| Độ dài clip sinh / shot | 5 s (cắt còn 2–5 s) | [A] |
| Số take / shot được duyệt (premium) | 3 (tỉ lệ đạt khoảng 33%) | [A] — đo ở E6 |
| Số take / shot được duyệt (local i2v) | 4 | [A] — đo ở E2 |
| Thời gian một clip local 5 s | 5 phút (khoảng 1–9 phút theo nguồn) | [S]/[A] — đo ở E2 |
| Nhịp dựng | 12 shot/phút (pilot) — 19 shot/phút (thể loại, video mẫu) | [A] / [O] |
| Tỉ lệ router hybrid | 65% still / parallax, 25% local i2v, 10% premium | [A] |

Chi phí / shot được duyệt = giá/s × 5 s × số take.

| Provider | USD / shot premium được duyệt |
|---|---|
| Hailuo 2.3 Fast (768p) | khoảng 0,57 |
| Veo 3.1 Lite (720p) | khoảng 0,75 |
| Runway Gen-4 Turbo | khoảng 0,75 |
| Kling 3.0 (720p) | khoảng 1,26 |
| Veo 3.1 Fast (720p) | khoảng 1,50 |
| Runway Gen-4.5 | khoảng 1,80 |
| Seedance 2.0 (720p) | khoảng 2,25 |

## 4. So sánh kịch bản (một phút phim hoàn chỉnh, nhịp 12 shot/phút)

| Kịch bản | Tiền mặt / phút | GPU local / phút | Công người / phút [A] | Rủi ro chính |
|---|---|---|---|---|
| **All-premium** (Kling 3.0 720p) | khoảng 15 (Hailuo Fast: khoảng 7) | 0 | 1–1,5 h (chọn take, prompt) | Chi phí tăng tuyến tính; drift nhân vật; phụ thuộc provider |
| **All-local** (Wan 2.2 trên 3090) | khoảng 0 | 12 × 4 × 5 phút ≈ **4 h** | 1,5–2 h | Thời gian GPU; style 2D chưa chắc; tranh chấp Ollama |
| **Hybrid** (65 / 25 / 10) | 1,2 shot × 1,26 ≈ **1,5** | 3 × 4 × 5 ≈ **1 h** | 1–1,5 h | Điều phối; đồng bộ style giữa nhánh |
| **Reusable 2D cutout** | khoảng 0 (sau 149 nếu CTA) | 0 | đầu tư 1–3 ngày / nhân vật, sau đó 0,5–1 h / phút | Chi phí rig ban đầu; chuyển động cứng |
| Motion comic thuần (still + camera) | 0 | 0 (CPU) | 0,5–1 h | Cảm giác slideshow; rủi ro chính sách YouTube nếu thiếu tính sáng tạo |

Keyframe ảnh thêm khoảng 0 (local) hoặc khoảng 1–2 USD/phút (premium, khoảng 3 ảnh / shot × 0,05).

Nhịp thể loại 19 shot/phút làm các con số trên tăng khoảng 1,6×. Phim 10 phút hybrid: khoảng 15–25 USD tiền mặt và khoảng 10–16 giờ GPU [A].

Thời gian tiết kiệm nhờ tái sử dụng nhân vật / bối cảnh:
- Background master dùng lại cho mọi shot cùng bối cảnh: phần lớn shot không cần sinh BG mới.
- Character sheet đã duyệt giảm retry keyframe.
- Không đo được ở P0. Phải ghi trong ledger P1 (số lần sinh / asset được tái dùng).

## 5. Ước tính chi phí pilot (60–90 s)

Pilot: 12–16 shot; khoảng 9–10 still / parallax, khoảng 3 local i2v, 2–4 premium.

| Hạng mục | Thấp | Cao | Ghi chú |
|---|---|---|---|
| Premium i2v (2–4 shot × 3 take × 5 s) | 0 (chỉ free credit) | khoảng 7 (Kling 3.0 API) | Hoặc 1 tháng subscription khoảng 10–15 |
| Keyframe premium (nếu local không đạt) | 0 | khoảng 8 (khoảng 120 ảnh × 0,067) | |
| TTS | 0 | 0 | local / ghi âm |
| Phần mềm | 0 | 0 | không mua CTA ở pilot |
| **Tổng tiền mặt** | **0** | **khoảng 15–25** | Trong khung 30–60 USD/tháng |
| GPU local | khoảng 1–2 h | khoảng 5 h | phụ thuộc E2 |
| Công HUMAN LEAD | khoảng 4 h | khoảng 10 h | duyệt truyện, bible, animatic, shot |

**Bất định lớn nhất:**
1. GPU server có dùng được không; Wan 2.2 có giữ style 2D không. Nếu không, phải chuyển nhiều shot sang premium và chi phí tăng khoảng 3–5×.
2. Tỉ lệ take đạt thực tế.
3. Điều khoản thương mại / watermark của free tier.

## 6. Phân biệt hình thức chi trả

| Hình thức | Đặc điểm | Rủi ro |
|---|---|---|
| Subscription web UI | Credit tháng, thường không cộng dồn; thao tác tay; không tự động hóa | Credit bỏ phí; điều khoản thương mại theo gói |
| Credit web UI (top-up) | Trả theo lượng | Giá credit / model thay đổi |
| API billing | Trả theo giây / clip; tự động hóa được; trả trước | Phải có budget guard để tránh chạy vượt |
| Free trial / free tier | 0 USD | Watermark, giới hạn thương mại, hàng đợi chậm; đăng ký tài khoản vẫn cần HUMAN LEAD duyệt |
| Local inference | 0 tiền theo lượt | Thời gian GPU; vận hành; license model (Apache-2.0 ổn; FLUX dev non-commercial) |

## 7. Khuyến nghị

- **Rẻ nhất chấp nhận được:** motion comic (still + camera / parallax bằng FFmpeg) cho mọi shot, keyframe từ Qwen-Image-Edit local, TTS local. Tiền mặt 0 USD. Chất lượng chuyển động thấp nhất.
- **Chất lượng cao nhất thực tế:** keyframe premium (Nano Banana / Seedream) cộng premium i2v (Kling 3.0 / Veo 3.1 Fast / Runway Gen-4.5) cho đa số shot. Chi phí khoảng 15–25 USD/phút. Phải kiểm drift nhân vật.
- **Cân bằng (khuyến nghị):** hybrid 65 / 25 / 10. Escalate theo `ANIMATION_WORKFLOW_RESEARCH.md` §7. Pilot khoảng 0–25 USD. Sản xuất khoảng 1,5–3 USD/phút cộng GPU local.
- **Provider premium đầu tiên để thử (P3):** chưa chọn. Đề xuất so sánh Kling 3.0, Hailuo 2.3 và Veo 3.1 Lite / Fast trên cùng 2 shot (E6). Nếu chọn sớm vì đã có cả web subscription lẫn API rẻ ở 720p, Kling là ứng viên [S], nhưng chỉ chốt sau E6.
- **Safeguard bắt buộc khi có paid adapter:**
  - Trần chi phí theo project và theo tháng.
  - Ước tính trước mỗi lần chạy.
  - Approval từng lần sinh trả phí.
  - `max_retries` mỗi shot.
  - Không retry tự động khi lỗi chất lượng.
  - Ledger ghi chi phí ước tính và thực tế.

## 8. Nguồn

Truy cập ngày 2026-10-23.

- Kling: [cloudzero](https://www.cloudzero.com/blog/kling-ai-pricing/), [shhots](https://shhots.ai/blog/kling-ai-pricing/), [aitoolanalysis](https://aitoolanalysis.com/kling-ai-pricing/), [heygen](https://www.heygen.com/blog/kling-ai-pricing)
- Runway: [eesel](https://www.eesel.ai/blog/runway-ai-pricing), [stacksheriff](https://stacksheriff.com/ai-tools/runway-pricing/), [camclo3d](https://camclo3d.com/blog/runway-pricing)
- Veo: [benchlm](https://benchlm.ai/media-pricing/veo), [cloudzero](https://www.cloudzero.com/blog/veo-3-pricing/), [veopricing](https://www.veopricing.com/veo-3-1-api-providers/)
- MiniMax Hailuo: [MiniMax pricing docs](https://platform.minimax.io/docs/guides/pricing-video), [magichour](https://magichour.ai/blog/hailuo-23-pricing)
- Seedance: [openrouter](https://openrouter.ai/bytedance/seedance-2.5), [atlascloud](https://www.atlascloud.ai/blog/case-studies/seedance-2.0-pricing-full-cost-breakdown-2026), [apimodels](https://apimodels.app/access/seedance-api-pricing)
- Gemini image: [developersdigest](https://www.developersdigest.tech/models/image-generation/google-gemini-api), [benchlm nano-banana](https://benchlm.ai/media-pricing/nano-banana)
- Figma Weave: [weave.figma.com/pricing](https://weave.figma.com/pricing)
- Wan thời gian: [runpod](https://www.runpod.io/articles/guides/comfyui-wan-2-2), [localaimaster](https://localaimaster.com/blog/local-ai-video-generation)
- Live2D: [help.live2d.com](https://help.live2d.com/en/?p=2172); Cartoon Animator: [fitgap](https://us.fitgap.com/products/009147/cartoon-animator)
- Phần cứng GPU node: tài liệu `ntnghia1908/youtube-auto-short` @ `a94995a` (`docs/guides/enhance-worker-windows.md`, `docs/decisions/CP1-product-contract.md` §11)
