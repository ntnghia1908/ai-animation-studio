# Current State

| Metadata | Value |
|---|---|
| Status | OPERATIONAL STATE — NOT AUTHORITY |

Chỉ ghi operational state không suy ra được từ Git, task contract hoặc accepted decisions.

Ngân sách token của file: xem `docs/ai/workflow.md` §10.

## Current focus

P0 — Research & Framework Bootstrap (`docs/tasks/P0-research-bootstrap.md`). Gate hiện tại: **P0 READY FOR HUMAN REVIEW — P1 NOT YET AUTHORIZED**.

## Next proposed action

PROPOSED, không authorize implementation:

1. HUMAN LEAD review PR P0 và trả lời các decision D-01…D-14 (`docs/decisions/P1-IMPLEMENTATION-AUTHORIZATION-DRAFT.md` §6).
2. Nếu duyệt: chạy các experiment E1–E6 không tốn phí (`docs/research/ANIMATION_WORKFLOW_RESEARCH.md` §9) song song với task S1 đầu tiên của P1 (pilot adoption framework).

## Open decisions

Danh sách D-01…D-14 ở `docs/decisions/P1-IMPLEMENTATION-AUTHORIZATION-DRAFT.md` §6. Quan trọng nhất: kiến trúc MVP (D-02), GPU server dùng được cho project (D-07), truyện pilot và quyền bản dịch (D-08), engine TTS (D-06).

## Blockers

- Chưa xác nhận cấu hình GPU server cho project này. Laptop dev không có GPU NVIDIA nên không benchmark được local image-to-video.
- `scripts/product-check.mjs` của kit có lỗi regex (finding ngoài scope; chi tiết ở `FRAMEWORK_ADOPTION.md`).
