# Animation Workflow Research

| Metadata | Value |
|---|---|
| Status | RESEARCH REPORT — NOT AUTHORITY |
| Research date | 2026-10-23 |
| Task | `docs/tasks/P0-research-bootstrap.md` |
| Author | ORCHESTRATOR (Claude Code) |

Báo cáo này chỉ đề xuất, không tạo decision. Giá chi tiết ở `PRODUCTION_COST_BENCHMARK.md`; Figma ở `FIGMA_INTEGRATION_ASSESSMENT.md`.

## 0. Mức độ bằng chứng

| Nhãn | Nghĩa |
|---|---|
| **[O]** | Quan sát trực tiếp trong phiên này (chạy lệnh, xem frame) |
| **[C]** | Xác nhận từ tài liệu chính thức / trang của nhà cung cấp |
| **[S]** | Nguồn thứ cấp (blog, review, aggregator); có thể lỗi thời hoặc mâu thuẫn |
| **[A]** | Giả định của ORCHESTRATOR, chưa kiểm chứng |
| **[H]** | Giả thuyết cần experiment (§9) |

Giới hạn chung: phiên này không chạy được model sinh ảnh / video nào. Laptop dev không có GPU NVIDIA và chưa có quyền dùng API trả phí. Mọi nhận định về chất lượng model là [S] hoặc [H] cho tới khi có experiment.

## 1. Video tham khảo: "Mượn thọ – Cái Kết Của Kẻ Vô Ơn – Liêu Trai Chí Dị – Mộng Hoạt Hình"

HUMAN LEAD đặt file ở root workspace. File không được commit (repo public, nội dung bên thứ ba).

### 1.1 Số đo kỹ thuật [O]

| Thuộc tính | Giá trị |
|---|---|
| Thời lượng | 434,2 s (7 phút 14 giây) |
| Video | AV1, 854×480, 30 fps (bản tải về; bản gốc có thể chất lượng cao hơn) |
| Audio | AAC 44,1 kHz stereo |
| Số cắt cảnh (`ffmpeg select='gt(scene,0.3)'`) | 138 cắt, khoảng 139 shot |
| Độ dài shot | trung bình 3,1 s; trung vị 2,8 s; ngắn nhất 0,07 s; dài nhất 14,2 s |
| Phân bố | < 2 s: 32; 2–4 s: 74; 4–6 s: 24; 6–10 s: 8; > 10 s: 1 |
| Nhịp dựng | khoảng **19 shot / phút** |

Số cắt cảnh có thể bao gồm vài transition / flash bị đếm nhầm. Bậc độ lớn (khoảng 130–140 shot cho 7 phút) vẫn đáng tin.

### 1.2 Quan sát hình ảnh [O]

Nguồn: contact sheet 48 frame (mỗi 9 s) và chuỗi frame trong cùng shot.

- **Phong cách:** 2D painterly, nét viền đậm, tô phẳng có grain, bảng màu xanh lam / đỏ / vàng ấm; bối cảnh nội thất cổ Trung Hoa chi tiết.
- **Nhân vật:** 2–4 nhân vật lặp lại (thư sinh đội mũ đen có quầng mắt, cô gái áo xanh, nữ nhân áo cam, lão nhân). Nhận diện **khá nhất quán** giữa các shot: kiểu tóc, mũ, trang phục, màu áo. Có lệch nhẹ ở chi tiết (khuôn mặt, tỉ lệ) giữa các shot.
- **Chuyển động trong shot:**
  - Nhiều shot hội thoại: nhân vật gần như đứng yên, **camera push-in chậm**, chuyển động nhỏ ở mặt / mắt. Miệng hầu như không khớp lời.
  - Một số shot có hành động thật trong shot (vd cô gái đưa túi tiền cho thư sinh: tay và thân thay đổi tư thế liên tục, nền giữ nguyên). Kiểu chuyển động này giống image-to-video AI hơn là cutout rig.
  - Có transition dissolve / overlay giữa các shot.
- **Text trên hình:** subtitle tiếng Việt burned-in trong hộp trắng bo góc. Đồng thời còn **chữ Hán in trong hình** ở một số frame (vd "30两碎银柳娘", "八个月后", "啊真的是妖是狐妖", "哈哈哈", con dấu "聊斋 石安"). Có logo nhỏ của kênh ở góc phải trên.

### 1.3 Suy luận (không phải sự thật)

- [H] Video nhiều khả năng là bản lồng tiếng / phụ đề tiếng Việt của một phim hoạt hình AI gốc Trung Quốc, vì chữ Hán và tiêu đề tiếng Trung nằm trong hình. **Không suy ra** stack phần mềm cụ thể của creator từ bề ngoài video. Theo kickoff §3, không được kết luận ở điểm này.
- [H] Dấu hiệu cho thấy pipeline "ảnh tĩnh nhất quán → image-to-video ngắn (3–5 s) → dựng theo lời kể": shot ngắn đều quanh 3 s (khớp clip i2v 5 s bị cắt), chuyển động tay / thân mềm nhưng nền ổn định, nhân vật trôi nhẹ chi tiết giữa shot.
- [A] Nếu đúng như trên, phần lớn chi phí nằm ở số lượng clip. 7 phút × 19 shot/phút ≈ 130–140 clip, tức khoảng 650–700 s video được sinh (chưa tính retry).
- **Hệ quả bản quyền:** nếu video là bản Việt hóa của tác phẩm bên thứ ba, nó **không** phải tài liệu hợp pháp để dùng làm reference sinh ảnh. Chỉ dùng để học nhịp dựng và bố cục.

### 1.4 Kênh "Mộng Hoạt Hình"

Tìm kiếm web không ra trang kênh hay bài phỏng vấn về quy trình của kênh. Kết quả cho thấy trên YouTube có nhiều video Liêu Trai tiếng Việt gắn hashtag `#HoatHinhAI`, tức thể loại "hoạt hình AI cổ trang" đang phổ biến [S]. Không có production breakdown công khai của kênh này để trích dẫn.

## 2. Bối cảnh nguồn truyện

- Liêu Trai Chí Dị (Bồ Tùng Linh, 1640–1715): nguyên tác đã thuộc phạm vi công cộng [A, theo thời hạn bảo hộ thông thường].
- **Bản dịch tiếng Việt là tác phẩm phái sinh**, có thể vẫn được bảo hộ. Luật SHTT Việt Nam: bảo hộ suốt đời tác giả + 50 năm cho tác phẩm văn học nói chung [S, luatvietnam.vn; luatminhkhue.vn]. Thời hạn với bản dịch phải xác minh trên văn bản luật gốc. Có đề xuất nâng lên 75 năm, chưa rõ đã thông qua hay chưa [S].
- Đề xuất: Story Library bắt buộc lưu trường dịch giả / nguồn bản dịch / quyền. Pilot nên dùng (a) bản dịch đã hết bảo hộ, hoặc (b) bản dịch / chuyển ngữ mới do HUMAN LEAD hoặc LLM làm từ nguyên tác Hán văn có ghi rõ, hoặc (c) truyện dân gian Việt Nam phạm vi công cộng. Đây là decision D-08.

## 3. Bốn pipeline sản xuất

### A. Traditional 2D Cutout / Puppet Animation

```text
Character design (layer PSD: đầu, thân, tay, chân, mắt, miệng A–X)
   → Rig (bone / mesh deform)  → Motion library (đi, gật, giơ tay, chớp mắt)
   → Lip-sync từ audio (viseme)  → Dàn cảnh trên nền nhiều lớp  → Render
```

- **Công cụ:**
  - Cartoon Animator 5 (Reallusion): rig 2D, auto lip-sync từ audio, Spring Dynamics, FFD. License vĩnh viễn khoảng 149 USD bản Standard; Reallusion nói phần mềm royalty-free cho output video [S].
  - Live2D Cubism: mesh deform chất lượng cao, mạnh cho mặt / tóc; miễn phí hoặc PRO cho cá nhân và doanh nghiệp nhỏ doanh thu < 10 triệu yên/năm, kể cả mục đích thương mại [C, live2d.com].
  - Blender Grease Pencil: hỗ trợ cut-out và có template 2D Animation [C, docs.blender.org]; scriptable bằng Python [S].
  - Moho, Spine, OpenToonz: chưa đánh giá chi tiết.
- **Ưu:** nhân vật tái dùng vô hạn, nhất quán tuyệt đối; render deterministic, không tốn phí mỗi shot; lip-sync được.
- **Nhược:** chi phí ban đầu cao. Mỗi nhân vật cần tách layer + rig, ước tính 1–3 ngày người / nhân vật cho người mới [A]. Chuyển động cứng nếu motion library nghèo. Góc nhìn bị giới hạn (rig 2D thường chỉ đẹp ở 1–2 góc). Tự động hóa end-to-end khó: Cartoon Animator / Live2D là GUI, API tự động hạn chế [A].
- **Hợp với:** series dài, nhân vật cố định, nhiều hội thoại.

### B. Motion Comic / Limited Animation

```text
Keyframe illustration (ảnh tĩnh, tách lớp FG / nhân vật / BG)
   → Camera move (pan / zoom / push-in) + parallax theo lớp
   → Hiệu ứng nhẹ (chớp mắt, khói, nến, mưa, ánh sáng) + transition + SFX
   → Dựng theo lời kể
```

- **Công cụ:** After Effects là chuẩn ngành cho 2.5D parallax [S, motionarray, aejuice, 80.lv]. FFmpeg làm được Ken Burns, crop / zoompan và overlay nhiều lớp dịch chuyển theo biểu thức thời gian [A, cần experiment E1]. Figma Motion làm được keyframe vị trí / scale / xoay / opacity [S].
- **Ưu:** rẻ nhất, deterministic, tự động hóa hoàn toàn bằng code; nhân vật nhất quán bằng chính ảnh đã duyệt. Phù hợp phim kể chuyện do lời dẫn dắt.
- **Nhược:** cảm giác "slideshow" nếu lạm dụng. Theo bài viết thứ cấp, YouTube coi "image slideshows / scrolling text with no meaningful narrative" là không đủ điều kiện kiếm tiền [S]. Cần có câu chuyện, lời dẫn và dựng có chủ đích. Muốn có parallax thì phải tách lớp và vá nền phía sau nhân vật.
- **Hợp với:** shot thiết lập bối cảnh, shot lời kể, shot hội thoại ít cử động. Video mẫu có nhiều shot dạng push-in gần tĩnh [O].

### C. AI Image-to-Video

```text
Character reference sheet (front / 3⁄4 / side, biểu cảm) ──┐
Style reference + Background reference ────────────────────┤
                                                           ▼
Storyboard keyframe (image edit model, nhiều ảnh tham chiếu)
   → Image-to-video 5 s (first frame / first+last frame, motion prompt)
   → Chọn take / regenerate  → Cắt 2–4 s  → Dựng
```

- **Model local (open weights):**
  - Wan 2.2 (Apache-2.0): TI2V-5B chạy 720p / 24 fps; theo nguồn thứ cấp chạy được trên GPU 24 GB, ComfyUI nói khoảng 8 GB với offloading. Bản 14B (T2V / I2V A14B) cần quantization + offloading trên 24 GB [S, nhiều nguồn mâu thuẫn]. Wan2.2-Animate-14B (character animation / replacement) open weights, Apache-2.0 [C, huggingface.co/Wan-AI]. Thời gian sinh trên RTX 3090 rất khác nhau giữa các nguồn: khoảng 1–9 phút / clip 5 s tùy độ phân giải, số bước, LoRA tăng tốc [S]. Phải đo ở E2.
  - Wan 2.6 / 3.0: API đóng; trạng thái open weights của Wan 2.7 / 3.0 mâu thuẫn giữa các nguồn [S]. Phải kiểm trực tiếp trên GitHub `Wan-Video` / Hugging Face `Wan-AI` trước khi chọn.
  - Khác: LTX-Video / LTX-2, HunyuanVideo [S]; chưa đánh giá.
- **Model premium (API / web):**
  - Kling 3.0 [S]
  - Runway Gen-4.5 [S]
  - Veo 3.1 Fast / Lite [S]
  - MiniMax Hailuo 2.3 / H3 [C cho bảng giá MiniMax]
  - Seedance 2.0 / 2.5 [S]

  Giá: xem `PRODUCTION_COST_BENCHMARK.md`.
