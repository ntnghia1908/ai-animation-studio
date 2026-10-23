# Architecture Proposal — AI Animation Studio MVP

| Metadata | Value |
|---|---|
| Status | PROPOSAL — NOT ACCEPTED |
| Date | 2026-10-23 |
| Requirement | `docs/product/requirements/REQ-001-animation-studio-mvp.md` (NEEDS_CLARIFICATION) |
| Task | `docs/tasks/P0-research-bootstrap.md` |

Không có mục nào trong file này là decision. Mục "Đề xuất" chỉ là khuyến nghị của ORCHESTRATOR. Decision cần HUMAN LEAD được đánh số D-xx và tổng hợp ở `docs/decisions/P1-IMPLEMENTATION-AUTHORIZATION-DRAFT.md` §6. Khi HUMAN LEAD chấp thuận, phần tương ứng chuyển thành decision record `ACCEPTED` riêng.

## 1. Driver kiến trúc

1. **Animatic-first:** dữ liệu và luồng phải cho phép dựng animatic rẻ trước khi sinh shot đắt.
2. **Provider-neutral:** domain trung tâm không biết Kling / Wan / ComfyUI; mọi model đi qua adapter.
3. **Truy vết và chi phí:** mỗi take có hồ sơ đầy đủ; phải có budget guard.
4. **Resume / reproducible:** artifact trung gian có hash; chạy lại chỉ làm phần thay đổi.
5. **Local first, một người vận hành:** đơn giản để vận hành trên laptop dev và một server; GPU worker là tùy chọn.
6. **Nhỏ nhất có hiệu quả:** tránh framework frontend lớn, tránh hạ tầng phân tán khi chưa cần.

## 2. Option A — Modular monolith Python + file workspace + LAN web (Đề xuất)

```text
                       ┌──────────────── animation_studio (Python package) ────────────────┐
 CLI ───────────────►  │  domain: Project, Story, Adaptation, Character, Asset, Scene,      │
 Web (FastAPI, LAN) ─► │          Shot, Take, Approval, CostEntry, Timeline                  │
                       │  services: story · script · bible · voice · storyboard · router ·   │
                       │            render · review · ledger                                 │
                       │  ports:  LLMPort · TTSPort · ImagePort · VideoPort · StoragePort     │
                       └───────┬───────────────┬────────────────┬──────────────┬────────────┘
                               │               │                │              │
                      Ollama (urllib)   TTS adapter     Image/Video adapters    FFmpeg (subprocess)
                                        (local / import)  ├─ ManualImport (P1)
                                                          ├─ StillCamera (P1, FFmpeg)
                                                          ├─ ComfyUIWorker (P2, HTTP → GPU node)
                                                          └─ PaidProvider<X> (P3, budget guard)
 Storage: workspace/<project_id>/  (JSON manifest + asset files theo hash, ghi atomic)
```

- **Kiểu:** một package Python (src-layout), các module M1–M10 là subpackage; CLI và web cùng gọi một service layer.
- **Lưu trữ:** file workspace ngoài git.
  - `project.json`, `story/`, `script/rev-N.json`, `bible/`, `shots/<shot_id>/takes/<take_id>/{take.json, output.*}`, `timeline.json`, `ledger.jsonl`.
  - Ghi atomic. Asset định danh bằng sha256. Pattern tái dùng từ youtube-auto-short (`docs/research/REUSE_ASSESSMENT.md`).
- **Job:** hàng đợi đơn giản trong process (1 worker CPU). Việc GPU (P2) chạy qua worker kéo việc theo giao thức lease kiểu CP13.1 của youtube-auto-short.
- **Render:** `timeline.json` → FFmpeg filtergraph (zoompan / crop / overlay cho camera và parallax, `concat`, `amix`, subtitle ASS). Output kiểm bằng ffprobe.
- **Web:** FastAPI + template HTML server-render + JS nhỏ; mật khẩu + cookie; chỉ LAN.
- **Ưu:** đơn giản nhất; tái dùng được nhiều pattern đã chạy thật; dễ test (fake adapter); resume tự nhiên nhờ manifest; không cần DB server.
- **Nhược:** query thống kê (ledger) bằng JSON kém hơn DB; khó mở rộng nhiều người dùng đồng thời (không phải mục tiêu); phải tự giữ tính toàn vẹn khi ghi đồng thời (một writer).

