# Project Profile — AI Animation Studio

| Metadata | Value |
|---|---|
| Status | CURRENT |
| Project stage | P0 — Research & Framework Bootstrap (chưa có source ứng dụng; P1 chưa được authorize) |

Canonical owner cho: project là gì, authority order, module map, project policy, integration mechanism, execution profile được phép, setup và Test policy.

## 1. Project

- **Mục tiêu:** hệ thống AI Animation Production Studio chuyển truyện có sẵn (giai đoạn đầu: Liêu Trai Chí Dị, truyện dân gian, truyền thuyết, truyện ngắn) thành phim hoạt hình 2D kể chuyện bằng tiếng Việt, phong cách 2D Á Đông. Dài hạn: truyện nhân quả, đạo đức, khuyến thiện và nội dung Phật giáo do HUMAN LEAD cung cấp.
- **Triết lý sản xuất:** Hybrid, Local First, Quality First, Cost Aware. Không đặt mục tiêu tự động hóa 100% nếu chất lượng giảm. Không phụ thuộc độc quyền một nhà cung cấp.
- **Story-agnostic:** không hard-code riêng Liêu Trai hay Phật giáo; thể loại / quy tắc riêng là cấu hình hoặc template.
- **Trong phạm vi hiện tại (P0):** nghiên cứu, bootstrap framework, requirement nháp, đề xuất architecture / roadmap / authorization boundary P1.
- **Ngoài phạm vi hiện tại:** mọi implementation; gọi API trả phí; đăng video.
- **Tham chiếu bên ngoài (KHÔNG phải source of truth):**
  - `ntnghia1908/youtube-auto-short`: chỉ đọc; nguồn pattern để tái dùng chọn lọc (`docs/research/REUSE_ASSESSMENT.md`). Không phải runtime dependency.
  - `ntnghia1908/ai-dev-framework`: nguồn snapshot framework (`FRAMEWORK_ADOPTION.md`); không có runtime dependency.
  - Video tham khảo "Mượn thọ – Mộng Hoạt Hình": chỉ để nghiên cứu nhịp dựng và phong cách, không sao chép, không commit vào repo.

## 2. Authority order

1. HUMAN LEAD decisions, approved task contracts và decision record `ACCEPTED` trong `docs/decisions/`. Hiện **chưa có** decision `ACCEPTED` nào của project; `docs/decisions/P1-IMPLEMENTATION-AUTHORIZATION-DRAFT.md` là `PROPOSED`.
2. `docs/ai/workflow.md`, `docs/ai/execution-profiles.md` và file này cho workflow / policy.
3. Requirement `READY` trong `docs/product/requirements/` cho hành vi sản phẩm (READY ≠ authorization). REQ-001 hiện là `NEEDS_CLARIFICATION`.
4. Source code và tests hiện hành (chưa có).
5. `docs/workflow/current-state.md` chỉ là operational state, không phải authority.
6. `docs/research/*`, `docs/architecture/ARCHITECTURE_PROPOSAL.md`, `docs/roadmap/IMPLEMENTATION_ROADMAP.md`: bằng chứng và đề xuất, **không phải** authority cho tới khi HUMAN LEAD chuyển phần liên quan thành decision record.
7. `README.md` và tài liệu onboarding chỉ mô tả / cross-link.

Chưa có authority cho: architecture, storage / schema, dependency, security model của web UI, public API, provider AI trả phí, chính sách nội dung Phật giáo. Phải tạo authority tương ứng trước khi implement phần chạm vào các boundary này.

## 3. Module map

Tất cả đều **planned**; chưa có module nào implemented. Ranh giới đề xuất ở `docs/architecture/ARCHITECTURE_PROPOSAL.md` (chưa được chấp thuận).

| Path (đề xuất) | Vai trò | Trạng thái | Rule riêng |
|---|---|---|---|
| `src/animation_studio/story/` | M1 Story Library: nguồn truyện, provenance, quyền sử dụng | planned | REQ-001; decision chưa có |
| `src/animation_studio/script/` | M2 AI Screenwriter: cải biên, scene / shot list | planned | REQ-001 |
| `src/animation_studio/bible/` | M3 Character & Visual Bible | planned | REQ-001 |
| `src/animation_studio/voice/` | M4 Voice & Timing | planned | REQ-001; engine TTS = decision gate |
| `src/animation_studio/storyboard/` | M5 Storyboard & Animatic | planned | REQ-001 |
| `src/animation_studio/router/` | M6 Shot Production Router | planned | REQ-001 |
| `src/animation_studio/providers/` | M7 Animation Generation adapters | planned | provider = decision gate |
| `src/animation_studio/render/` | M8 Timeline & Renderer (FFmpeg) | planned | REQ-001 |
| `src/animation_studio/web/` | M9 Review Studio (LAN) | planned | security model = decision gate |
| `src/animation_studio/ledger/` | M10 Cost & Asset Tracking | planned | REQ-001 |
| `docs/research/` | báo cáo nghiên cứu P0 | implemented (tài liệu) | không phải authority |
| `docs/` khác | authority, task, decision, workflow | theo từng mục | framework |
| `scripts/` | tooling của framework | implemented (từ kit) | framework |

