# P1 Implementation Authorization Boundary — Draft

| Metadata | Value |
|---|---|
| Status | PROPOSED — chờ HUMAN LEAD |
| Date | 2026-10-23 |
| Proposed by | ORCHESTRATOR (Claude Code) |
| Requirement | `docs/product/requirements/REQ-001-animation-studio-mvp.md` (NEEDS_CLARIFICATION) |
| Architecture | `docs/architecture/ARCHITECTURE_PROPOSAL.md` (PROPOSAL, Option A đề xuất) |

**Bản nháp này không authorize gì.** Nó chỉ có hiệu lực khi HUMAN LEAD trả lời các decision ở §6 và đổi Status thành `ACCEPTED` (kèm ngày, phạm vi đã sửa). Khi đó task contract P1 dùng `Authorization mode: boundary` và `Authorization source: docs/decisions/P1-IMPLEMENTATION-AUTHORIZATION-DRAFT.md (ACCEPTED <ngày>)`.

## 1. Mục tiêu boundary

Xây Offline MVP theo `docs/roadmap/IMPLEMENTATION_ROADMAP.md` P1 (P1.0–P1.8). Kết quả là pilot 60–90 s tới MP4 bằng phương thức still + camera và nhập tay, không GPU, không chi tiêu.

## 2. Trong boundary (đề xuất)

- Package `src/animation_studio/` theo Option A; module M1–M6, M8–M10 ở mức P1; M7 chỉ có adapter `ManualImport` và `StillCamera`.
- Storage file-based JSON trong workspace ngoài git; atomic IO, hashing, manifest / resume.
- Ollama local qua `urllib` cho M2 (tùy chọn; luôn có đường nhập / sửa tay).
- Render FFmpeg: animatic, camera move / parallax đơn giản, subtitle tiếng Việt, mix audio, MP4 16:9.
- Review Studio LAN: FastAPI + HTML server-render, mật khẩu + cookie.
- `BudgetGuard` và ledger, kể cả khi chưa có paid adapter (để AC-002 / AC-003 kiểm được bằng fake adapter).
- Test (pytest) với fake provider; chốt chặn test không gọi mạng / dịch vụ thật.
- Tái dùng chọn lọc code / pattern của youtube-auto-short theo `docs/research/REUSE_ASSESSMENT.md`, ghi nguồn.
- Cập nhật tài liệu trong phạm vi (project-profile module map, current-state, task contract).
- Dependency được phép **nếu D-04 / D-05 duyệt**: Python 3.12, `fastapi`, `uvicorn`, `pytest`, `httpx` (dev). TTS engine chỉ khi D-06 duyệt.

## 3. Ngoài boundary (cần decision riêng)

- Bất kỳ API / dịch vụ trả phí; đăng ký tài khoản / trial; mua phần mềm.
- Cài và chạy model image / video local (Wan, Qwen-Image-Edit, ComfyUI). Thuộc P0.5 experiment / P2.
- Paid provider adapter (P3).
- Database server, queue, SPA framework.
- Truy cập Review Studio từ ngoài LAN; nhiều người dùng.
- Upload YouTube.
- Thay đổi security model, public API ngoài phạm vi LAN UI.
- Sửa Framework Core; sửa youtube-auto-short.
- Package dùng chung giữa youtube-auto-short và project này.

## 4. Giới hạn vận hành

- Writer đồng thời = 1. Execution profile mặc định `dual-agent` (Claude Code ORCHESTRATOR → subagent `implementer`). `codex` là dự phòng / reviewer.
- Mỗi checkpoint P1.x là một hoặc vài task contract; READY → push + PR; HUMAN LEAD merge.
- Ngân sách diff đề xuất: ≤ khoảng 800 dòng app / PR (theo audit youtube-auto-short F4). Vượt thì tách hoặc ghi lý do.
- Dừng và hỏi HUMAN LEAD khi chạm decision gate mới (`docs/ai/workflow.md` §3, §6).

## 5. Verification bắt buộc của boundary

- `node scripts/framework-check.mjs` PASS.
- `python -m pytest -q` PASS (lệnh chốt cùng D-04).
- Pilot run P1.8: MP4 đạt AC-001; HUMAN LEAD xem và duyệt.

## 6. Decision cần HUMAN LEAD

| ID | Câu hỏi | Khuyến nghị ORCHESTRATOR |
|---|---|---|
| D-01 | Chấp nhận framework adoption như `FRAMEWORK_ADOPTION.md` (kit @ `7496eac`, governance `boundary/3`, writer = 1, `.gitattributes` LF)? | Chấp nhận |
| D-02 | Kiến trúc MVP | Option A (modular monolith Python + file workspace + LAN web); ComfyUI chỉ là adapter worker ở P2 |
| D-03 | Lưu trữ | JSON file + atomic write ở P1; xem lại SQLite ở P4 |
| D-04 | Runtime / env manager / test command | Python 3.12, hatchling src-layout; env: conda (giống youtube-auto-short) hoặc venv tùy server; `python -m pytest -q` |
| D-05 | Web stack + security | FastAPI + uvicorn, HTML server-render, mật khẩu + cookie, chỉ LAN |
| D-06 | TTS | P1 bắt đầu với nhập audio; thêm VieNeu-TTS v3 (Apache-2.0) sau E4 nếu đạt |
| D-07 | GPU server cho project | Xác nhận card (RTX 3090 / 3050?), VRAM, lịch dùng chung Ollama; cho phép E2 / E3 |
| D-08 | Truyện pilot + quyền bản dịch | Truyện Liêu Trai ngắn 2 nhân vật, dùng bản chuyển ngữ mới từ nguyên tác Hán văn hoặc bản dịch đã hết bảo hộ; HUMAN LEAD chọn |
| D-09 | Số shot pilot | 12–16 shot (gần nhịp thể loại), trong đó có shot reframe rẻ; tối thiểu 8 theo kickoff |
| D-10 | Figma Education trong sản xuất công khai | Không dùng cho asset xuất hiện trong video công khai; chỉ planning / prototype nội bộ |
| D-11 | Ngân sách thử nghiệm premium (P0.5 / P3) | Chưa chi ở P1; cho phép tạo tài khoản free tier cho E3 / E6 khi cần (0 USD) |
| D-12 | Phong cách hình ảnh mục tiêu | 2D Á Đông painterly / nét viền như thể loại, nhưng thiết kế nhân vật riêng, không bắt chước video tham khảo |
| D-13 | Chính sách công bố AI / kiếm tiền YouTube | Gắn nhãn nội dung AI theo YouTube; đảm bảo đóng góp sáng tạo (kịch bản, lời dẫn, dựng) |
| D-14 | Execution profile P0 (single-agent, ORCHESTRATOR làm trực tiếp tài liệu) | Phê chuẩn hồi tố; P1 dùng dual-agent |

## 7. Phê duyệt

- HUMAN LEAD decision: _(trống — chờ)_
- Ngày: _(trống)_
- Sửa đổi so với bản nháp: _(trống)_
