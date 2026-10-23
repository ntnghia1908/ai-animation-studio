# P1a Implementation Authorization Boundary — Offline vertical slice

| Metadata | Value |
|---|---|
| Status | PROPOSED — chờ HUMAN LEAD |
| Date | 2026-10-23 |
| Basis | `docs/decisions/ADR-001-mvp-architecture-and-phasing.md` (Option A, A3 ràng buộc tăng trưởng, A4 thứ tự) |
| Requirement | `docs/product/requirements/REQ-001-animation-studio-mvp.md` (một phần, xem §7) |
| Prerequisite | P0.1 đã merge (quality gate + CI) |

Bản nháp không authorize gì. Có hiệu lực khi HUMAN LEAD đổi Status thành `ACCEPTED` và trả lời các decision ở §6.

## 1. Mục tiêu

Ra **một đoạn phim 16:9 có chuyển động, dài 30–60 giây**, từ một truyện ngắn, với ảnh và giọng nhập tay. Đi theo đúng luồng animatic-first, chỉ bằng CLI + FFmpeg trên server, không GPU, không AI provider, không tốn tiền. HUMAN LEAD xem video này để quyết P1b.

## 2. Luồng của slice

```text
story.txt + rights ─► import-story ─┐
images/ (PNG, layer) ─┐             │
audio/ (WAV/MP3)  ────┴► import-assets ─► asset manifest (sha256, nguồn, license)
                                    │
                 shots.json (viết tay hoặc ORCHESTRATOR soạn giúp trong chat)
                                    ▼
                     animatic  ─► animatic.mp4   (ảnh tĩnh + giọng + phụ đề, cắt theo timing)
                                    │  HUMAN LEAD xem
                                    ▼
                     render    ─► film.mp4      (camera move, 1 shot parallax, transition, nhạc nền)
```

- `shots.json` (5–8 shot), mỗi shot có:
  - ảnh hoặc các layer;
  - đoạn audio hoặc thời lượng;
  - text phụ đề;
  - chuyển động camera: `static | push_in | pull_out | pan_left | pan_right | parallax`;
  - transition.
- Tên lệnh CLI là đề xuất; task contract sẽ chốt.

## 3. Trong boundary

- Package `src/animation_studio/`, **chỉ** các phần slice cần:
  - workspace + atomic IO + hashing (tái dùng từ youtube-auto-short theo `docs/research/REUSE_ASSESSMENT.md`, ghi nguồn);
  - import truyện, kèm provenance tối thiểu: nguồn, tác giả, dịch giả, quyền;
  - import asset, kèm manifest;
  - đọc / validate `shots.json`;
  - dựng animatic;
  - render phim bằng FFmpeg:
    - camera move mượt (upscale trước khi crop để tránh rung kiểu `zoompan`);
    - một shot parallax 2–3 layer PNG;
    - crossfade;
    - phụ đề tiếng Việt (font Be Vietnam Pro, OFL);
    - nhạc nền giảm âm lượng khi có giọng;
    - chuẩn hóa loudness;
  - tự kiểm output (§5 phần tự động).
- CLI (`python -m animation_studio …`). **Không Web UI.**
- Resume đơn giản: không render lại shot mà input (hash) và tham số không đổi.
- Test pytest với ảnh / audio tổng hợp bằng FFmpeg; không gọi mạng / dịch vụ.
- Dependency: conda env (D-04 ACCEPTED), Python 3.12 (đề xuất), `pytest` (dev). Ngoài ra chỉ FFmpeg / ffprobe hệ thống. **Không** FastAPI, Pillow, ComfyUI, TTS engine.
- Mở rộng quality gate của P0.1 để chạy pytest.
- Tài liệu: module map trong project-profile, current-state, task contract, hướng dẫn chạy ngắn trong `README.md`.

## 4. Ngoài boundary