Chỉ tạo `<module>/AGENTS.md` khi module có convention riêng đủ rõ.

## 4. Project policy

- Ngôn ngữ: trao đổi với HUMAN LEAD và tài liệu nội bộ bằng tiếng Việt; tên file, identifier, code và tên tài liệu bằng tiếng Anh.
- Dependency mới, dịch vụ ngoài (kể cả bản free / trial cần đăng ký tài khoản) và model AI mới là decision gate (`docs/ai/workflow.md` §3).
- **Chi tiêu:** không gọi API trả phí, mua credit hay subscription khi chưa có HUMAN LEAD approval rõ ràng, ghi lại cho từng lần (provider, model, trần chi phí). Mọi lần sinh nội dung trả phí phải có ước tính chi phí trước và giới hạn retry.
- **Nguồn nội dung:** truyện gốc và bản cải biên lưu riêng; ghi provenance (nguồn, tác giả, dịch giả, quyền sử dụng, lịch sử cải biên). Nội dung Phật giáo: không tự tạo lời Phật dạy rồi gán cho kinh điển; phân biệt nguyên văn / diễn giải / sáng tác; HUMAN LEAD duyệt trước khi sản xuất.
- **Bản quyền:** không dùng footage, frame hay nhân vật của video bên thứ ba làm asset hoặc reference sinh ảnh khi chưa có quyền.
- Repository public: không commit credential, token, media nguồn có bản quyền hay output lớn. Output sinh ra đặt ngoài git (vị trí cụ thể do decision P1 chốt).
- Figma là công cụ tùy chọn; Studio không được phụ thuộc vào Figma (`docs/research/FIGMA_INTEGRATION_ASSESSMENT.md`).
- Không sửa Framework Core.

## 5. Integration mechanism

- Branch: `feature/<scope>`, `fix/<scope>`, `docs/<scope>`; target `main`.
- Commit cục bộ được phép trong task đã authorized (task approval hoặc boundary).
- Push + mở Pull Request: được phép khi task đạt READY. P0 do HUMAN LEAD yêu cầu trực tiếp trong kickoff §12.
- **Merge do HUMAN LEAD quyết.** Agent không merge, không push thẳng `main`.
- Với `governance.taskAuthorization=boundary`, task nằm hoàn toàn trong boundary đã được HUMAN LEAD chấp thuận không cần APPROVE TASK riêng; vẫn dừng ở integration gate.

## 6. Ownership

HUMAN LEAD giữ: scope, architecture, dependency, provider / chi tiêu, chính sách nội dung và bản quyền, duyệt nội dung trước sản xuất, chọn truyện, approval từng giai đoạn (script, bible, animatic, shot, render), integration và milestone. Agent chỉ thực thi bên trong boundary đã duyệt.

## 7. Execution profiles

- Được phép: `dual-agent` (ưu tiên), `single-agent` (khi HUMAN LEAD duyệt cho task).
- Profile của từng task là source of truth; không suy đoán profile từ tool / model.

### Governance mode

Project chọn `task` (cần APPROVE TASK) hoặc `boundary` (HUMAN LEAD cấp Implementation Authorization Boundary một lần). Ghi lựa chọn trong `framework.config.json` và không tự đổi giữa phiên.

Project này dùng `boundary` (`framework.config.json`). Chưa có boundary nào được duyệt.

### Execution profile ưu tiên: native dual-agent