- **Nhất quán nhân vật (khâu tạo keyframe):**
  - Local: Qwen-Image-Edit-2511, Apache-2.0 theo nguồn thứ cấp; cải thiện nhất quán nhân vật và hỗ trợ nhiều ảnh tham chiếu [S]. FLUX.1 Kontext [dev]: weights **non-commercial**, thương mại cần license trả phí [S]. LoRA nhân vật huấn luyện riêng [A].
  - Premium: Nano Banana (Gemini image) [S], Seedream, GPT Image (qua Figma Weave) [C, weave.figma.com].
- **Workflow creator phổ biến** [S, neolemon, genra, anijam; vendor blog nên có thiên lệch]:
  - Character bible / reference sheet là source of truth.
  - Dựng bộ biểu cảm 5–8 trạng thái + pose + props từ master frame.
  - Sinh ảnh tĩnh nhất quán trước, rồi mới i2v.
  - Lời dẫn (voice-over) dễ làm chất lượng hơn hội thoại nhiều.
  - Một phim 2 phút có thể cần 30–40 clip 3–5 s.
- **Ưu:** chuyển động phong phú nhất, gần video mẫu nhất; ít thao tác tay cho mỗi nhân vật mới.
- **Nhược:** chi phí và thời gian tăng theo số clip × retry. Nhân vật trôi (drift), lỗi tay / mặt, biến dạng. Không deterministic. Model đóng có điều khoản riêng và có thể đổi giá bất kỳ lúc nào. Lip-sync tiếng Việt chưa chắc chắn.

### D. Hybrid Animation

```text
                 ┌──────── Story / Script / Bible (đã duyệt) ────────┐
                 ▼                                                   ▼
        Voice + timing (TTS / ghi âm)                  Keyframe nhất quán (local edit model)
                 └───────────────► ANIMATIC (ảnh tĩnh + giọng + camera tạm) ◄┘
                                          │  HUMAN LEAD duyệt
                                          ▼
                              SHOT PRODUCTION ROUTER (từng shot)
       ┌───────────────┬──────────────────┼──────────────────┬───────────────┐
       ▼               ▼                  ▼                  ▼               ▼
 Still + camera   2D cutout / puppet  Local i2v (Wan)   Premium i2v     Import tay
 / parallax       (P2, nếu đáng)      chuyển động nhỏ   shot phức tạp   (clip ngoài)
       └───────────────┴──────────────────┴──────────────────┴───────────────┘
                                          ▼
                         Timeline (timeline.json) → FFmpeg render → Review → MP4
```

- Ý tưởng: dùng kỹ thuật rẻ nhất mà vẫn đạt chất lượng cho từng shot; chỉ nâng cấp shot cần chuyển động phức tạp.
- **Ưu:** tối ưu cả 5 mục tiêu ở kickoff; mỗi nhánh có thể thay thế độc lập (provider adapter).
- **Nhược:** phức tạp hơn khi điều phối. Phong cách giữa các nhánh phải đồng nhất: shot i2v phải dùng đúng keyframe của shot tĩnh làm frame đầu. Cần router và ledger tốt.

## 4. Đánh giá công cụ

