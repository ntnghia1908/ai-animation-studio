# Framework Adoption Record

## Reference

- Framework kit: `ntnghia1908/ai-dev-framework`, nhánh `main` @ `7496eac` (merge PR #11, FW-GROWTH-01). `VERSION` = `4.4`; Core `docs/ai/workflow.md` Version `4.4`. Kit chưa có tag `v4.4` (tag mới nhất `v4.2`), nên adoption ghi theo commit, không theo tag.
- Lưu ý: bản clone local `ai-dev-framework/` trong workspace đang ở `d7df465` (cũ hơn `origin/main` 8 commit). Adoption dùng snapshot `git archive origin/main` @ `7496eac`; bản clone local không bị sửa.
- Adoption date / decision: 2026-10-23, theo yêu cầu kickoff của HUMAN LEAD ("AI Animation Studio — Master Project Kickoff", §1, §11, §12). HUMAN LEAD chấp nhận adoption (D-01, 2026-10-23); PR #1 merged `49295d0`.

Thay đổi framework sau adoption ghi ở `docs/ai/framework-history.md`.

## Adopted

- Framework Core nguyên văn: `docs/ai/workflow.md`, `docs/ai/execution-profiles.md`, `docs/ai/agent-adapter-contract.md`, `docs/ai/adapter-descriptor.schema.json`.
- Template Project Layer: `AGENTS.md`, `CLAUDE.md`, `framework.config.json`, `docs/ai/project-profile.md`, `docs/ai/framework-history.md`, `docs/workflow/current-state.md`, `docs/tasks/_template.md`, `docs/product/` (PRODUCT_AGENT, README, requirement template).
- Adapter: `chatgpt` (Product Agent), `claude-code` (ORCHESTRATOR / IMPLEMENTER, gồm `.claude/`), `codex` (descriptor + README). Đây là bộ adapter mặc định của template v4.4.
- Workflow: `.github/workflows/requirement-to-task.yml` (chép nguyên văn từ adapter, P0.1) và `.github/workflows/quality.yml` (P0.1).
- Script: `scripts/framework-check.mjs`, `scripts/product-check.mjs` (đã sửa regex ở P0.1), `scripts/token-audit.py`, `scripts/codex-usage.py`.
- Governance: `boundary` mode, `maxParallelImplementers: 3` (chỉ là trần cấu hình; writer thực tế = 1).

## Adapted

- `docs/ai/project-profile.md`: điền project, authority order, module map (toàn bộ planned), policy, integration, execution profile, setup cho AI Animation Studio.
- Thêm `.gitattributes` (`* text=auto eol=lf`). Lý do: máy Windows có `core.autocrlf=true`, khiến file bị checkout thành CRLF; `framework-check.mjs` tách dòng theo `\n` nên báo sai "missing entry ## v4.4". Đây là cấu hình repo, không sửa Core hay checker.
- REQ-001 được ORCHESTRATOR soạn trực tiếp từ kickoff của HUMAN LEAD thay vì qua buổi phỏng vấn Product Agent (ChatGPT), vì kickoff đã chứa đủ IDEA và ràng buộc. Status giữ `NEEDS_CLARIFICATION` cho tới khi HUMAN LEAD trả lời các open question.
- Thứ tự "Bước 1 bootstrap rồi mới tới IDEA" (`docs/ai/PROJECT_BOOTSTRAP.md` của kit) được gộp vào một PR P0 theo yêu cầu kickoff §12. Cài đặt theo `docs/install-new-project.md` của kit (thủ công), vì `scripts/bootstrap-project.sh` từ chối repo đã có `README.md`.

## Not adopted

- Adapter `copilot`: chưa cần, HUMAN LEAD không yêu cầu.
- `bootstrap/github/framework-bootstrap.yml` (Mode A): repo đã có commit và đã cài local.
- Tài liệu nội bộ của kit (`docs/mechanism.md`, `docs/install-*.md`, ADR / task của kit): tham khảo tại repo kit, không chép vào project.

## Adoption boundary

- Adoption **không** authorize implementation của bất kỳ module nào (M1–M10), không duyệt architecture, dependency, dịch vụ ngoài hay chi tiêu.
- Adoption không duyệt Implementation Authorization Boundary nào. Thứ tự và trạng thái: `docs/decisions/ADR-001-mvp-architecture-and-phasing.md`; bản nháp P0.1 / P1a ở `docs/decisions/` (PROPOSED).
- Không sửa Framework Core. Rule riêng project đặt ở `docs/ai/project-profile.md` hoặc decision record.

## Verification status

- `node scripts/framework-check.mjs`: PASS trên branch `feature/p0-research-bootstrap` (2026-10-23; kết quả chi tiết ở `docs/tasks/P0-research-bootstrap.md`, mục Result).
- `node scripts/product-check.mjs docs/product/requirements/REQ-001-animation-studio-mvp.md`: bản của kit có lỗi regex (escape `\\.` / `\\n`) nên FAIL giả. Đã sửa ở P0.1; REQ-001 PASS. Cần báo upstream (`docs/tasks/P0.1-checker-quality-gate-ci.md`, mục Result).
- `node scripts/quality-gate.mjs`: PASS (P0.1; framework-check, product-check, `node --test`, file cấm).
- Pilot S1 (`docs/install-new-project.md` bước 8): **chưa làm**. Adoption chưa được tuyên bố hoàn tất cho tới khi có task S1 đầu tiên ở P1.
