# Claude Code — execution adapter

Adapter riêng cho Claude Code. Shared workflow nằm ở `AGENTS.md` và `docs/ai/`.

@../../docs/workflow/current-state.md

## Mapping vai trò

- `dual-agent`, Claude là ORCHESTRATOR (`agents.orchestrator = claude-code` hoặc không bind): main session = ORCHESTRATOR; `.claude/agents/implementer` = IMPLEMENTER.
- `dual-agent`, external Codex là ORCHESTRATOR (`agents.orchestrator = codex`, task ghi `Orchestrator: codex` và `Implementer: claude-code`): Claude main session = IMPLEMENTER do ORCHESTRATOR giao. Main session không tự nhận ORCHESTRATOR, không delegate tiếp sang subagent hay agent khác, không tự mở rộng scope; dừng ở READY report cho Codex review. Không giả định subagent `implementer` đã được đăng ký.
- `single-agent`: main session đóng cả ORCHESTRATOR + IMPLEMENTER; không delegate implementer.
- Không gọi agent/model/AI CLI ngoài execution profile và field `Implementer` của task.

## Entry point

Đọc entry point thực sự tồn tại. Adopted project: `AGENTS.md`, `docs/ai/project-profile.md`, `docs/workflow/current-state.md`, task contract. Starter-kit root không phải adopted project và không có các file trên: dùng `core/`, `templates/`, ADR và task contract. Capabilities trong adapter descriptor không cấp authorization.

## Chọn IMPLEMENTER

Task `dual-agent` do Claude làm ORCHESTRATOR: ORCHESTRATOR chọn IMPLEMENTER theo Danh sách IMPLEMENTER ở `docs/ai/project-profile.md` §7 lúc viết contract và ghi vào field `Implementer`. Gọi adapter tương ứng: subagent `implementer` (Claude Code), hoặc CLI của adapter khác theo README của adapter đó (`adapters/<tool>/README.md` trong kit). Chỉ gọi IMPLEMENTER ghi trong contract.

Codex CLI làm IMPLEMENTER: theo `adapters/codex/README.md` mục "Cách chạy" (kiểm quota trước, `-s workspace-write`, effort đặt rõ); verification dài: xem `docs/ai/workflow.md` §5, giới hạn sandbox: xem README adapter Codex.

## Delegation

Áp dụng khi Claude là ORCHESTRATOR; khi là IMPLEMENTER cho Codex thì không delegate tiếp. Giao task cho implementer kèm task contract, base commit, `Implementation authorized: YES` và plan ngắn.
Resume cùng task theo `docs/ai/workflow.md` §9; task mới dùng context mới.

Mẫu delegation prompt:

```text
Contract: <path>; base commit: <SHA>; Implementation authorized: YES.
Plan: <ngắn, trong owned paths>.
Giới hạn chờ lệnh: xem docs/ai/workflow.md §5 (Claude Code subagent: 5 phút).
Tái dùng: <helper / module có sẵn>; code bị thay: <mục Code bị thay / xóa của contract>.
READY report theo docs/ai/workflow.md §5 / §7 (helper mới, AC → test, dòng + / −).
```

## Session

Bootstrap từ repository. Session mới không dùng transcript chat làm authority.

## Kết thúc session

Rule session scope và handoff: `docs/ai/workflow.md` §9. Trong Claude Code, khi đủ scope thì đề xuất `/clear` và đưa handoff prompt trong một code block để dán vào session mới.
