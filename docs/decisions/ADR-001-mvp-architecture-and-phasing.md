# ADR-001 — MVP architecture direction and incremental phasing

| Metadata | Value |
|---|---|
| Status | ACCEPTED |
| Accepted by | HUMAN LEAD, 2026-10-23 (review PR #1, P0) |
| Context | `docs/research/*`, `docs/architecture/ARCHITECTURE_PROPOSAL.md` |
| Supersedes | phạm vi boundary của `docs/decisions/P1-IMPLEMENTATION-AUTHORIZATION-DRAFT.md` (P1.0–P1.8 không được duyệt một lần) |

File này là **canonical owner** của hướng kiến trúc MVP và thứ tự phase sau P0. Nơi khác chỉ trỏ tới đây.

## Quyết định của HUMAN LEAD

Ý HUMAN LEAD (tóm tắt trung thực):

> Chấp nhận kết quả nghiên cứu và kiến trúc theo hướng tổng thể, nhưng chưa duyệt toàn bộ P1.0–P1.8 ngay. 14 quyết định D-01…D-14 chưa cần giải quyết cùng lúc. Xử lý theo thứ tự P0.1 → P1a → P1b. Đồng ý Option A — Modular Monolith Python + file workspace + FFmpeg, nhưng tránh xây đủ 10 module và Web UI hoàn chỉnh trước khi có phim mẫu đạt chất lượng.

## A1. Kết quả nghiên cứu

Bốn báo cáo trong `docs/research/` được chấp nhận làm **cơ sở định hướng**. Chúng vẫn là research report, không phải authority chi tiết. Số liệu giá và hiệu năng model vẫn phải kiểm lại khi dùng.

## A2. Kiến trúc: Option A (= D-02, D-03)

- Modular monolith Python (src-layout), **file workspace** (JSON + asset theo hash, ghi atomic, ngoài git), **FFmpeg** làm renderer.
- Domain trung tâm provider-neutral; model / dịch vụ ngoài chỉ đi qua adapter (khi phase sau cần).
- Option B (ComfyUI-centric) và Option C (services + DB + SPA): không chọn. ComfyUI chỉ được cân nhắc như adapter worker ở phase sau, theo decision riêng.

## A3. Ràng buộc tăng trưởng (canonical)

- **Không xây đủ M1–M10 và không làm Web UI hoàn chỉnh** trước khi có phim mẫu đạt quality gate (`docs/decisions/P1a-VERTICAL-SLICE-AUTHORIZATION-DRAFT.md` §5).
- Chỉ tạo module / abstraction khi vertical slice hiện tại cần. Không dựng sẵn port / adapter / router "cho tương lai".
- Module map trong `ARCHITECTURE_PROPOSAL.md` §7 là hướng đích, không phải danh sách phải làm.

## A4. Thứ tự phase

| Phase | Nội dung | Trạng thái authorization |
|---|---|---|
| P0.1 | Sửa checker, bổ sung quality gate, hoàn thiện CI | Draft: `docs/decisions/P0.1-QUALITY-GATE-AUTHORIZATION-DRAFT.md` (PROPOSED) |
| P1a | Vertical slice offline rất nhỏ: nhập truyện, ảnh / giọng, animatic, một đoạn phim có chuyển động | Draft: `docs/decisions/P1a-VERTICAL-SLICE-AUTHORIZATION-DRAFT.md` (PROPOSED) |
| P1b | Review Studio, local AI, tích hợp provider | Chưa draft; chỉ xem xét **sau khi HUMAN LEAD xem video P1a** |

Mỗi phase cần HUMAN LEAD chấp thuận boundary riêng. ADR này không authorize implementation.

## A5. Trạng thái các decision D-01…D-14

| ID | Chủ đề | Trạng thái |
|---|---|---|
| D-02 | Kiến trúc | **ACCEPTED** (A2) |
| D-03 | Lưu trữ file JSON | **ACCEPTED** trong Option A (A2); SQLite xem lại khi cần |
| D-01 | Framework adoption | **ACCEPTED** (HUMAN LEAD 2026-10-23; PR #1 merged `49295d0`) |
| D-14 | Phê chuẩn P0 single-agent | **ACCEPTED** (HUMAN LEAD 2026-10-23) |
| D-04 | Runtime / env / test command | **ACCEPTED một phần** (HUMAN LEAD 2026-10-23): môi trường server là **conda**. Python version, tên env, packaging và lệnh test vẫn là đề xuất trong P1a draft, chốt khi duyệt P1a |
| D-08 | Truyện + asset cho P1a / pilot | Mở. HUMAN LEAD quyết khi đã lên server; cần trước P1a.4 (chạy thật), không chặn P1a.1–P1a.3 (dùng asset tổng hợp) |
| D-06 | TTS | Hoãn: P1a chỉ nhập audio; TTS xét ở P1b |
| D-09 | Số shot pilot | Hoãn: P1a dùng 5–8 shot; pilot đầy đủ xét sau |
| D-12 | Phong cách hình ảnh | Hoãn: P1a dùng ảnh nhập tay |
| D-05 | Web stack + security | Hoãn tới P1b (không có Web UI ở P1a) |
| D-07 | GPU server | Hoãn tới P1b (local AI) |
| D-10 | Figma Education trong sản xuất | Hoãn tới P1b |
| D-11 | Ngân sách premium | Hoãn tới P1b / P3 |
| D-13 | Chính sách AI / kiếm tiền YouTube | Hoãn tới trước lần đăng đầu tiên |

## Hệ quả

- `ARCHITECTURE_PROPOSAL.md`: Option A đã chọn; phần thiết kế chi tiết §7 vẫn là đề xuất.
- `IMPLEMENTATION_ROADMAP.md`: P1 tách thành P1a / P1b.
- `P1-IMPLEMENTATION-AUTHORIZATION-DRAFT.md`: SUPERSEDED, chỉ giữ làm lịch sử.