- Ưu tiên `dual-agent` với subagent **native của cùng tool** đang mở; `single-agent` vẫn dùng được khi HUMAN LEAD duyệt cho task. Profile của task đã duyệt không đổi chỉ vì mở CLI khác; native delegation không khả dụng thì xin duyệt phương án khác, không tự hạ profile.
- Mapping: Claude Code main session (ORCHESTRATOR) → subagent `implementer`; Codex main session (ORCHESTRATOR) → built-in native worker. Không hard-code model ID; model thực tế do runtime/user quyết và phải ghi nhận khi pilot (xem README adapter).
- `governance.maxParallelImplementers` (tối đa 3) chỉ là **trần cấu hình**. Số writer đồng thời thực tế là **1** cho tới khi HUMAN LEAD duyệt riêng một pilot worktree (mỗi IMPLEMENTER một branch/worktree, ownership không giao nhau, dependency thỏa, verification độc lập — `docs/ai/workflow.md` §5). Subagent dùng chung quyền của process cha; thread riêng không phải worktree.
- `boundary` mode là chế độ governance, không phải authorization: project mới **chưa có boundary được duyệt** nên phải DỪNG, không sửa source project cho tới khi HUMAN LEAD định nghĩa và duyệt boundary (hoặc duyệt task theo `task` mode).
- Handoff: đổi CLI giữa các task độc lập dùng bootstrap repository + authorization của task mới. Đổi giữa chừng một task cần HUMAN LEAD duyệt rõ; handoff prompt theo `docs/ai/workflow.md` §9. Trước khi nhận: kiểm boundary/task, branch/base/HEAD, `git status --short --untracked-files=all`, `git worktree list` và xác nhận session cũ đã dừng; writer mơ hồ → STOP/BLOCKED.

### Danh sách IMPLEMENTER

Canonical owner cho việc tool nào được làm IMPLEMENTER của task `dual-agent`; HUMAN LEAD duyệt danh sách adapter được phép. Tên model / vendor chỉ ghi ở đây và ở adapter, không ghi vào Core.

Danh sách dưới đây là **đề xuất ban đầu**, chờ HUMAN LEAD xác nhận khi duyệt boundary P1.

| Adapter | Điểm mạnh | Giới hạn | Dùng khi | Dự phòng |
|---|---|---|---|---|
| `claude-code` (subagent `implementer`) | tích hợp sẵn với ORCHESTRATOR Claude Code, không cần CLI riêng | tiêu hạn mức của session chính | mặc định cho task P1 | `codex` |
| `codex` (`codex exec` / native worker) | dùng hạn mức gói Codex; vendor khác nên review chéo được | chưa pilot trong project này; sandbox giới hạn mạng / loopback | task tự chứa, spec rõ; reviewer thứ hai cho task S2 | `claude-code` |

Cách chọn:

- ORCHESTRATOR chọn IMPLEMENTER lúc viết task contract và ghi vào field `Implementer`. Trong `boundary` mode, lựa chọn này không cần APPROVE TASK riêng; vẫn phải nằm trong danh sách adapter được phép.
- Không đổi IMPLEMENTER giữa task (một writer trên một branch), trừ dự phòng đã khai ở bảng (hạn mức, auth, lỗi tool, circuit breaker); ghi việc đổi vào Result.
- Nhiều IMPLEMENTER chạy song song chỉ khi task graph chứng minh độc lập, mỗi người một branch/worktree, ownership không giao nhau và không vượt `governance.maxParallelImplementers` (`docs/ai/workflow.md` §5). Khuyến nghị 2–3 khi thực sự có thể song song; không tạo parallelism giả.

## 9. Setup / tools

- Máy dev hiện tại (2026-10-23): laptop Windows 11, Intel Iris Xe (không có GPU NVIDIA), 16 GB RAM, Node 24, Python 3.13, FFmpeg build 2026-09, WSL Ubuntu (đang dừng). Chỉ dùng để phát triển. Production / GPU worker sẽ chạy trên server; cấu hình server chưa được xác nhận cho project này (`docs/research/PRODUCTION_COST_BENCHMARK.md` §Hardware).
- Runtime, package manager và dependency của ứng dụng: **chưa chốt**, là decision gate của P1 (đề xuất trong `docs/architecture/ARCHITECTURE_PROPOSAL.md`).

Framework checker: `node scripts/framework-check.mjs`.

### Test policy

Canonical owner; áp dụng cho mọi IMPLEMENTER bất kể tool.

- Trong vòng sửa: chạy test liên quan tới thay đổi (file hoặc bộ lọc theo tên), ưu tiên dừng ở lỗi đầu tiên với traceback ngắn.
- Toàn bộ suite: một lần trước khi báo READY và một lần sau mỗi vòng fix review; không chạy toàn bộ sau từng lần sửa.
- Lệnh chuẩn chạy toàn bộ suite: chưa có (chưa có source / test). Đề xuất cho P1: `python -m pytest -q`; chốt cùng decision runtime P1. Trong P0 chỉ có `node scripts/framework-check.mjs`.
- Test không được gọi dịch vụ thật (API AI trả phí, Ollama, mạng ngoài); provider dùng fake / fixture.
- Không nới `docs/ai/workflow.md` §7: required verification trong task contract vẫn phải chạy và PASS trước READY.
