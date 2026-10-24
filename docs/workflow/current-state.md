# Current State

| Metadata | Value |
|---|---|
| Status | OPERATIONAL STATE — NOT AUTHORITY |

Chỉ ghi operational state không suy ra được từ Git, task contract hoặc accepted decisions.

Ngân sách token của file: xem `docs/ai/workflow.md` §10.

## Current focus

- P0 đã được HUMAN LEAD review (2026-10-23). Research và Option A được chấp nhận. Thứ tự P0.1 → P1a → P1b (`docs/decisions/ADR-001-mvp-architecture-and-phasing.md`).
- P0.1 hoàn tất (PR #3, `98fdf00`). Gate: `node scripts/quality-gate.mjs`; CI "Quality" chạy trên mọi PR.
- Boundary P1a ACCEPTED (2026-10-23): `docs/decisions/P1a-VERTICAL-SLICE-AUTHORIZATION-DRAFT.md`. P1a.1 (PR #6), P1a.2 (PR #8), P1a.3 (PR #9) đã merge. P1a.4 Phần A (QC output + render song song) READY: `docs/tasks/P1a.4-output-qc-pilot.md`; Phần B (pilot "Tổ kiến và nhà ở") có bản xem trước, chờ chạy thật + HUMAN LEAD chấm.
- Làm việc trên server; laptop chỉ là máy dev.

## Next proposed action

PROPOSED, không authorize implementation:

1. HUMAN LEAD merge PR P1a.4 Phần A.
2. Chạy pilot thật trên server: `bash ~/animation-studio-pilot/to-kien/run.sh` (giọng audiobook mặc định; `VOICE=piper` cho bản TTS), xem `film.mp4`, chấm 5 tiêu chí boundary §5.
3. ORCHESTRATOR ghi kết quả Phần B vào Result P1a.4 (PR docs riêng); đạt → đề xuất đóng P1a, mở P1b; không đạt → contract P1a.5.
4. HUMAN LEAD (tùy chọn) bật required status check "Quality" cho `main`; gửi báo lỗi `product-check.mjs` lên kit.

## Open decisions

- D-08: truyện pilot đã chọn ("Tổ kiến và nhà ở", *Báo Ứng Hiện Đời* tập 1); quyền bản dịch + bản audiobook chưa xác nhận → chỉ demo nội bộ, không đăng.
- Hoãn tới P1b: D-05, D-06, D-07, D-09, D-10, D-11, D-12, D-13 (ADR-001 A5).

## Blockers

- Token `gh` thiếu scope `workflow`: push file `.github/workflows/` qua SSH (server đã có SSH key).
