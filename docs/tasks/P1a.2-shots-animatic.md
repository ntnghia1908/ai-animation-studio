# Task: P1a.2 — `shots.json` + animatic

## Status / Approval

- Status: IN_PROGRESS
- Type: FEATURE
- Change class: S1
- Owner: HUMAN LEAD
- Execution profile: dual-agent
- Orchestrator: claude-code
- Implementer: codex (`codex exec`, effort high) — task tự chứa, spec rõ, chỉ FFmpeg + stdlib, không cần socket; dự phòng `claude-code`
- Human Lead: HUMAN LEAD
- Authorization mode: boundary
- Authorization source: docs/decisions/P1a-VERTICAL-SLICE-AUTHORIZATION-DRAFT.md (ACCEPTED, HUMAN LEAD 2026-10-23) §2, §3
- Parallel group: —
- Owned paths: `src/animation_studio/shots.py`, `src/animation_studio/animatic.py`, `src/animation_studio/__main__.py`, `src/animation_studio/media.py`, `src/animation_studio/hashing.py`, `src/animation_studio/fonts/`, `tests/conftest.py`, `tests/test_shots.py`, `tests/test_animatic.py`, `README.md`, `docs/ai/project-profile.md` (module map), `docs/workflow/current-state.md`, file này
- Dependencies: P1a.1 merged (PR #6)
- Base commit / branch: `a14e84d` (main sau merge PR #7) / `feature/p1a-animatic`
- Human Lead approval: accepted (HUMAN LEAD 2026-10-23)
- Implementation authorized: YES

Lifecycle: `boundary` mode = `DRAFT → IN_PROGRESS → READY`. DONE suy ra từ Git sau khi merge.

## Goal

HUMAN LEAD viết tay `<project>/shots.json` tham chiếu asset đã nhập, rồi chạy:

```text
python -m animation_studio animatic <project>
```

Kết quả: `<project>/animatic/animatic.mp4` (1920×1080, 30 fps, H.264 + AAC). Mỗi shot là ảnh tĩnh, có giọng đọc và phụ đề tiếng Việt, cắt thẳng theo thời lượng shot. HUMAN LEAD xem file này để chỉnh nhịp trước khi render có chuyển động (P1a.3).

## Scope

- In scope:
  - Schema `shots.json` v1, kèm validate có thông báo lỗi rõ (vị trí shot và trường bị lỗi).
  - Lệnh `animatic`: validate → dựng từng segment shot → nối → burn phụ đề.
  - Resume đơn giản: segment shot đã có, cùng key (sha input + tham số), thì không encode lại.
  - Font Be Vietnam Pro Regular + `OFL.txt` chép vào `src/animation_studio/fonts/` (SIL OFL, `youtube-auto-short@f47813d:src/auto_short/render/fonts/`).
- Out of scope:
  - Thực hiện camera move, parallax, transition, nhạc nền, chuẩn hóa loudness (P1a.3). Ở P1a.2 các trường này chỉ được validate; animatic luôn cắt thẳng, layer chồng tĩnh.
  - Quality gate output đầy đủ (blackdetect, freezedetect, ebur128) và kiểm 30–60 s (P1a.4).
  - Sinh `shots.json` tự động, Web UI.

## Authority / key decisions

- Boundary P1a §2 (luồng, danh sách trường shot), §3 (resume, font OFL, không Pillow).
- ADR-001 A3: chỉ tạo phần animatic cần.
- REQ-001 FR-005 (animatic từ `shots.json`), FR-004 (đo thời lượng audio), FR-012 (resume đơn giản).
- Quyết định cục bộ S1 (schema v1):

  ```json
  {
    "version": 1,
    "shots": [
      {
        "id": "s01",
        "image": "assets/images/<file>.png",
        "audio": "assets/audio/<file>.wav",
        "duration_s": 4.0,
        "subtitle": "Ngày xưa có một thư sinh…",
        "camera": "static",
        "transition": "cut"
      },
      {
        "id": "s02",
        "layers": ["assets/images/bg.png", "assets/images/fg.png"],
        "duration_s": 3.0,
        "camera": "parallax",
        "transition": "crossfade"
      }
    ]
  }
  ```

  - `id`: duy nhất, `^[a-z0-9][a-z0-9_-]{0,31}$`.
  - Có đúng một trong `image` / `layers`. `layers` có 2–3 phần tử, xếp từ dưới lên trên. Đường dẫn tương đối project và phải có trong `assets/manifest.json` với `kind` đúng.
  - Thời lượng: có `audio` thì thời lượng shot = `max(duration_s, audio duration_s)`; không có `audio` thì `duration_s` bắt buộc (> 0).
  - `subtitle`: tùy chọn, hiển thị suốt shot.
  - `camera` ∈ `static | push_in | pull_out | pan_left | pan_right | parallax` (mặc định `static`); `parallax` bắt buộc dùng `layers`. `transition` ∈ `cut | crossfade` (mặc định `cut`; áp cho chỗ nối với shot kế tiếp).
- Output: `<project>/animatic/{animatic.mp4, subtitles.srt, segments/<key>.mp4}`. `segments/` là cache, xóa được.

## Implementation approach

- `shots.py`: đọc + validate → danh sách shot đã resolve (đường dẫn tuyệt đối, thời lượng). Không thêm dependency (không jsonschema).
- `animatic.py`:
  - Segment / shot: ảnh (hoặc layer `overlay` chồng tĩnh) scale + pad về 1920×1080, `-r 30`, `-t <dur>`; audio là giọng `apad` tới đủ thời lượng, hoặc im lặng (`anullsrc`); libx264 (`-preset veryfast`, `yuv420p`) + AAC 48 kHz stereo. Mọi segment dùng tham số giống nhau để nối bằng concat demuxer `-c copy`.
  - Key segment = sha256 của `canonical_json` gồm sha asset, thời lượng và tham số encode. Đã có file thì bỏ qua. Ghi file tạm rồi rename.
  - Phụ đề: sinh `subtitles.srt` theo mốc tích lũy; burn bằng filter `subtitles` với `fontsdir` trỏ tới `fonts/`, `force_style` FontName=Be Vietnam Pro. Lần encode cuối ghi `animatic.mp4` tạm rồi rename.
- `hashing.py`: thêm lại `canonical_json` (chép từ `youtube-auto-short@f47813d:src/auto_short/hashing.py`).
- `media.py`: tái dùng `probe` cho kiểm output trong test; chỉ thêm helper nếu thật cần.
- Ngân sách: khoảng ≤ 350 dòng app, ≤ 250 dòng test. Test dùng ảnh / audio nhỏ sinh bằng FFmpeg, 2–3 shot ngắn (≤ 2 s / shot).

## Phải giữ nguyên

- `import-story`, `import-assets` và layout workspace của P1a.1; toàn bộ test hiện có vẫn PASS.
- Không runtime dependency Python mới; chỉ FFmpeg / ffprobe hệ thống.
- `node scripts/quality-gate.mjs` giữ các bước hiện có.

## Code bị thay / xóa

Không có (chỉ thêm mới; `__main__.py`, `hashing.py` sửa tại chỗ để thêm lệnh / hàm).

## Acceptance Criteria

1. `shots.json` sai: JSON hỏng, thiếu `version` / `shots`, `id` trùng hoặc sai định dạng, có cả hoặc thiếu cả `image` / `layers`, `layers` ngoài 2–3 phần tử, asset không có trong manifest hoặc sai `kind`, thiếu thời lượng khi không có audio, `camera` / `transition` lạ, `parallax` không có `layers`. Mỗi trường hợp đều exit ≠ 0, thông báo nêu shot và trường bị lỗi, không ghi file nào vào `animatic/`.
2. Thời lượng shot = `max(duration_s, thời lượng audio)`; không có audio thì dùng `duration_s`.
3. `animatic.mp4`: 1920×1080, 30 fps, H.264 + AAC; thời lượng = tổng thời lượng shot ±0,1 s; ảnh không đúng 16:9 được giữ tỉ lệ (pad), không bị méo.
4. `subtitles.srt` có đúng một cue cho mỗi shot có `subtitle`, mốc đầu / cuối khớp ranh giới shot ±100 ms. Phụ đề tiếng Việt có dấu được burn vào video bằng Be Vietnam Pro (font + `OFL.txt` có trong package).
5. Shot `layers` cho ra khung hình chồng các layer (layer PNG trong suốt phía trên nhìn thấy được trên nền).
6. Chạy lại `animatic` khi không đổi gì thì không encode lại segment nào (mtime segment giữ nguyên, CLI báo số segment tái dùng). Đổi một shot thì chỉ segment đó được dựng lại.
7. `python -m pytest -q` PASS; test không gọi mạng, media sinh bằng FFmpeg trong `tmp_path`.
8. `node scripts/quality-gate.mjs` PASS trong env `animation-studio`; CI "Quality" xanh trên PR.

## Required verification

IMPLEMENTER (Codex, trong sandbox `workspace-write`, mỗi lệnh < 5 phút):

- `python -m pytest -q tests/test_shots.py tests/test_animatic.py` — AC1–AC7.
- `python -m pytest -q` — không regression P1a.1.

ORCHESTRATOR (ngoài sandbox):

- `node scripts/quality-gate.mjs` trong env `animation-studio` — AC8.
- Chạy tay `animatic` trên workspace tạm với 3 shot (1 shot `layers`, phụ đề có dấu); trích 1 frame mỗi shot (`ffmpeg -ss`) và xem bằng mắt — AC3, AC4, AC5.
- Chạy lại lần 2 để kiểm tái dùng segment — AC6.
- Link CI run xanh trên PR — AC8.

Tất cả required verification phải chạy và PASS trước READY.

## Manual test checklist (Tech Lead)

Không chạm database, security model hay public API contract (CLI nội bộ). Manual test là điểm danh.

- [ ] Viết `shots.json` 3–5 shot với asset thử, chạy `animatic`, xem `animatic.mp4`: phụ đề đọc được, đúng dấu, khớp giọng.

## Handoff

Không dùng.

## Result

- Main changes:
- Tests:
- Diff + / − (app, test):
- Helper mới (đã tìm, lý do không tái dùng):
- Review:
- Important findings / decisions:
- Known limitations:
- PR:
