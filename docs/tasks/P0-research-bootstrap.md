# Task: P0 — Research & Framework Bootstrap

## Status / Approval

- Status: READY
- Type: DOC
- Change class: S2
- Owner: HUMAN LEAD
- Execution profile: single-agent
- Orchestrator: claude-code
- Human Lead: HUMAN LEAD
- Authorization mode: boundary
- Authorization source: HUMAN LEAD kickoff "AI Animation Studio — Master Project Kickoff" 2026-10-23, §12 (P0 only; docs / research; không implementation)
- Parallel group: —
- Owned paths: root framework files, `docs/`, `scripts/` (từ kit), `adapters/`, `.claude/`, `.gitattributes`
- Dependencies: none
- Base commit / branch: `f88b8b8` / `feature/p0-research-bootstrap`
- Human Lead approval: inherited from kickoff (P0 scope); execution profile single-agent phê chuẩn hồi tố (D-14 ACCEPTED 2026-10-23)
- Implementation authorized: YES

Lifecycle: `task` mode = `DRAFT → APPROVED → IN_PROGRESS → READY`; `boundary` mode = `DRAFT → IN_PROGRESS → READY`. DONE suy ra từ Git sau khi merge.

## Goal

Repository có framework v4.4 đã adopt và cấu hình cho project, cùng bộ tài liệu P0 (research, requirement, architecture proposal, roadmap, authorization draft) để HUMAN LEAD ra quyết định P1.

## Scope

- In scope: 11 deliverable của kickoff §12; nghiên cứu web; phân tích video tham khảo (chỉ đọc, không commit); đọc youtube-auto-short (chỉ đọc).
- Out of scope: source code ứng dụng; dependency; gọi API trả phí; sửa Framework Core; sửa youtube-auto-short; merge.

## Authority / key decisions

- Kickoff HUMAN LEAD §1–§13. Không tạo decision `ACCEPTED`; mọi đề xuất ghi là PROPOSED / PROPOSAL.
- Single-agent: ORCHESTRATOR viết trực tiếp vì việc chỉ gồm tài liệu / nghiên cứu cần toàn bộ ngữ cảnh. HUMAN LEAD phê chuẩn hồi tố (D-14, 2026-10-23).

## Implementation approach

- Cài kit theo `docs/install-new-project.md` của kit (thủ công vì repo có sẵn `README.md`); điền Project Layer.
- Nghiên cứu: web search / fetch tài liệu chính thức và nguồn thứ cấp, gắn nhãn mức bằng chứng; ffprobe / scene detect / contact sheet cho video tham khảo.

## Phải giữ nguyên

- `README.md` gốc (chỉ đổi line ending sang LF).
- Framework Core nguyên văn.

## Code bị thay / xóa

- không có

## Acceptance Criteria

1. Có đủ 11 deliverable của kickoff §12 ở đúng path (hoặc path canonical tương đương).
2. `node scripts/framework-check.mjs` PASS.
3. Tài liệu research phân biệt quan sát / nguồn chính thức / thứ cấp / giả định / giả thuyết và ghi nguồn + ngày.
4. Architecture proposal có 2–3 option, trade-off, khuyến nghị, và không gán nhãn decision accepted.
5. Không có source code ứng dụng, dependency hay media bên thứ ba trong diff.

## Required verification

- `node scripts/framework-check.mjs` — AC2.
- `git diff --stat main...HEAD` và `git ls-files` — AC1, AC5 (không có `*.mp4`, không có `src/`).
- Rà soát tài liệu (review pass riêng) — AC3, AC4.

Tất cả required verification phải chạy và PASS trước READY.

## Manual test checklist (Tech Lead)

Không chạm database, security model hay public API contract. Manual review của HUMAN LEAD là đọc PR P0.

- [x] HUMAN LEAD đọc báo cáo; quyết định ghi ở `docs/decisions/ADR-001-mvp-architecture-and-phasing.md` A5.

## Handoff

Không dùng.

## Result

- Main changes:
  - Adopt framework v4.4 (kit @ `7496eac`).
  - 4 báo cáo research.
  - REQ-001 (NEEDS_CLARIFICATION).
  - Architecture proposal (Option A đề xuất).
  - Roadmap.
  - P1 authorization draft (PROPOSED).
- Tests: AC1 → kiểm path; AC2 → framework-check; AC3 / AC4 → review; AC5 → `git ls-files`. Kết quả ở mục Review.
- Diff + / − (app, test): app 0 / 0, test 0 / 0 (chỉ tài liệu và file framework).
- Helper mới: không có.
- Verification:
  - `node scripts/framework-check.mjs` PASS (exit 0), 20 dòng PASS gồm task contract và decision record.
  - REQ-001 PASS với bản sao tạm của `product-check.mjs` đã sửa escape. Bản gốc của kit FAIL với mọi file.
  - `git ls-files` không có `*.mp4` và không có `src/`.
- Review: self-review single-agent trước READY. Đã kiểm chéo số liệu giữa research / cost benchmark / REQ, nhãn bằng chứng, và chắc chắn không có nhãn ACCEPTED.
- Important findings / decisions:
  - Video tham khảo khoảng 19 shot/phút, có dấu vết chữ Hán in trong hình → có thể là bản Việt hóa của tác phẩm bên thứ ba.
  - Laptop dev không có GPU NVIDIA.
  - Figma Weave là plan riêng, không thuộc Education.
- Known limitations:
  - Không chạy được model nào; chất lượng model là giả thuyết.
  - Giá nhiều provider là nguồn thứ cấp.
  - Chưa đăng nhập Figma Education.
  - Finding ngoài scope: `scripts/product-check.mjs` của kit có lỗi regex (`\\.`, `\\n` trong regex literal) nên luôn FAIL. Báo HUMAN LEAD, không sửa.
- HUMAN LEAD review (2026-10-23): chấp nhận research + Option A; tách P1 thành P0.1 → P1a → P1b → `docs/decisions/ADR-001-mvp-architecture-and-phasing.md`. D-01, D-14 ACCEPTED.
- PR: #1 (merged `49295d0`), branch `feature/p0-research-bootstrap`.
