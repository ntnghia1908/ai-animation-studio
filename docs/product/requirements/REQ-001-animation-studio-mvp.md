---
id: REQ-001
title: "AI Animation Studio MVP — pilot 60–90 s animated story"
status: NEEDS_CLARIFICATION
version: 1
owner: "HUMAN LEAD"
created: 2026-10-23
updated: 2026-10-23
---

# Requirement: REQ-001 — AI Animation Studio MVP

Soạn bởi ORCHESTRATOR từ kickoff của HUMAN LEAD (2026-10-23) và kết quả nghiên cứu P0 (`docs/research/`). Status `NEEDS_CLARIFICATION`: requirement chưa READY và không authorize implementation.

## 1. Problem

HUMAN LEAD muốn sản xuất phim hoạt hình 2D kể chuyện bằng tiếng Việt từ truyện có sẵn (Liêu Trai, dân gian; sau này truyện nhân quả / Phật giáo). Hiện chưa có quy trình hay công cụ nào. Làm thủ công một phim tốn nhiều giờ phối hợp nhiều công cụ rời rạc: viết lại truyện, giữ nhân vật nhất quán, lồng tiếng, dựng.

Các công cụ AI video tính phí theo lượt sinh. Nếu sinh shot đắt trước khi chốt nhịp truyện, tiền và công sẽ bị lãng phí. Ngoài ra, không có cách nào truy được mỗi shot đến từ đâu, tốn bao nhiêu và đã được duyệt hay chưa.

## 2. Goal

HUMAN LEAD làm ra được một phim hoạt hình 2D tiếng Việt dài 60–90 giây từ một truyện có sẵn, với những tính chất sau:

- Nhân vật và phong cách nhất quán.
- Nhịp kể tự nhiên.
- Duyệt được từng giai đoạn.
- Tái tạo được kết quả.
- Mọi chi phí sinh nội dung được ghi lại.
- Không phát sinh chi phí ngoài ý muốn.

## 3. Actors

| Actor | Role / need |
|---|---|
| HUMAN LEAD | Chọn truyện, duyệt nội dung / bible / animatic / shot / bản cuối, quyết chi tiêu; cần ít thao tác lặp |
| Studio (hệ thống) | Lưu truyện và cải biên, đề xuất kịch bản / shot, dựng animatic và bản cuối, ghi chi phí |
| Nhà cung cấp AI (local / trả phí) | Sinh văn bản, giọng, ảnh, video theo yêu cầu |
| Người xem YouTube (gián tiếp) | Xem phim 16:9 tiếng Việt, hiểu được lời thoại |

## 4. Current workflow / context

Chưa có. HUMAN LEAD đã có hạ tầng từ project khác:
- máy GPU chạy Ollama;
- kinh nghiệm FFmpeg pipeline và web review trong LAN (`ntnghia1908/youtube-auto-short`);
- tài khoản Figma Education.

Video tham khảo về phong cách và nhịp: "Mượn thọ – Mộng Hoạt Hình" (`docs/research/ANIMATION_WORKFLOW_RESEARCH.md` §1).

## 5. Desired workflow / outcome

1. HUMAN LEAD nhập truyện (TXT / Markdown / dán text) kèm nguồn, tác giả, dịch giả, quyền sử dụng.
2. Studio đề xuất bản cải biên: lời dẫn, thoại, scene, shot list, mô tả nhân vật. HUMAN LEAD sửa và duyệt. Truyện gốc giữ nguyên.
3. HUMAN LEAD lập / duyệt Character & Visual Bible: nhân vật, trang phục, biểu cảm, bảng màu, bối cảnh, phong cách.
4. Studio tạo giọng tiếng Việt (hoặc HUMAN LEAD nhập file ghi âm) và tính thời lượng từng shot.
5. Studio tạo hoặc nhận storyboard (mỗi shot một khung hình), rồi dựng animatic rẻ: khung hình + giọng + camera tạm + phụ đề. HUMAN LEAD xem và duyệt.
6. Với mỗi shot, Studio đề xuất cách sản xuất. HUMAN LEAD giữ hoặc đổi. Các cách gồm: ảnh tĩnh + chuyển động camera, animation local, AI trả phí, hoặc nhập clip làm sẵn.
7. Studio sản xuất / nhận các shot, dựng bản cuối 16:9 MP4 có giọng, phụ đề, nhạc nền, hiệu ứng âm thanh. HUMAN LEAD duyệt hoặc yêu cầu làm lại từng shot.
8. Mọi lần sinh nội dung đều có hồ sơ: công cụ, model, prompt, tham chiếu, tham số, chi phí, số lần thử, trạng thái duyệt.

