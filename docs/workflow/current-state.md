# Current State

| Metadata | Value |
|---|---|
| Status | OPERATIONAL STATE — NOT AUTHORITY |

Chỉ ghi operational state không suy ra được từ Git, task contract hoặc accepted decisions.

Ngân sách token của file: xem `docs/ai/workflow.md` §10.

## Current focus

- P0 đã được HUMAN LEAD review (2026-10-23). Research và Option A được chấp nhận. Thứ tự P0.1 → P1a → P1b (`docs/decisions/ADR-001-mvp-architecture-and-phasing.md`).
- P0.1 đang IN_PROGRESS (branch `chore/p0.1-quality-gate`): đã sửa `product-check.mjs`, thêm quality gate + CI; chờ push, PR, CI xanh.
- Việc chuyển sang server: HUMAN LEAD clone repo về server và làm tiếp ở đó. Laptop chỉ là máy dev.

## Next proposed action

PROPOSED, không authorize implementation:

1. PR #1 đã merge (`49295d0`); D-01, D-14 ACCEPTED. HUMAN LEAD merge PR #2 (ADR-001 + bản nháp P0.1 / P1a).
2. Boundary P0.1 đã ACCEPTED. Hoàn tất `docs/tasks/P0.1-checker-quality-gate-ci.md`: push qua SSH, mở PR, kiểm CI xanh.
3. Trên server: tạo conda env (D-04); HUMAN LEAD quyết D-08 (truyện + asset pack: ảnh 5–8 shot, 1 shot có 2–3 layer, file giọng) trước P1a.4.

## Open decisions

- Cho P1a: duyệt boundary P1a; phần còn lại của D-04 (env name, Python version); D-08 (trên server); P1a-1 (vị trí workspace); P1a-2 (ngưỡng quality gate).
- Hoãn tới P1b: D-05, D-06, D-07, D-09, D-10, D-11, D-12, D-13 (ADR-001 A5).

## Blockers

- Push `.github/workflows/` (P0.1) cần SSH hoặc token có scope `workflow` (`gh auth refresh -s workflow`); làm trên server.