| Công cụ | Vai trò khả dĩ | Bằng chứng chính | Đánh giá cho project |
|---|---|---|---|
| ComfyUI | Chạy workflow local (Wan, Qwen-Image-Edit) trên GPU server, gọi qua HTTP API | ComfyUI có hướng dẫn chính thức cho Qwen-Image-Edit-2511 [S/docs.comfy.org]; HTTP API `/prompt` [A]; license GPL-3.0 [A, cần kiểm] | **Nên dùng làm worker local** ở P2, gọi qua adapter. Không đưa ComfyUI vào domain trung tâm; tránh ràng buộc GPL bằng cách gọi qua process / HTTP, không import code |
| Wan 2.2 (TI2V-5B, I2V-A14B, Animate-14B) | Local i2v cho shot chuyển động nhỏ / vừa | Apache-2.0 [C/S]; VRAM và thời gian mâu thuẫn [S] | **Ứng viên local số 1**, phải benchmark E2 trên GPU server |
| Live2D Cubism | Rig mặt / tóc chất lượng cao | Miễn phí / PRO cho cá nhân < 10 triệu yên [C] | P2 evaluation; chi phí rig cao, chỉ đáng khi nhân vật lặp lại nhiều tập |
| Cartoon Animator 5 | Rig 2D + auto lip-sync | khoảng 149 USD vĩnh viễn [S]; royalty-free video [S] | P2 evaluation; Windows GUI, khó tự động hóa [A] |
| Blender Grease Pencil | Cut-out / dàn cảnh / camera scriptable | Docs chính thức [C] | Dự phòng cho parallax 3D-camera nếu FFmpeg không đủ (E1) |
| Figma Motion | Keyframe đơn giản, export MP4 / GIF / WebM / Lottie | Help Center [C]; open beta | Không đủ cho nhân vật; xem đánh giá Figma |
| Figma Weave | Canvas so sánh nhiều model ảnh / video | Pricing chính thức [C]; sản phẩm riêng, plan riêng | Sandbox so sánh provider (P3), không phải pipeline |
| Kling AI | Premium i2v, có lip-sync | Giá [S] | Ứng viên premium; xem cost benchmark |
| Runway | Premium i2v (Gen-4.5, Gen-4 Turbo) | Giá [S] | Ứng viên premium |
| Veo 3.1 / Hailuo / Seedance | Premium i2v giá / giây thấp | Giá MiniMax [C], khác [S] | Ứng viên premium, cần so sánh E6 |
| Qwen-Image-Edit-2511 | Keyframe nhất quán nhân vật, local | Apache-2.0 [S] | **Ứng viên local số 1** cho keyframe (E3) |
| VieNeu-TTS v3 Turbo | TTS tiếng Việt local, clone giọng | Apache-2.0 repo; v4 đóng, chỉ API [S/GitHub README] | Ứng viên TTS local (E4) |
| Rhubarb Lip Sync | Viseme 2D từ audio | CLI xuất JSON / TSV; 6–9 hình miệng [S]; license cần đọc LICENSE.md | P2 cho cutout; recognizer chủ yếu tiếng Anh, tiếng Việt phải thử [H] |
| FFmpeg | Render, compose, camera move, subtitle, mix audio | Đã có trên máy dev [O]; pattern sẵn ở youtube-auto-short | **Lõi renderer** |

## 5. Ma trận so sánh

Thang 1–5 (5 = tốt nhất cho project). Điểm dựa trên bằng chứng ở §3–§4 cộng giả định [A]; sẽ hiệu chỉnh sau experiment.

| Tiêu chí | A. Cutout / puppet | B. Motion comic | C. AI i2v (premium) | C'. AI i2v (local Wan) | D. Hybrid |
|---|---|---|---|---|---|
| Chất lượng hình | 3 (phụ thuộc artwork) | 3–4 (bằng keyframe) | 4–5 | 3 [H] | 4 |
| Nhất quán nhân vật | 5 | 5 (dùng ảnh đã duyệt) | 3 | 3 [H] | 4 |
| Chất lượng chuyển động | 3 | 2 | 4–5 | 3 [H] | 4 |
| Tái sử dụng | 5 | 4 (BG, layer) | 2 | 2 | 4 |
| Tự động hóa | 2 (GUI) | 5 | 4 (API) | 4 | 4 |
| Khả thi GPU local | 5 (CPU) | 5 (CPU) | n/a | 2–3 (cần 24 GB) | 4 |
| Chi phí / shot được duyệt | 5 sau khi rig | 5 | 2 | 4 (điện + thời gian) | 4 |
| Throughput | 3 | 5 | 4 | 2 (phút / clip) | 4 |
| Độ phức tạp tích hợp | 4 (khó) | 1 (dễ) | 2 | 3 | 3 |
| Ràng buộc license | thấp | thấp | điều khoản từng provider | Apache-2.0 (Wan 2.2) | hỗn hợp, quản lý được |

(Hàng "Độ phức tạp tích hợp": số cao = phức tạp hơn.)