## 6. Functional requirements

### FR-001 — Story Library
- User: HUMAN LEAD
- Trigger: nhập truyện mới
- Behavior: lưu nguyên văn kèm nguồn, tác giả, dịch giả, thể loại, quyền sử dụng, trạng thái duyệt; mỗi truyện có ID ổn định.
- Result: truyện xuất hiện trong thư viện; nguyên văn không bị thay đổi bởi các bước sau.

### FR-002 — Adaptation tách khỏi nguồn
- User: HUMAN LEAD / Studio
- Trigger: yêu cầu cải biên
- Behavior: bản cải biên (lời dẫn, thoại, scene, shot list, mô tả nhân vật) lưu thành revision riêng, có lịch sử; mỗi đoạn được đánh dấu *nguyên văn / diễn giải / sáng tác*.
- Result: HUMAN LEAD xem được khác biệt giữa nguồn và cải biên, duyệt một revision.

### FR-003 — Character & Visual Bible
- User: HUMAN LEAD
- Trigger: tạo / sửa nhân vật, bối cảnh, phong cách
- Behavior: lưu nhận diện, ngoại hình, trang phục, biểu cảm, tư thế, bảng màu, ảnh tham chiếu, kèm trạng thái duyệt.
- Result: mọi shot tham chiếu được tới asset bible đã duyệt.

### FR-004 — Voice & timing
- User: HUMAN LEAD
- Trigger: duyệt kịch bản
- Behavior: tạo giọng tiếng Việt cho lời dẫn và ít nhất 2 giọng nhân vật bằng một engine local, hoặc nhận file audio nhập tay; đo thời lượng từng câu.
- Result: mỗi shot có thời lượng đề xuất khớp với giọng.

### FR-005 — Storyboard & animatic
- User: HUMAN LEAD
- Trigger: có voice + shot list
- Behavior: mỗi shot có một khung hình (sinh hoặc nhập); HUMAN LEAD sắp thứ tự, chỉnh thời lượng; Studio dựng animatic MP4 rẻ có giọng, phụ đề, camera tạm.
- Result: animatic xem được; có trạng thái duyệt.

### FR-006 — Shot production routing
- User: HUMAN LEAD
- Trigger: animatic đã duyệt
- Behavior: Studio đề xuất phương thức cho từng shot theo độ phức tạp chuyển động, nhu cầu nhất quán, chi phí, thời lượng và khả năng kỹ thuật. Có 5 phương thức: (1) ảnh tĩnh + camera; (2) nhân vật 2D tái dùng; (3) image-to-video local; (4) image-to-video trả phí; (5) nhập clip.
- Result: mỗi shot có phương thức đã chọn và lý do; HUMAN LEAD ghi đè được.

### FR-007 — Paid generation safeguard
- User: HUMAN LEAD
- Trigger: một shot chọn phương thức trả phí
- Behavior: hiển thị chi phí ước tính và yêu cầu HUMAN LEAD xác nhận trước mỗi lần sinh; tôn trọng trần ngân sách và số lần thử tối đa; không tự retry trả phí.
- Result: không có lần sinh trả phí nào xảy ra khi chưa xác nhận.

