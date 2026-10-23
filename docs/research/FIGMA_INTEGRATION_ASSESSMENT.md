# Figma Integration Assessment

| Metadata | Value |
|---|---|
| Status | RESEARCH REPORT — NOT AUTHORITY |
| Research date | 2026-10-23 |
| Task | `docs/tasks/P0-research-bootstrap.md` |

Nhãn bằng chứng giống `ANIMATION_WORKFLOW_RESEARCH.md` §0: [O] quan sát, [C] nguồn chính thức, [S] nguồn thứ cấp, [A] giả định, [H] giả thuyết. Phiên này **không đăng nhập** tài khoản Figma Education của HUMAN LEAD, nên mọi entitlement của chính tài khoản đó đều chưa được kiểm chứng.

## 1. Kết luận ngắn

- **Figma Education không phải nền tảng sản xuất cho kênh YouTube công khai / có kiếm tiền.** Help Center coi "using EDU licenses commercially" là lạm dụng [C]. Nếu kênh bật kiếm tiền, việc dùng Education để tạo asset sản xuất là rủi ro license. Câu hỏi "kênh YouTube có quảng cáo có tính là commercial không" phải để HUMAN LEAD quyết, tốt nhất sau khi hỏi Figma.
- **Hữu ích thật** cho việc nội bộ, không sinh doanh thu: prototype UI Review Studio, sơ đồ workflow, story map trên FigJam, bố cục thử character sheet / storyboard.
- **Figma Motion không đủ cho animation nhân vật.** Chỉ keyframe vị trí, scale, xoay, opacity (+ shader); không có bone hay mesh deform; không có API tự động export [C/S]. FFmpeg làm được camera move tương đương mà tự động hóa được.
- **Figma Weave là sản phẩm và gói riêng, không nằm trong Education.** Theo FAQ: "Because Figma and Figma Weave are currently separate products, they require individual plans." [C] Có gói Free 150 credit/tháng kèm "Commercial license" [C]. Hữu ích như sandbox so sánh nhiều model trước khi chọn provider (P3).
- **Khuyến nghị:** **không đưa Figma vào pipeline P1.** Cho phép dùng Figma Design / FigJam như công cụ thiết kế nội bộ tùy chọn (P1+). Asset đi vào Studio qua PNG / SVG / JSON import tay. Cân nhắc Weave Free / Starter ở P3 cho experiment E3 / E6 nếu HUMAN LEAD duyệt.

## 2. Entitlement: đã xác nhận và chưa xác nhận

| Mục | Trạng thái | Chi tiết |
|---|---|---|
| Education plan tương đương Professional (higher-ed) | [C] | Higher-ed / bootcamp / high school nhận gói Professional; K-12 nhận Enterprise qua trường |
| AI credits | [C] | 3.000 credit/người/tháng; reset hằng tháng, không cộng dồn, không chia sẻ |
| AI tools (Figma Make, agent trong Figma Design) | [C] | Chỉ cho higher-ed và bootcamp |
| Figma Sites | [C] | 1 site, không custom domain |
| Thời hạn | [C] | 1 năm cho sinh viên, 2 năm cho giảng viên; hết hạn phải xác minh lại; hết hạn thì team bị hạ xuống Starter, team có ≥ 4 file bị khóa |
| Thương mại | [C, gián tiếp] | Misuse gồm "using EDU licenses commercially"; bootcamp yêu cầu rõ "not used for client work, agency folders, or revenue generation". Không thấy điều khoản riêng cho kênh YouTube |
| Figma Motion | [C] | Open beta; "available on any plan"; export MP4 / WebM / GIF / SVG / Lottie (JSON, dotLottie); free plan giới hạn ≤ 1920×1080 và ≤ 30 fps; plan trả phí cao hơn |
| Figma Motion trên Education | [A] | Education = Professional nên khả năng cao có đủ quyền như paid; **chưa kiểm trên tài khoản thật** |
| Motion: AI sinh keyframe, publish animated component, export độ phân giải cao | [S] | Một số nguồn nói cần Full seat trả phí; chưa xác nhận với Education |
| Figma Weave | [C] | Plan riêng: Free 0 USD / 150 credit; Starter 24 USD / 1.500; Professional 45 USD / 4.000; Max 100 USD / 10.000; Team 42 USD/người / 4.500. Top-up 10 USD / 1.000–1.200 credit. Không có ưu đãi Education |
| Weave dùng AI credits của Education? | [C, phủ định] | Hai sản phẩm cần plan riêng |
| Thương mại trên Weave | [C] | Platform "provides full commercial rights"; "most models … cleared for commercial use"; từng model xem Trust Center |
| API / automation | [A] | Figma REST API export được node thành PNG / SVG / PDF (đã biết từ trước, phải kiểm lại). Help Center không nêu API export animation. Không có automation cho Motion |

## 3. Đánh giá từng sản phẩm

### Figma Design

| Use case | Giá trị | Ghi chú |
|---|---|---|
| Character reference sheet / Character Bible | Trung bình | Bố cục tốt, component cho biểu cảm. Ảnh nhân vật vẫn sinh ở nơi khác; Figma chỉ là bàn trình bày |
| Thư viện style / environment | Trung bình | Thay được bằng thư mục asset + trang review của Studio |
| Storyboard layout | Trung bình | Animatic của Studio có giá trị hơn vì có giọng và timing |
| Review / collaboration | Thấp với project 1 người | Hữu ích nếu sau này có cộng tác viên |
| Prototype UI Review Studio | **Cao** | Không sinh doanh thu → phù hợp Education |