- Review Studio / Web UI, LLM screenwriter, TTS, router, provider adapter, budget guard, ledger chi phí đầy đủ, lip-sync, GPU / local AI, Figma: tất cả để **P1b**, sau khi xem video P1a.
- Sinh ảnh hay giọng bằng AI trong code. HUMAN LEAD có thể tự tạo bằng công cụ ngoài rồi nhập vào như asset, ghi nguồn và license.
- Phim pilot đầy đủ 60–90 s, 12–16 shot (sau P1a).
- Package dùng chung với youtube-auto-short.

## 5. Quality gate của P1a (exit)

**Tự động** (chạy trong test và sau mỗi lần render):

| Kiểm tra | Ngưỡng đề xuất |
|---|---|
| Định dạng | 1920×1080, 16:9, fps cố định (đề xuất 30), H.264 + AAC |
| Thời lượng | bằng tổng thời lượng shot ±0,1 s; trong 30–60 s |
| Đồng bộ phụ đề | mỗi dòng nằm trong khung thời gian của shot / đoạn audio tương ứng (±100 ms) |
| Khung đen / đứng hình ngoài ý muốn | không có đoạn đen hoặc đóng băng > 0,5 s ngoài transition (`blackdetect` / `freezedetect`) |
| Loudness | integrated khoảng −16 LUFS ±1 (`ebur128`) |
| Tái tạo | render lại cùng input → cùng thời lượng, thứ tự shot và audio PCM hash |

**HUMAN LEAD chấm** (thang 1–5, ghi vào task Result):
- chuyển động camera mượt (không rung / giật);
- phụ đề tiếng Việt dễ đọc, đúng dấu;
- nhịp kể khớp giọng;
- shot parallax có chiều sâu thuyết phục;
- tổng thể: "đủ làm phim mẫu".

Ngưỡng đề xuất: không mục nào < 3 và mục tổng thể ≥ 4. Nếu không đạt thì lặp lại trong P1a, chưa mở P1b.

## 6. Decision cần HUMAN LEAD trước khi ACCEPTED

| ID | Câu hỏi | Khuyến nghị |
|---|---|---|
| D-04 | Runtime trên server | Conda: **ACCEPTED**. Còn lại đề xuất: env riêng `animation-studio`, Python 3.12, `pyproject.toml` hatchling src-layout, `pip install -e ".[dev]"`, test `python -m pytest -q` |
| D-08 | Truyện + asset pack cho P1a (HUMAN LEAD quyết trên server; chỉ cần trước P1a.4) | Một truyện ngắn có quyền rõ ràng. HUMAN LEAD chuẩn bị 1–2 nhân vật, 1–2 nền, ảnh cho 5–8 shot (1 shot có 2–3 layer PNG nền trong suốt), file giọng đọc. Trong lúc chờ, dev dùng asset tổng hợp |
| P1a-1 | Vị trí workspace trên server | Thư mục ngoài repo, cấu hình bằng `config.toml` (gitignored) |
| P1a-2 | Ngưỡng quality gate ở §5 | Chấp nhận như đề xuất hoặc chỉnh |

## 7. Truy vết tới REQ-001

| REQ-001 | Mức trong P1a |
|---|---|
| FR-001 Story Library | tối thiểu (import + provenance) |
| FR-008 Manual import | có (ảnh, layer, audio) |
| FR-004 Voice & timing | chỉ nhập audio + đo thời lượng |
| FR-005 Storyboard & animatic | có (từ `shots.json`) |
| FR-006 Routing | chỉ phương thức 1 (still + camera / parallax), chọn tay trong `shots.json` |
| FR-009 Timeline & render | có (tối thiểu) |
| FR-012 Resume | đơn giản |
| AC-006 Reproducible render | có |
| FR-002, FR-003, FR-007, FR-010, FR-011 | không (P1b) |

## 8. Vận hành

- `dual-agent` (Claude Code ORCHESTRATOR → subagent `implementer`), writer = 1.
- Dự kiến 3–4 task:
  1. skeleton + workspace + import;
  2. animatic;
  3. motion render + parallax;
  4. quality gate output + pilot run.
- Ngân sách diff ≤ khoảng 800 dòng app / PR.
- Branch `feature/p1a-<task>`; READY → push + PR; HUMAN LEAD merge.
