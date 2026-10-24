# AGENTS.md

Entry point cho mọi agent làm việc trong repository này.

| Cần biết | Ở đâu |
|---|---|
| Quy trình S0/S1/S2, decision gate, lifecycle, review, integration | `docs/ai/workflow.md` |
| IDEA → REQUIREMENT Product Agent | `docs/product/PRODUCT_AGENT.md` |
| Vai trò HUMAN LEAD / ORCHESTRATOR / IMPLEMENTER | `docs/ai/execution-profiles.md` |
| Project này là gì, authority, module, policy, integration | `docs/ai/project-profile.md` |
| Focus, blocker, open decision, next action | `docs/workflow/current-state.md` |
| Task contract S1/S2 | `docs/tasks/_template.md` |
| Lịch sử thay đổi framework sau adoption | `docs/ai/framework-history.md` |

## Bootstrap

Đầu mỗi session/task, đọc theo thứ tự:

1. file này;
2. `docs/ai/project-profile.md`;
3. `docs/workflow/current-state.md`;
4. approved task contract, nếu có;
5. `AGENTS.md` gần nhất của subtree sắp sửa;
6. authority, source và tests liên quan.

Không preload toàn bộ tài liệu. Session mới bootstrap từ repository, không dựa vào transcript chat.

## Native dual-agent (auto-adapt)

CLI đang mở (Claude Code hoặc Codex) tự đề xuất mình là ORCHESTRATOR và giao việc cho subagent native của chính tool đó, chỉ khi: adapter của nó được bật trong `framework.config.json`, hỗ trợ role, không có `agents.orchestrator` cố định mâu thuẫn, và policy của task cho phép. Có binding cố định sang tool khác → dừng, chờ HUMAN LEAD quyết. Chi tiết (mapping native, write concurrency, handoff): `docs/ai/project-profile.md` §7.

## Invariants

- Repository là source of truth; chat/session không thay thế authority, task contract hoặc source/tests.
- Tuân thứ tự authority trong `docs/ai/project-profile.md`.
- File lịch sử không được dùng làm authority hiện hành.
- Không mô tả thành phần mới chỉ được lên kế hoạch như đã implemented.
- Chỉ làm những gì authority và task contract đã duyệt; không âm thầm mở rộng scope.
- Không thay đổi architecture, dependency, security model, public API contract hoặc project-wide policy một cách âm thầm.
- Một normative rule chỉ có một canonical owner; nơi khác chỉ pointer tới rule.
- Không tuyên bố PASS cho verification chưa chạy thành công trong môi trường hiện tại.
- Không sửa test để che lỗi.

## Project boundary

- Giai đoạn hiện tại: P0 đã review; P0.1 (checker, quality gate, CI) đã xong (PR #3). P1a (vertical slice) đã đóng. Boundary **P1b-1 — TTS local + pilot đầy đủ** ACCEPTED (2026-10-24); chưa có task P1b-1 nào được duyệt (chi tiết: `docs/ai/project-profile.md`).
- Source code ứng dụng hiện chỉ có các file phẳng của P1a trong `src/animation_studio/` (module map: `docs/ai/project-profile.md` §3). Hướng kiến trúc: Option A (`docs/decisions/ADR-001-mvp-architecture-and-phasing.md`). Mọi module M1–M10 chỉ là **planned**; không xây trước khi vertical slice cần (ADR-001 A3).
- Boundary đã duyệt: P0.1 (`docs/decisions/P0.1-QUALITY-GATE-AUTHORIZATION-DRAFT.md`, hoàn tất) P1a (`docs/decisions/P1a-VERTICAL-SLICE-AUTHORIZATION-DRAFT.md`, hoàn tất), P1b-1 (`docs/decisions/P1b-1-TTS-FULL-PILOT-AUTHORIZATION-DRAFT.md`, ACCEPTED). Chỉ tạo/sửa source, test, dependency hay config ứng dụng trong boundary P1b-1 và theo task contract đã duyệt. Thứ tự: P0.1 → P1a → P1b-1 → P1b-2 → P1b-3 (ADR-001 A4, P1b-1 §1). Quality gate: `node scripts/quality-gate.mjs`.
- Không gọi API trả phí, không mua/đăng ký dịch vụ, không đăng nội dung lên YouTube khi chưa có HUMAN LEAD approval rõ ràng.
- Repository là public: không commit media nguồn có bản quyền của bên thứ ba (vd video tham khảo), credential hay token.