## 3. Option B — ComfyUI-centric

```text
 Studio (mỏng: story/script/review) ──► ComfyUI API (workflow JSON cho mọi bước ảnh/video/TTS) ──► output
                                       └─ Custom nodes cho camera/parallax/compose
```

- **Kiểu:** dùng ComfyUI làm engine trung tâm; mọi bước sinh và cả composition là node graph; Studio chỉ quản lý truyện, review và gọi workflow.
- **Ưu:** tận dụng hệ sinh thái node (Wan, Qwen-Image-Edit, LoRA, lip-sync); thử nghiệm model mới rất nhanh.
- **Nhược:**
  - Domain (shot, approval, ledger, provenance) bị đẩy vào workflow JSON khó kiểm soát.
  - Phụ thuộc chặt vào một runtime GPU, trong khi laptop dev không chạy được.
  - Custom node chung process có thể kéo theo ràng buộc GPL-3.0 [A, cần kiểm license ComfyUI].
  - Provider trả phí phải đi qua node của bên thứ ba.
  - Timeline / subtitle / mix audio trong ComfyUI kém hơn FFmpeg.
  - Trái với "không phụ thuộc độc quyền".

## 4. Option C — Service-based (DB + queue + SPA)

```text
 SPA (React) ─► API service ─► PostgreSQL
                    │
                    └─► Queue (Redis) ─► workers: llm · tts · image · video · render
```

- **Ưu:** mở rộng tốt, nhiều người dùng, query ledger mạnh, worker phân tán.
- **Nhược:** quá nặng cho một người vận hành; nhiều dependency (Postgres, Redis, Node toolchain); vận hành và test tốn kém; trái "keep UI simple". Không cần ở MVP.

## 5. So sánh

| Tiêu chí | A. Modular monolith | B. ComfyUI-centric | C. Services |
|---|---|---|---|
| Thời gian ra pilot | **nhanh** | trung bình | chậm |
| Provider-neutral | **cao** | thấp | cao |
| Truy vết / approval / ledger | tốt (JSON) | yếu | **tốt nhất** |
| Chạy trên laptop dev không GPU | **có** | không | có (nặng) |
| Tái dùng youtube-auto-short | **cao** | thấp | trung bình |
| Dependency mới | ít (FastAPI, uvicorn, pytest; TTS riêng) | ComfyUI + custom nodes | nhiều |
| Mở rộng P4 (batch, phim dài) | đủ cho 1 người; có thể thêm SQLite | trung bình | **cao** |
| Rủi ro license | thấp | GPL cần kiểm | thấp |

## 6. Khuyến nghị

**Option A** cho MVP (P1–P3), dùng ComfyUI **như một adapter worker** ở P2 (lấy ưu điểm của B mà không đặt domain vào ComfyUI). Xem lại sau P3 xem có cần SQLite cho ledger / thống kê không; chưa cần Option C.

## 7. Thiết kế chi tiết đề xuất cho Option A

### 7.1 Domain model (khái niệm)

| Entity | Thuộc tính chính |
|---|---|
| `Project` | id, title, story_id, style_id, status, budget_cap |
| `Story` | id, source_text (bất biến), source, author, translator, category, rights, approval |
| `Adaptation` | story_id, revision, segments[] (text, kind = verbatim / paraphrase / invented), scenes[], approval |
| `Character` | id, name, description, wardrobe, palette, expressions[], reference_assets[], approval |
| `Asset` | sha256, kind (image / audio / video / layer), path, origin (tool, model, license), approval |
| `Scene` | id, location_asset, shots[] |
| `Shot` | id, order, narration / dialogue refs, duration, keyframe_asset, method (1–5), method_reason, override_by, status |
| `Take` | id, shot_id, adapter, provider, model, prompt, refs[], params, output_asset, est_cost, actual_cost, attempt, status, approval |
| `Approval` | target, decision, by, at, note |
| `CostEntry` | take_id, provider, unit, quantity, est / actual USD, approved_by |
| `Timeline` | ordered clips (shot → take), audio tracks, subtitles, transitions |