## 6. Workflow đề xuất: "Animatic-first, motion-comic-base hybrid"

1. **Story → Script:** truyện gốc và bản cải biên lưu riêng. LLM (Ollama local) đề xuất narration, dialogue, scene / shot list có cấu trúc. HUMAN LEAD duyệt.
2. **Bible:** mỗi nhân vật có một reference sheet đã duyệt (front / 3⁄4 / side + 5–8 biểu cảm + trang phục + palette). Thêm style guide và 2–3 background master. Asset nào cũng có hash và trạng thái approval.
3. **Voice + timing trước:** TTS tiếng Việt (local, hoặc import file ghi âm) → độ dài từng câu → khung thời lượng từng shot.
4. **Storyboard keyframe:** mỗi shot một keyframe, sinh bằng image-edit model local với tham chiếu bible, hoặc import tay. Khâu này rẻ, được sinh lại nhiều lần.
5. **Animatic:** keyframe + giọng + camera move tạm + subtitle → MP4 nháp. HUMAN LEAD duyệt nhịp, độ dài, bố cục, thứ tự. **Không sinh shot đắt trước bước này.**
6. **Router từng shot** (đề xuất, HUMAN LEAD ghi đè được):
   - Mặc định **Still + camera / parallax** cho shot thiết lập, shot lời kể, shot hội thoại ít cử động. Dự kiến 60–70% số shot [A].
   - **Local i2v** cho chuyển động nhỏ / vừa: chớp mắt, tóc, vải, nến, khói, quay đầu, cử chỉ tay đơn giản. Dự kiến 20–30% [A].
   - **Premium i2v** chỉ khi đạt ngưỡng escalation (§7). Dự kiến ≤ 10–15%, tối đa 2–4 shot trong pilot.
   - **Import tay** khi HUMAN LEAD tự làm (vd bằng web UI của Kling, Figma Weave, hay After Effects).
   - **Cutout / puppet:** chưa đưa vào P1. Đánh giá ở P2 khi đã biết nhân vật nào lặp lại nhiều tập.
7. **Audio + lip-sync:** ưu tiên kể chuyện bằng lời dẫn. Video mẫu cũng hầu như không khớp miệng [O]. Hội thoại cận mặt dùng mouth-flap đơn giản hoặc chấp nhận không lip-sync ở P1. Lip-sync AI chỉ đánh giá ở P2 / P3.
8. **Timeline + FFmpeg render** 16:9, subtitle, nhạc nền, SFX, transition.
9. **Review + ledger:** mỗi take ghi provider, model, prompt, reference, tham số, chi phí, retry, approval.

Nhịp dựng: video mẫu khoảng 19 shot/phút [O]. Pilot 60–90 s với 8–12 shot cho nhịp chậm hơn nhiều (6–9 s/shot). Đề xuất pilot **12–16 shot**, trong đó vài "shot" là reframe / crop của cùng keyframe (rẻ). Cách này cho nhịp gần thể loại mà vẫn trong ngân sách. Đây là decision D-09.

## 7. Điều kiện escalate một shot lên premium

Một shot chỉ nên escalate khi **tất cả** điều kiện sau đúng:

1. Animatic đã được duyệt và shot nằm trong bản đã duyệt.
2. Shot cần chuyển động mà still / parallax / local i2v không đạt: tương tác hai nhân vật, hành động toàn thân, hiệu ứng siêu nhiên phức tạp, hoặc camera xoay quanh nhân vật.
3. Local i2v đã thử tối đa N take (đề xuất N = 3) mà HUMAN LEAD đánh giá không đạt. Hoặc shot được HUMAN LEAD đánh dấu "hero shot".
4. Ước tính chi phí của shot (giá / giây × độ dài × số retry dự kiến) nằm trong ngân sách còn lại của dự án.
5. HUMAN LEAD approve lần sinh trả phí đó (provider, model, trần chi phí, số retry tối đa).

## 8. Câu hỏi kỹ thuật còn mở

