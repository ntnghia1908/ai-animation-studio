# Current State

| Metadata | Value |
|---|---|
| Status | OPERATIONAL STATE — NOT AUTHORITY |

Chỉ ghi operational state không suy ra được từ Git, task contract hoặc accepted decisions.

Ngân sách token của file: xem `docs/ai/workflow.md` §10.

## Current focus

- P0 đã được HUMAN LEAD review (2026-10-23). Research và Option A được chấp nhận. Thứ tự P0.1 → P1a → P1b (`docs/decisions/ADR-001-mvp-architecture-and-phasing.md`).
- Việc chuyển sang server: HUMAN LEAD clone repo về server và làm tiếp ở đó. Laptop chỉ là máy dev.

## Next proposed action

PROPOSED, không authorize implementation:

1. HUMAN LEAD merge PR #1 và trả lời D-01 (framework adoption) và D-14 (phê chuẩn P0 single-agent).
2. HUMAN LEAD duyệt `docs/decisions/P0.1-QUALITY-GATE-AUTHORIZATION-DRAFT.md`. Sau đó thực hiện `docs/tasks/P0.1-checker-quality-gate-ci.md` trên server, branch `chore/p0.1-quality-gate`; push workflow qua SSH hoặc token có scope `workflow`.
3. Song song: HUMAN LEAD chuẩn bị D-04 (runtime server) và D-08 (truyện + asset pack: ảnh 5–8 shot, 1 shot có 2–3 layer, file giọng) cho P1a.

## Open decisions

- Cho P0.1: D-01, D-14, duyệt boundary P0.1.
- Cho P1a: D-04, D-08, P1a-1 (vị trí workspace), P1a-2 (ngưỡng quality gate).
- Hoãn tới P1b: D-05, D-06, D-07, D-09, D-10, D-11, D-12, D-13 (ADR-001 A5).

## Blockers

- Token `gh` trên laptop thiếu scope `workflow` → không push được file `.github/workflows/`. Trên server dùng SSH hoặc `gh auth refresh -s workflow`.
- `scripts/product-check.mjs` có lỗi regex; sẽ sửa ở P0.1.