### FR-008 — Manual asset import
- User: HUMAN LEAD
- Trigger: có clip / ảnh / audio làm ở công cụ ngoài
- Behavior: nhập vào đúng shot / asset, ghi công cụ nguồn, model, chi phí khai báo, license.
- Result: asset nhập tay dùng được như asset sinh tự động.

### FR-009 — Timeline & render
- User: HUMAN LEAD
- Trigger: đủ shot cho bản dựng
- Behavior: dựng phim 16:9 từ shot, giọng, phụ đề tiếng Việt, transition, nhạc nền, SFX.
- Result: một file MP4; dựng lại cùng đầu vào cho cùng kết quả.

### FR-010 — Review Studio
- User: HUMAN LEAD
- Trigger: mở giao diện trong mạng LAN
- Behavior: xem tổng quan project, truyện / kịch bản, bible, storyboard / animatic, từng shot, bản dựng; duyệt / từ chối / yêu cầu làm lại.
- Result: mọi approval được lưu kèm thời điểm.

### FR-011 — Cost & asset ledger
- User: HUMAN LEAD
- Trigger: mỗi lần sinh / nhập
- Behavior: lưu provider, model, prompt, asset tham chiếu, tham số, thời lượng, vị trí output, revision, trạng thái duyệt, chi phí ước tính / thực tế, số lần thử.
- Result: HUMAN LEAD xem được tổng chi phí theo phim / shot / provider.

### FR-012 — Recovery / resume
- User: HUMAN LEAD
- Trigger: tắt máy / lỗi giữa chừng
- Behavior: chạy lại không làm lại bước đã hoàn tất và còn hợp lệ; output đã duyệt không bị ghi đè.
- Result: tiếp tục từ bước dở dang.

## 7. Non-functional requirements

- NFR-001: Studio chạy được mà không cần tài khoản dịch vụ trả phí nào (đường local / nhập tay đủ để ra phim).
- NFR-002: Studio không phụ thuộc Figma hay một nhà cung cấp AI duy nhất; asset trao đổi qua PNG / SVG / JSON / MP4 / WAV.
- NFR-003: Animatic của pilot dựng xong trong ≤ 5 phút trên server (cần đo).
- NFR-004: Giao diện review dùng trong LAN, có bảo vệ truy cập.

## 8. Business rules / constraints

- BR-001: Không sinh shot trả phí trước khi animatic được duyệt.
- BR-002: Nguyên văn truyện và bản cải biên lưu tách biệt; mọi thay đổi có lịch sử.
- BR-003: Với nội dung Phật giáo: không tạo lời Phật dạy rồi gán cho kinh điển; phân biệt nguyên văn / diễn giải / sáng tác; HUMAN LEAD duyệt trước sản xuất.
- BR-004: Không dùng footage, frame hay nhân vật của tác phẩm bên thứ ba khi chưa có quyền.
- BR-005: Hệ thống story-agnostic; không hard-code riêng Liêu Trai hay Phật giáo.
- BR-006: Mọi chi tiêu phải được HUMAN LEAD duyệt; mặc định không có provider trả phí nào được bật.

## 9. Edge cases / failure behavior

- EC-001: Provider lỗi hoặc hết hạn mức → shot giữ trạng thái chưa xong, không mất asset khác, không tự retry trả phí.
- EC-002: Vượt trần ngân sách → chặn lần sinh, báo lý do.
- EC-003: Kịch bản đổi sau khi đã có shot → các shot / animatic liên quan bị đánh dấu "cần xem lại"; shot đã duyệt không bị xóa.
- EC-004: File nhập sai định dạng / độ phân giải → từ chối kèm lý do.
- EC-005: Truyện thiếu thông tin quyền sử dụng → không cho vào sản xuất cho tới khi HUMAN LEAD xác nhận.

## 10. Acceptance criteria

### AC-001 — Pilot film
Given một truyện đã duyệt có 2 nhân vật lặp lại và 2–3 bối cảnh, when HUMAN LEAD đi hết quy trình, then có một MP4 16:9 dài 60–90 giây, 8–16 shot, giọng tiếng Việt nghe hiểu, phụ đề tiếng Việt.