1. GPU server thực tế cho project: card nào, VRAM bao nhiêu, có dùng chung với Ollama không, có thời gian rảnh không? Tài liệu youtube-auto-short ghi có RTX 3090 (dùng chung Ollama) và RTX 3050 [O]; chưa xác nhận cho project này.
2. Wan 2.2 có giữ được phong cách 2D tô phẳng / nét viền không, hay kéo về 3D / realistic [H]?
3. Qwen-Image-Edit-2511 giữ nhận diện nhân vật 2D Á Đông qua 10–15 shot ở mức nào [H]?
4. Chất lượng TTS tiếng Việt local (VieNeu-TTS v3) đủ cho kể chuyện cổ trang chưa: giọng trầm, ngữ điệu, từ Hán-Việt [H]?
5. FFmpeg có làm parallax nhiều lớp mượt và đủ nhanh không, hay cần Blender [H]?
6. Rhubarb (hoặc recognizer phonetic) có dùng được với tiếng Việt không [H]?
7. Điều khoản thương mại của output Kling / Runway / Veo ở từng gói (free tier thường có watermark / hạn chế) [A].
8. Chính sách YouTube với kênh hoạt hình AI: mức độ biến đổi và đóng góp sáng tạo cần thiết để tránh bị xếp vào "inauthentic content" [S].
9. Nguồn truyện pilot và quyền của bản dịch.

## 9. Experiment cần chạy trước khi duyệt architecture chi tiết

Không experiment nào tốn tiền trừ khi ghi rõ. Mỗi experiment cần HUMAN LEAD cho phép chạy.

| ID | Experiment | Câu hỏi | Môi trường | Chi phí | Kết quả cần |
|---|---|---|---|---|---|
| E1 | Camera move + parallax 2–3 lớp bằng FFmpeg trên 3 ảnh mẫu hợp pháp | Mượt, nhanh, đủ chất lượng? | Laptop dev | 0 | 3 clip 5 s; thời gian render; nhận xét HUMAN LEAD |
| E2 | Wan 2.2 TI2V-5B và I2V-A14B (quantized) trên GPU server, 5 keyframe 2D | Thời gian / clip, VRAM, giữ style, tỉ lệ take dùng được | GPU server | điện | bảng thời gian, VRAM, 5×3 take, chấm điểm |
| E3 | Nhất quán nhân vật: Qwen-Image-Edit-2511 (local) so với 1 model premium qua free tier / Weave free (nếu được duyệt) | Giữ nhận diện qua 10 pose / biểu cảm? | GPU server (+ free tier) | 0 | lưới 10 ảnh / model; chấm điểm |
| E4 | TTS tiếng Việt: VieNeu-TTS v3 local so với 1–2 dịch vụ (free tier) | Dễ hiểu, tự nhiên, Hán-Việt | Laptop / server | 0 | 3 đoạn 30 s; HUMAN LEAD nghe chấm |
| E5 | Lip-sync tối thiểu: Rhubarb (phonetic) + 6 sprite miệng trên 1 shot | Có đáng làm ở P2? | Laptop | 0 | 1 clip; nhận xét |
| E6 | Premium i2v: 2 shot giống nhau trên 2–3 provider (dùng free credit) | Chất lượng / giá thực tế / retry | Web UI free tier | 0 nếu chỉ free credit; cần approval đăng ký tài khoản | 2×3 take mỗi provider |
| E7 | Cutout: rig 1 nhân vật trong Cartoon Animator trial hoặc Live2D free | Thời gian rig, chất lượng, tự động hóa | Windows | 0 (trial) | số giờ, clip 10 s |
| E8 | Figma Motion: 1 shot pan / zoom + export MP4 | Có gì hơn FFmpeg? | Figma Education | 0 | clip + nhận xét |

E1, E4 và E5 chạy được ngay trên laptop. E2 và E3 cần GPU server. E6 và E7 cần HUMAN LEAD cho phép đăng ký tài khoản / trial.

## 10. Nguồn

Truy cập ngày 2026-10-23.