### FigJam

Story map, scene planning, sơ đồ workflow: **hữu ích, rủi ro thấp**. Đây là công việc lập kế hoạch nội bộ. Không cần tích hợp kỹ thuật.

### Figma Motion

- **Có:** timeline, keyframe position / scale / rotation / opacity, preset, motion variables, animated components, export MP4 / WebM / GIF / Lottie [C/S].
- **Không có (theo tài liệu tìm được):** bone rig, mesh deform, lip-sync, puppet; API export tự động [S/A].
- **Đánh giá:**
  - Không phù hợp cho animation nhân vật.
  - Làm được camera move / parallax đơn giản cho một shot, nhưng phải thao tác tay từng shot, không tự động hóa.
  - Có thể dùng cho motion graphics phụ: tiêu đề, intro / outro, khung chữ.
  - Experiment E8 chỉ cần nếu HUMAN LEAD muốn làm intro / outro bằng Figma.

### Figma Weave

- Canvas node-based, kết nối nhiều model ảnh / video (Google, OpenAI, Runway, Luma, ByteDance, BFL, Kling…) [S]. Bảng giá chính thức liệt kê GPT Image, Flux, Ideogram, Seedream, Nano Banana, Topaz, Seedance [C].
- **Giảm độ phức tạp so sánh provider:** có, ở giai đoạn thử nghiệm. Một tài khoản dùng được nhiều model, không phải đăng ký từng nơi.
- **Không giảm độ phức tạp khi tự động hóa:** không thấy API công khai để gọi workflow từ Studio [A]. Credit tính theo model và chênh lệch lớn (bảng giá ghi một lượt video tốn 2–857 credit) [S].
- **Vai trò đề xuất:** sandbox cho E3 / E6 ở P3; output tải về và đưa vào Studio qua "Import tay" (M6 phương thức 5) kèm ghi provider / model / credit vào ledger.

## 4. Ràng buộc thiết kế

- Studio **không phụ thuộc** Figma. Không có code gọi Figma API trong P1.
- Định dạng trao đổi chuẩn: PNG / SVG (ảnh, layer), JSON (metadata, Lottie nếu cần), MP4 / WebM (clip).
- Asset nào đến từ Figma / Weave cũng phải ghi nguồn công cụ và license / plan lúc tạo vào asset metadata (M10).

## 5. Pilot experiment cho Figma (tùy chọn, không chặn P1)

| ID | Nội dung | Điều kiện |
|---|---|---|
| F1 | Kiểm tài khoản Education thật: Motion có bật không, giới hạn export, số AI credit còn | HUMAN LEAD tự kiểm (5 phút) |
| F2 | Prototype 3 màn hình Review Studio (project overview, storyboard / animatic, shot review) | Việc nội bộ, phù hợp Education |
| F3 (= E8) | 1 shot pan / zoom bằng Motion, export MP4, so với FFmpeg | Tùy chọn |
| F4 | Weave Free: thử nhất quán nhân vật (E3) và 1 shot i2v (E6) bằng 150 credit miễn phí | HUMAN LEAD duyệt tạo tài khoản; 0 USD |

## 6. Khuyến nghị theo phase

| Phase | Dùng Figma? |
|---|---|
| P1 | Không trong pipeline. Tùy chọn: FigJam / Design cho planning và prototype UI nội bộ |
| P2 | Không bắt buộc |
| P3 | Weave như sandbox so sánh provider, nếu được duyệt; output nhập tay |
| P4+ | Xem lại nếu có cộng tác viên hoặc HUMAN LEAD mua plan thương mại |

## 7. Decision cần HUMAN LEAD

- D-10: Có dùng tài khoản Education cho bất kỳ asset nào xuất hiện trong video công khai không? Khuyến nghị: **không**, cho tới khi xác nhận với Figma hoặc dùng plan trả phí.
- Có tạo tài khoản Weave Free cho experiment không (P3)?

## 8. Nguồn

Truy cập ngày 2026-10-23.

- [Figma for Education (Help Center)](https://help.figma.com/hc/en-us/articles/360041061214-Figma-for-Education)
- [AI credits on the Education plan (Help Center)](https://help.figma.com/hc/en-us/articles/37611757713431-AI-credits-on-the-Education-plan)
- [Export animations from Figma (Help Center)](https://help.figma.com/hc/en-us/articles/41307983648407-Export-animations-from-Figma)
- [Figma Motion product page](https://www.figma.com/motion/)
- [Figma Weave pricing](https://weave.figma.com/pricing)
- [Figma Weave subscription plans (help.weavy.ai)](https://help.weavy.ai/en/articles/12267070-figma-weave-s-subscription-plans)
- Thứ cấp: [daily.dev Motion launch](https://daily.dev/posts/introducing-figma-motion-your-canvas-now-has-a-timeline-iqkjsl2la), [Motion guide (medium)](https://medium.com/@emilyharbord2/figma-finally-added-native-motion-design-a-full-guide-to-figma-motion-c63725675289), [LottieFiles Figma Motion](https://lottiefiles.com/plugins/figma/figma-motion), [scopeful Weave](https://www.scopeful.org/tools/figma-weave), [chasejarvis Weavy review](https://chasejarvis.com/blog/what-the-heck-is-weavy-the-100-honest-review-after-the-figma-acqusition/), [Figma forum: Education for commercial](https://forum.figma.com/t/figma-education-for-commercial/32185)