### 7.2 Port / adapter

```text
VideoPort.estimate(shot, params) -> CostEstimate
VideoPort.submit(shot, keyframe, prompt, params) -> JobRef
VideoPort.poll(JobRef) -> Status
VideoPort.fetch(JobRef) -> Asset
```

Adapter P1: `ManualImport`, `StillCamera` (FFmpeg). Adapter P2: `ComfyUIWorker`. Adapter P3: một `PaidProvider`.

Mọi adapter trả phí phải đi qua `BudgetGuard`:
- `enabled=false` mặc định;
- trần dự án / tháng;
- approval token cho từng lần submit;
- `max_attempts`;
- ghi `CostEntry` trước và sau.

### 7.3 Router (M6)

Luật đề xuất, có giải thích, không dùng ML:

| Thuộc tính shot | Phương thức đề xuất |
|---|---|
| `motion_level` = none / camera | 1 |
| `motion_level` = subtle, có keyframe | 3 nếu có GPU worker, ngược lại 1 |
| `motion_level` = complex | 4, nhưng chỉ khi thỏa điều kiện escalation (`docs/research/ANIMATION_WORKFLOW_RESEARCH.md` §7) |
| Có clip ngoài | 5 |

Lưu `method_reason`. HUMAN LEAD override được.

### 7.4 Dependency đề xuất cho P1 (mỗi mục là decision gate)

| Library | Purpose | Ghi chú |
|---|---|---|
| Python 3.12, `pyproject.toml` (hatchling) | runtime + packaging | như youtube-auto-short; env manager (conda / venv / uv) do HUMAN LEAD chọn |
| FFmpeg / ffprobe (system) | render, probe, animatic | đã có trên laptop |
| `fastapi` + `uvicorn` | Review Studio LAN | cùng pin với youtube-auto-short |
| `pytest` (+ `httpx` cho TestClient) | test | dev |
| `tomllib` (stdlib) | config | |
| Ollama qua `urllib` | M2 Screenwriter | không thêm dependency |
| TTS engine local (ứng viên: VieNeu-TTS v3) | M4 | riêng decision D-06, sau E4; có thể bắt đầu P1 với "nhập audio" |
| `Pillow` (tùy chọn) | xử lý ảnh / layer, thumbnail | chỉ thêm nếu FFmpeg không đủ |

### 7.5 Layout đề xuất

```text
src/animation_studio/{domain,story,script,bible,voice,storyboard,router,providers,render,web,ledger,storage}/
tests/
config.example.toml        # config.toml gitignored
workspace/                 # ngoài git (đường dẫn cấu hình)
```

## 8. Rủi ro

- Phong cách không đồng nhất giữa shot tĩnh và shot i2v. Giảm bằng cách dùng cùng keyframe làm frame đầu, cùng LUT / grain ở bước render.
- GPU worker chưa sẵn sàng. Giảm bằng cách để P1 không cần GPU: ảnh nhập tay / sinh ngoài, rồi `StillCamera`.
- Lặp lại god-file như project cũ. Giảm bằng router web tách từ đầu, rule FW-GROWTH-01 và ngân sách diff / PR.

## 9. Decision cần HUMAN LEAD (liên quan kiến trúc)

D-02 (chọn option), D-03 (lưu trữ file JSON so với SQLite), D-04 (runtime / env), D-05 (web stack + security LAN), D-06 (TTS), D-07 (GPU worker / server).
