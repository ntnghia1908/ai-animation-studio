# Current State

| Metadata | Value |
|---|---|
| Status | OPERATIONAL STATE — NOT AUTHORITY |

Chỉ ghi operational state không suy ra được từ Git, task contract hoặc accepted decisions.

Ngân sách token của file: xem `docs/ai/workflow.md` §10.

## Current focus

- P0 đã được HUMAN LEAD review (2026-10-23). Research và Option A được chấp nhận. Thứ tự P0.1 → P1a → P1b (`docs/decisions/ADR-001-mvp-architecture-and-phasing.md`).
- P0.1 hoàn tất (PR #3, `98fdf00`). Gate: `node scripts/quality-gate.mjs`; CI "Quality" chạy trên mọi PR.
- P1a đóng (PR #6, #8, #9, #10, #11): pilot "Tổ kiến và nhà ở" QC PASS 9/9, HUMAN LEAD "coi như ổn" — Result `docs/tasks/P1a.4-output-qc-pilot.md`.
- P1b chia ba boundary nối tiếp (HUMAN LEAD 2026-10-24): P1b-1 TTS local + pilot 60–90 s → P1b-2 GPU local AI + Review Studio → P1b-3 router / premium. Boundary P1b-1 ACCEPTED (2026-10-24): `docs/decisions/P1b-1-TTS-FULL-PILOT-AUTHORIZATION-DRAFT.md` — D-09, D-12, truyện "Tổ kiến", giọng không clone, tăng tốc encode đã chốt; D-06 chốt sau E4.
- GPU: hai máy Windows trong LAN (RTX 3090, RTX 3050), dùng chung với youtube-auto-short; ghi chú truy cập ở draft P1b-1 §1.
- Làm việc trên server; laptop chỉ là máy dev.

## Next proposed action

PROPOSED, không authorize implementation:

1. HUMAN LEAD merge PR #12 (boundary P1b-1).
2. Session mới: soạn + xin duyệt contract task P1b-1.1 E4 (so sánh TTS ngoài repo), rồi chạy E4.
3. HUMAN LEAD (tùy chọn) bật required status check "Quality" cho `main`; gửi báo lỗi `product-check.mjs` lên kit.

## Open decisions

- D-08: truyện pilot đã chọn ("Tổ kiến và nhà ở", *Báo Ứng Hiện Đời* tập 1); quyền bản dịch + bản audiobook chưa xác nhận → chỉ demo nội bộ, không đăng.
- D-06 (sau E4, P1b-1.1). Sau: D-05, D-07 (P1b-2), D-11 (P1b-3), D-10, D-13 (ADR-001 A5).

## Blockers

- Token `gh` thiếu scope `workflow`: push file `.github/workflows/` qua SSH (server đã có SSH key).
