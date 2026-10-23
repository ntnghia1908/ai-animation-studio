# Framework History

| Metadata | Value |
|---|---|
| Status | CURRENT |
| Scope | Lịch sử thay đổi framework (core, adapter, checker) của project này sau adoption |

File này chỉ ghi lịch sử; rule hiện hành nằm ở canonical owner của nó (`docs/ai/workflow.md`, `docs/ai/execution-profiles.md`, adapter, checker).

## Quy ước

- Mỗi thay đổi framework (core, adapter, checker) thêm một entry mới: ngày, thay đổi, lý do, PR/commit.
- Version tăng khi rule trong Framework Core thay đổi, hoặc khi HUMAN LEAD quyết một đợt thay đổi adapter / project policy đủ lớn để đánh version mới. Thay đổi nhỏ chỉ ở adapter hoặc checker ghi entry dưới version hiện tại, không tăng version.
- Heading version có dạng `## v<Version>`, khớp giá trị `Version` trong metadata của `docs/ai/workflow.md`; `scripts/framework-check.mjs` kiểm tra điều này.

## v4.4

- Ngày: 2026-10-08
- Thay đổi: thêm boundary authorization mode và bounded task-level parallelism cho multiple IMPLEMENTER instances (1–3). Boundary-authorized task không cần APPROVE TASK riêng; decision gates vẫn thuộc HUMAN LEAD.
- Lý do: giảm bottleneck do per-task approval sau khi một implementation boundary đã được HUMAN LEAD chấp thuận, đồng thời cho phép fan-out các task độc lập.
- Decision: HUMAN LEAD 2026-10-08.
- Task: TASK-002-boundary-authorization-parallel.

### P0.1 — sửa product-check.mjs — 2026-10-23

- Thay đổi: `scripts/product-check.mjs` đổi escape sai (`\\.`, `\\n`, `\\s`, `\\S`, `\\d`, `\\b`) trong regex literal thành escape đơn; luật READY giữ nguyên. Thêm `tests/product-check.test.mjs` (gồm test hồi quy so với bản `76abae8`). Đây là thay đổi checker của project, không phải Framework Core; không tăng version.
- Lý do: bản của kit luôn FAIL giả (filename, frontmatter) với REQ hợp lệ. Bản vá và báo lỗi upstream: `docs/tasks/P0.1-checker-quality-gate-ci.md`, mục Result.
- Task: P0.1 (`docs/tasks/P0.1-checker-quality-gate-ci.md`); PR/commit: chờ integration.

### FW-GROWTH-01 — 2026-10-19

- Thay đổi: `docs/ai/workflow.md` §4 mục contract "Code bị thay / xóa"; §5 tái dùng trước khi viết; §7 READY report có AC → test, dòng thêm / xóa, helper mới. Template task + adapter dẫn chiếu owner.
- Lý do: audit code growth (helper viết lại 7 lần, bug do viết lại hàm có sẵn, FEATURE xóa 3 %, test ≈ 1 : 1 code).
- Task: FW-GROWTH-01 (`docs/tasks/FW-GROWTH-01.md`); PR/commit: chờ integration.

### FW-TOKEN-01 — 2026-10-19

- Thay đổi: bổ sung quy tắc tiết kiệm token tại `docs/ai/workflow.md` §4/§5/§9/§10; adapter / current-state dẫn chiếu owner; thêm `scripts/token-audit.py` để đo cost per merged task, không mặc định theo dự án.
- Lý do: giảm context nạp lại và vòng sửa sau review; đo transcript thật do ORCHESTRATOR xác nhận (AC4).
- Task: FW-TOKEN-01 (`docs/tasks/FW-TOKEN-01.md`); PR/commit: chờ integration.

### FW-CODEX-ORCH-01 (Phase 1B.1)

- Thay đổi: adapter Codex khai thêm role `orchestrator` (giữ `implementer`); README adapter Codex và Claude Code, cùng execution rule, mô tả Codex ORCHESTRATOR giao thủ công cho Claude Code Sonnet IMPLEMENTER. Thêm test binding `agents.orchestrator = codex`; sửa kỳ vọng test lịch sử từ 4.3 sang 4.4. Chỉ đổi adapter / test; Framework Core v4.4 không đổi.
- Lý do: cho phép Codex điều phối và review mà không đổi Core; thay đổi nhỏ ở adapter nên ghi dưới version hiện tại.
- Trạng thái: chưa pilot; independent review pending.
- Task: FW-CODEX-ORCH-01 (`docs/tasks/FW-CODEX-ORCH-01.md`).

## v4.3

- Agent Adapter Architecture v1: provider-neutral role contracts, machine-readable adapter descriptors, project role bindings and task-level IMPLEMENTER selection.
- Existing S0/S1/S2 governance, approval gates, verification and integration ownership remain unchanged.

## v4.2

- Lịch sử của kit trước adoption; xem `CHANGELOG.md` của `ntnghia1908/ai-dev-framework`.

## Adoption — 2026-10-23

- Thay đổi: adopt Framework kit v4.4 (`ntnghia1908/ai-dev-framework` `main` @ `7496eac`, gồm FW-GROWTH-01 và FW-TOKEN-01). Chi tiết: `FRAMEWORK_ADOPTION.md`.
- Lý do: HUMAN LEAD kickoff AI Animation Studio (P0) yêu cầu dùng AI Dev Framework v4.4 hiện có.
- PR: #1 (merged `49295d0`, 2026-10-23); decision D-01 ACCEPTED.
