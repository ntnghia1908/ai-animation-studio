# Current State

| Metadata | Value |
|---|---|
| Status | OPERATIONAL STATE — NOT AUTHORITY |

Chỉ ghi operational state không suy ra được từ Git, task contract hoặc accepted decisions.

Ngân sách token của file: xem `docs/ai/workflow.md` §10.

## Current focus

- P0 đã được HUMAN LEAD review (2026-10-23). Research và Option A được chấp nhận. Thứ tự P0.1 → P1a → P1b (`docs/decisions/ADR-001-mvp-architecture-and-phasing.md`).
- P0.1 hoàn tất (PR #3, `98fdf00`). Gate: `node scripts/quality-gate.mjs`; CI "Quality" chạy trên mọi PR.
- Boundary P1a ACCEPTED (2026-10-23): `docs/decisions/P1a-VERTICAL-SLICE-AUTHORIZATION-DRAFT.md`. P1a.1 (skeleton + import) READY: `docs/tasks/P1a.1-skeleton-workspace-import.md`.
- Làm việc trên server; laptop chỉ là máy dev.

## Next proposed action

PROPOSED, không authorize implementation:

1. HUMAN LEAD merge PR P1a.1. Trên server: `cp config.example.toml config.toml` (conda env `animation-studio` đã tạo).
2. ORCHESTRATOR soạn task contract P1a.2 (`shots.json` + animatic) để HUMAN LEAD duyệt.
3. HUMAN LEAD cung cấp nguồn truyện Liêu Trai (bản dịch / quyền) và asset pack trước P1a.4.
4. HUMAN LEAD (tùy chọn) bật required status check "Quality" cho `main`; gửi báo lỗi `product-check.mjs` lên kit.

## Open decisions

- D-08 còn phần nguồn truyện + quyền + asset pack (trước P1a.4).
- Hoãn tới P1b: D-05, D-06, D-07, D-09, D-10, D-11, D-12, D-13 (ADR-001 A5).

## Blockers

- Token `gh` thiếu scope `workflow`: push file `.github/workflows/` qua SSH (server đã có SSH key).