- Wan 2.2 / VRAM / thời gian: [stable-diffusion-art](https://stable-diffusion-art.com/?p=18624), [techenclave](https://techenclave.com/t/workstation-for-wan-2-2-14b-comfyui-dual-3090s-vs-single-4090/412799), [hivenet](https://www.hivenet.com/post/wan-2-2-cloud-gpu-comfyui), [runpod guide](https://www.runpod.io/articles/guides/comfyui-wan-2-2), [localaimaster](https://localaimaster.com/blog/wan-video-generation-guide), [runaihome](https://runaihome.com/blog/wan-video-local-ai-gpu-guide-2026/)
- Wan release / license: [fuser.studio](https://fuser.studio/articles/best-open-source-video-models), [imagera.ai](https://imagera.ai/blog/is-wan-3-0-real-what-alibaba-shipped-2026), [wan27.org](https://wan27.org/blog/wan-2-7-open-source-guide), [Wan-AI/Wan2.2-Animate-14B-Diffusers](https://huggingface.co/Wan-AI/Wan2.2-Animate-14B-Diffusers/tree/main)
- Qwen-Image-Edit: [huggingface qwen-image-edit-2511](https://huggingface.co/qwen/qwen-image-edit-2511), [docs.comfy.org](https://docs.comfy.org/tutorials/image/qwen/qwen-image-edit-2511), [vast.ai](https://vast.ai/model/qwen-image-edit)
- FLUX Kontext license: [rits.shanghai.nyu.edu](https://rits.shanghai.nyu.edu/ai/flux-1-kontext-dev-released-open-weights-model-for-advanced-image-editing/), [runware](https://runware.ai/models/bfl-flux-1-kontext-dev)
- Live2D: [help.live2d.com](https://help.live2d.com/en/?p=2172), [live2d.com](https://www.live2d.com/en/?p=607)
- Cartoon Animator: [fitgap](https://us.fitgap.com/products/009147/cartoon-animator), [digitalproduction](https://digitalproduction.com/2022/11/23/cartoon-animator-5-cta5/), [Reallusion commercial rights](https://discussions.reallusion.com/t/commercial-rights/14208)
- Blender Grease Pencil: [docs.blender.org](https://docs.blender.org/manual/en/dev/grease_pencil/introduction.html)
- Motion comic / parallax: [motionarray](https://blog.motionarray.com/learn/after-effects/animate-flat-2d-images-after-effects/), [aejuice](https://aejuice.com/blog/how-to-create-parallax-effect-in-after-effects), [80.lv](https://80.lv/articles/inside-the-making-of-2-5d-parallax-animation-for-music-artist), [petapixel](https://petapixel.com/2013/11/19/creating-motion-stills-animate-photo-post-parallax-effect)
- Workflow creator AI: [neolemon pipeline](https://www.neolemon.com/blog/ai-storyboard-to-animation-pipeline-workflow/), [genra](https://genra.ai/blog/how-to-create-ai-animated-stories-guide), [anijam](https://www.anijam.ai/blog/how-to-make-ai-story-video/)
- TTS: [VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS)
- Lip-sync: [rhubarb (ecosystem)](https://awesome.ecosyste.ms/projects/github.com%2Fdanielswolf%2Frhubarb-lip-sync), [lip-sync-engine](https://www.jsdelivr.com/package/npm/lip-sync-engine)
- YouTube AI / inauthentic content: [vidiq](https://vidiq.com/blog/post/youtube-ai-monetization/), [layer3labs](https://www.layer3labs.io/guides/youtube-ai-content-policy), [tubebuddy](https://www.tubebuddy.com/blog/youtube-ai-monetization-best-practices/). Phải đối chiếu YouTube Help Center trước khi đăng.
- Bản quyền VN: [luatvietnam](https://luatvietnam.vn/tin-phap-luat/thoi-han-bao-ho-quyen-so-huu-tri-tue-230-30744-article.html), [luatminhkhue](https://luatminhkhue.vn/tu-dich-sach-roi-dang-mien-phi-tren-mang-co-vi-pham-ban-quyen.aspx), [baophapluat](https://baophapluat.vn/de-nghi-bao-ho-tac-quyen-den-75-nam-post54202.html)
- Video Liêu Trai AI tiếng Việt trên YouTube: [Họa Nữ](https://www.youtube.com/watch?v=jRrEopHBOXo), [Tỷ Muội Dịch Giá](https://www.youtube.com/watch?v=iWwZt0PDuSI)