### AC-002 — Animatic gate
Given animatic chưa được duyệt, when yêu cầu sinh một shot trả phí, then yêu cầu bị chặn.

### AC-003 — Paid confirmation
Given một shot chọn phương thức trả phí, when bắt đầu sinh, then Studio hiển thị chi phí ước tính và chỉ chạy sau khi HUMAN LEAD xác nhận; số lần thử không vượt giới hạn đã đặt.

### AC-004 — Traceability
Given bản phim cuối, when HUMAN LEAD mở ledger, then mỗi shot cho biết phương thức, provider / model (hoặc "nhập tay"), asset tham chiếu, số lần thử, chi phí ước tính / thực tế và trạng thái duyệt.

### AC-005 — Source fidelity
Given truyện đã cải biên, when xem truyện, then nguyên văn không đổi và bản cải biên hiển thị riêng, có đánh dấu nguyên văn / diễn giải / sáng tác.

### AC-006 — Reproducible render
Given cùng các asset và timeline đã duyệt, when dựng lại, then thu được video có cùng thời lượng, cùng thứ tự shot và cùng audio.

### AC-007 — Method comparison
Given ít nhất 2 shot đại diện, when sản xuất bằng ít nhất 2 phương thức khác nhau (vd ảnh tĩnh + camera so với image-to-video), then HUMAN LEAD xem được các phiên bản cạnh nhau, kèm chi phí và thời gian từng phiên bản.

### AC-008 — Resume
Given quá trình bị dừng giữa chừng, when chạy lại, then các bước đã xong và còn hợp lệ không chạy lại, và shot đã duyệt giữ nguyên.

## 11. Out of scope

- Phim dài 7–10 phút (P4).
- Tự động đăng YouTube.
- Lip-sync chính xác theo âm vị.
- Tích hợp Figma API.
- Nhiều người dùng / phân quyền.
- Workflow riêng cho nội dung Phật giáo (P5), ngoài các business rule BR-003.
- Huấn luyện model / LoRA.

## 12. Assumptions

- Server có GPU dùng được cho image / video model local (chưa xác nhận).
- HUMAN LEAD có thời gian duyệt mỗi giai đoạn của pilot (khoảng 4–10 giờ tổng).
- Một engine TTS tiếng Việt local đạt chất lượng nghe hiểu (chưa đo).

## 13. Open questions

1. Truyện pilot nào, bản dịch nào, quyền sử dụng ra sao (D-08)?
2. Pilot 8–12 shot (theo kickoff) hay 12–16 shot (gần nhịp thể loại hơn) (D-09)?
3. Kênh đích có bật kiếm tiền không? Câu trả lời ảnh hưởng license Figma Education và điều khoản provider (D-10, D-13).
4. Giọng: TTS local hay HUMAN LEAD / người khác thu âm? Giọng nhân vật cần giống ai (D-06)?
5. Phong cách hình ảnh mục tiêu: gần video tham khảo hay khác (D-12)?
6. Ai dùng Review Studio ngoài HUMAN LEAD? Truy cập từ ngoài LAN không?

## 14. Readiness

- [x] Problem is specific.
- [x] Goal is observable and non-technical.
- [x] Actors are known.
- [x] Current context is sufficient.
- [x] Desired workflow is clear.
- [x] Functional requirements are explicit.
- [x] Relevant rules and edge cases are recorded.
- [x] Acceptance criteria are testable.
- [x] Out of scope is explicit.
- [ ] No material open question blocks planning.

Readiness: NEEDS_CLARIFICATION

## 15. Traceability

- Source idea / request: HUMAN LEAD kickoff "AI Animation Studio — Master Project Kickoff" (2026-10-23), §2, §5, §6, §9.
- Parent requirement: None
- Generated tasks: None
- Notes: research inputs in `docs/research/`; architecture options in `docs/architecture/ARCHITECTURE_PROPOSAL.md` (không thuộc requirement).
