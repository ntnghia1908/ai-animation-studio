# Task: P1a.3 — Render phim có chuyển động

## Status / Approval

- Status: READY
- Type: FEATURE
- Change class: S1
- Owner: HUMAN LEAD
- Execution profile: dual-agent
- Orchestrator: claude-code
- Implementer: codex (`codex exec`, effort high) — spec rõ, chỉ FFmpeg + stdlib, P1a.2 cùng adapter xong 1 lượt; quota còn nhiều (5 h: 4 %, tuần: 1 %); dự phòng `claude-code`
- Human Lead: HUMAN LEAD
- Authorization mode: boundary
- Authorization source: docs/decisions/P1a-VERTICAL-SLICE-AUTHORIZATION-DRAFT.md (ACCEPTED, HUMAN LEAD 2026-10-23) §2, §3, §5
- Parallel group: —
- Owned paths: `src/animation_studio/render.py` (mới), `src/animation_studio/animatic.py`, `src/animation_studio/shots.py`, `src/animation_studio/__main__.py`, `tests/conftest.py`, `tests/test_render.py` (mới), `tests/test_shots.py`, `tests/test_animatic.py`, `README.md`, `docs/ai/project-profile.md` (module map, CLI), `docs/workflow/current-state.md`, file này
- Dependencies: P1a.2 merged (PR #8)
- Base commit / branch: `7c295ac` (main sau merge PR #8) / `feature/p1a-render`
- Human Lead approval: accepted (HUMAN LEAD 2026-10-23)
- Implementation authorized: YES

Lifecycle: `boundary` mode = `DRAFT → IN_PROGRESS → READY`. DONE suy ra từ Git sau khi merge.

## Goal

Từ cùng `shots.json` đã dùng cho animatic, HUMAN LEAD chạy:

```text
python -m animation_studio render <project>
```

Kết quả: `<project>/render/film.mp4` (1920×1080, 30 fps, H.264 + AAC). Shot có chuyển động camera mượt (push / pull / pan), shot `parallax` có 2–3 layer trôi với tốc độ khác nhau, crossfade giữa các shot được đánh dấu, phụ đề tiếng Việt, nhạc nền tự giảm khi có giọng, loudness khoảng −16 LUFS.

## Scope

- In scope:
  - Lệnh `render`: validate → dựng segment video / shot (có cache) → ghép video (cut / crossfade) → dựng track audio (giọng + nhạc ducking) → chuẩn hóa loudness → burn phụ đề → `film.mp4`.
  - Camera: `static`, `push_in`, `pull_out`, `pan_left`, `pan_right`, `parallax`.
  - Trường top-level tùy chọn `music` trong `shots.json` v1 (tương thích ngược).
  - Tách helper dùng chung giữa `animatic` và `render` (chạy FFmpeg, mốc SRT, burn phụ đề) mà không đổi hành vi `animatic`.
- Out of scope (P1a.4 hoặc sau):
  - Quality gate output tự động sau mỗi lần render (`blackdetect`, `freezedetect`, kiểm 30–60 s, test tái tạo PCM hash), pilot với asset thật, HUMAN LEAD chấm điểm.
  - Tham số chuyển động / transition / âm lượng nhạc cấu hình theo shot; easing tùy chọn; transition khác crossfade.
  - Web UI, sinh asset bằng AI, GPU.

## Authority / key decisions

- Boundary P1a §2 (luồng animatic → render), §3 (camera move upscale trước khi crop, 1 shot parallax 2–3 layer PNG, crossfade, phụ đề Be Vietnam Pro, nhạc nền giảm khi có giọng, chuẩn hóa loudness, resume theo hash), §5 (ngưỡng định dạng, thời lượng, sync phụ đề, loudness).
- ADR-001 A3; REQ-001 FR-006 (phương thức 1: still + camera / parallax), FR-009, FR-012.
- Quyết định cục bộ S1:
  - **Schema:** thêm `"music": "assets/audio/<file>"` ở root `shots.json` (tùy chọn, `kind` = `audio`, phải có trong manifest). `version` vẫn là 1. Validate cùng chỗ và cùng kiểu thông báo với trường shot (`shots.json (root): music: …`). `animatic` bỏ qua `music`.
  - **Khung hình:** render dùng *cover* (scale phủ kín 16:9, crop giữa), khác animatic (pad). Asset nên là 16:9; README ghi rõ.
  - **Camera** (biên độ cố định, easing smoothstep trên toàn shot):
    - `push_in`: zoom 1,00 → 1,15 vào giữa khung; `pull_out`: 1,15 → 1,00.
    - `pan_left` / `pan_right`: khung nhìn phủ ở zoom 1,15, trượt ngang hết biên dư (`pan_left` = camera đi sang trái, khung từ phải qua trái).
    - `parallax`: layer dưới cùng gần như đứng yên, các layer trên trôi ngang cùng chiều, biên độ tăng theo thứ tự layer (đề xuất 2 % / 5 % / 8 % chiều rộng); layer được scale đủ dư để không lộ mép.
    - `static`: khung tĩnh. Shot `layers` mà camera ≠ `parallax`: chồng layer thành một ảnh rồi áp camera.
    - Chống rung: không dùng `zoompan` trực tiếp trên ảnh gốc. Dựng trên canvas upscale (≥ 2×, scale lanczos) rồi crop / overlay theo biểu thức thời gian, cuối cùng scale về 1920×1080, để bước dịch chuyển dưới 1 pixel output. IMPLEMENTER chọn kỹ thuật cụ thể (vd `scale` + `crop` theo frame, hoặc `zoompan` trên canvas đã upscale) và ghi lý do trong Result.
  - **Crossfade:** dài cố định 0,5 s, bắt đầu tại ranh giới shot `i` → `i+1` (đuôi của shot `i` được kéo dài thêm 0,5 s, vd `tpad` clone hoặc chuyển động tiếp, và mờ dần trên đầu shot `i+1`). Tổng thời lượng phim vẫn bằng tổng thời lượng shot; mốc bắt đầu mỗi shot (giọng, phụ đề) không bị lệch. `transition` của shot cuối bị bỏ qua.
  - **Audio:** dựng riêng khỏi video. Giọng mỗi shot đặt tại mốc bắt đầu shot (`adelay`), trộn thành một track. Nhạc nền lặp hoặc cắt cho đủ thời lượng phim, fade-out 1 s ở cuối, nền khoảng −18 dB so với giọng; ducking bằng `sidechaincompress` lấy track giọng làm sidechain (giảm ≥ 6 dB khi có giọng). Không có `music` thì chỉ có giọng (hoặc im lặng).
  - **Loudness:** `loudnorm` hai lượt (đo rồi áp, `linear=true`), mục tiêu I = −16 LUFS, TP = −1,5 dBTP, LRA = 11. Track im lặng hoàn toàn (đo được −inf / < −70 LUFS) thì bỏ qua chuẩn hóa. Audio pipeline phải tất định (cùng input → cùng PCM) để P1a.4 kiểm AC-006.
  - **Encode:** video giữ `VIDEO` / `AUDIO` của animatic cho định dạng; segment render được phép chạy nhiều thread nếu cần tốc độ (AC-006 chỉ yêu cầu tái tạo thời lượng, thứ tự shot và PCM audio), ghi lựa chọn trong Result.
  - **Output:** `<project>/render/{film.mp4, subtitles.srt, segments/<key>.mp4}`. `segments/` là cache video-only, xóa được. Key = sha256 `canonical_json` gồm sha asset, thời lượng (kể cả đuôi crossfade), camera, tham số encode và tên pipeline có version.

## Implementation approach

- `render.py` (mới): `build_render(workspace, project_id) -> (built, reused, path)` theo khung của `build_animatic`: validate toàn bộ trước, cache segment theo key, ghi tạm trong thư mục stage rồi `replace`.
- Ghép video: một filter graph `xfade` / `concat` trên các segment; audio: một filter graph `adelay` + `amix` + (nhạc) `sidechaincompress`, rồi hai lượt `loudnorm`. Lần encode cuối gộp video + audio đã chuẩn hóa + burn phụ đề, `-t <tổng>`, `+faststart`.
- `animatic.py`: tách phần dùng chung thành helper công khai (vd `run_ffmpeg`, `srt_cues(shots) -> (bytes, cues)`, chuỗi filter burn phụ đề + stage font) và cho cả hai lệnh dùng; hành vi + key cache của animatic giữ nguyên (đổi tên hàm nội bộ không được làm đổi key).
- `shots.py`: thêm validate `music`; trả về cùng danh sách shot như hiện nay, cộng thông tin music (vd `load_shots` trả thêm music qua hàm riêng `load_music(pdir)` hoặc tuple — IMPLEMENTER chọn cách ít đụng chạm nhất, không phá caller hiện có ngoài `animatic.py`).
- `__main__.py`: lệnh `render <project>`, in `render built=<n> reused=<m> -> <path>`.
- Test: dùng lại `make_png`, `make_wav`, `shot_project`; thêm fixture nhạc (vd `sine` khác tần số, dài hơn phim) nếu cần. Ảnh nhỏ (64×48), shot ≤ 2 s, 2–3 shot / test, mỗi lệnh test < 5 phút.
- Ngân sách: khoảng ≤ 300 dòng app (kể cả refactor), ≤ 250 dòng test.

## Phải giữ nguyên

- `import-story`, `import-assets`, `animatic`: hành vi, layout output, key cache segment animatic; toàn bộ test hiện có PASS (chỉ sửa test animatic nếu đổi tên helper được import).
- Không runtime dependency Python mới; chỉ FFmpeg / ffprobe hệ thống (kiểm filter `xfade`, `sidechaincompress`, `loudnorm` có trong FFmpeg server trước khi dùng).
- `node scripts/quality-gate.mjs` giữ các bước hiện có.

## Code bị thay / xóa

- Phần dựng SRT, chạy FFmpeg và burn phụ đề viết inline trong `build_animatic` / `_run` / `_timestamp`: thay bằng helper dùng chung; không để lại bản trùng.

## Acceptance Criteria

1. `shots.json` có `music` sai (không phải chuỗi, không có trong manifest, sai `kind`): exit ≠ 0, thông báo nêu `music`, không ghi file nào vào `render/`. `shots.json` không có `music` vẫn hợp lệ cho cả `animatic` và `render`.
2. `film.mp4`: 1920×1080, 30 fps, H.264 + AAC; thời lượng = tổng thời lượng shot ±0,1 s, kể cả khi có crossfade.
3. Camera: với ảnh thử có chi tiết phân biệt được (vd ô màu lệch tâm), frame đầu và cuối của shot `push_in` / `pull_out` / `pan_left` / `pan_right` khác nhau đúng hướng (zoom vào / ra, dịch trái / phải); shot `static` có frame đầu ≈ frame cuối.
4. Parallax: trong shot `parallax` 2 layer, vị trí phần nhìn thấy của layer trên dịch chuyển nhiều hơn layer dưới giữa frame đầu và cuối.
5. Crossfade: tại giữa vùng crossfade, frame là pha trộn của hai shot (màu trung gian); với transition `cut`, frame ngay sau ranh giới là shot kế tiếp. Mốc bắt đầu shot sau không lệch (±1 frame).
6. `subtitles.srt` trong `render/` có một cue cho mỗi shot có `subtitle`, mốc khớp ranh giới shot ±100 ms; phụ đề được burn bằng Be Vietnam Pro.
7. Loudness: `ebur128` trên `film.mp4` có giọng (có và không có `music`) đo integrated −16 LUFS ±1.
8. Ducking: với nhạc nền, mức nhạc trong đoạn có giọng thấp hơn đoạn không giọng ≥ 6 dB (đo trên track trước `loudnorm` hoặc so cửa sổ RMS trên output, IMPLEMENTER chọn cách đo và ghi lại).
9. Resume: chạy lại `render` không đổi gì → không dựng lại segment nào (`built=0`); đổi `camera` của một shot → chỉ segment đó dựng lại. Hai lần render cùng input cho cùng PCM audio (sha256 của audio decode ra `s16le`).
10. `animatic` sau refactor: test animatic hiện có PASS, key segment không đổi.
11. `python -m pytest -q` PASS; test không gọi mạng, media sinh bằng FFmpeg trong `tmp_path`.
12. `node scripts/quality-gate.mjs` PASS trong env `animation-studio`; CI "Quality" xanh trên PR.

## Required verification

IMPLEMENTER (Codex, sandbox `workspace-write`, mỗi lệnh < 5 phút):

- `python -m pytest -q tests/test_shots.py tests/test_render.py` — AC1–AC9.
- `python -m pytest -q` — AC10, AC11, không regression.

ORCHESTRATOR (ngoài sandbox):

- `node scripts/quality-gate.mjs` trong env `animation-studio` — AC12.
- Chạy tay `render` trên workspace tạm với asset tổng hợp ~1920×1080 có chi tiết (5–6 shot, đủ 6 kiểu camera, 1 shot parallax 3 layer, 2 crossfade, phụ đề có dấu, giọng + nhạc), tổng ≥ 30 s: đo thời lượng, `ebur128`, thời gian render; trích frame đầu / giữa / cuối mỗi shot và giữa mỗi crossfade, xem bằng mắt — AC2–AC7; xem clip để đánh giá rung / giật của camera move.
- Chạy lại lần 2 để kiểm tái dùng + PCM hash — AC9.
- Link CI run xanh trên PR — AC12.

Tất cả required verification phải chạy và PASS trước READY.

## Manual test checklist (Tech Lead)

Không chạm database, security model hay public API contract (CLI nội bộ). Manual test là điểm danh; chấm điểm theo boundary §5 làm ở P1a.4 với asset thật.

- [ ] Chạy `render` trên project đã có animatic, xem `film.mp4`: camera mượt, parallax có chiều sâu, crossfade tự nhiên, nhạc nhỏ đi khi có giọng, phụ đề đúng dấu.

## Handoff

Không dùng.

## Result

- Main changes: `render.py` mới (segment video-only có cache, camera / parallax, ghép `xfade` / `concat`, mix giọng + nhạc `sidechaincompress`, `loudnorm` hai lượt, burn phụ đề); lệnh CLI `render`; trường root `music` trong `shots.py` (validate chung qua `_asset`); `animatic.py` tách `run_ffmpeg`, `srt_cues`, `subtitle_filter` dùng chung (key cache animatic không đổi); README mục Render.
- IMPLEMENTER: `codex exec` (model `gpt-6.1-sol`, effort high, sandbox `workspace-write`), 1 lượt + 2 vòng sửa (`codex exec resume`), khoảng 81k + 104k + 126k tokens.
- Tests (`python -m pytest -q`: 67 passed sau 2 vòng sửa, FFmpeg 6.1.1):

  | AC | Test |
  |---|---|
  | AC1 | `test_shots.py::test_invalid_music_without_output` (4 ca × `animatic` / `render`) |
  | AC2, AC5, AC6 | `test_render.py::test_timeline_format_subtitles_and_silence` (4 tổ hợp cut / crossfade: định dạng, thời lượng, pha trộn giữa crossfade, ranh giới cut đúng frame, SRT, pixel phụ đề) |
  | AC3 | `test_render.py::test_camera_direction_and_cover` (push / pull, pan trái / phải, static) |
  | AC4 | `test_render.py::test_parallax_layers_move_at_different_speeds` |
  | AC7–AC9 | `test_render.py::test_loudness_ducking_resume_pcm_and_atomic_output` (có / không nhạc: `ebur128`, ducking 880 Hz trước `loudnorm`, `built=0`, PCM sha256, đổi camera → `built=1`, lỗi encode cuối giữ output cũ) |
  | AC10 | `test_render.py::test_animatic_cache_identity_and_music_ignored` + test animatic hiện có |
  | AC11 | full suite; guard `_no_real_services` |
  | AC12 | `node scripts/quality-gate.mjs` PASS trong env `animation-studio`; CI "Quality" xanh trên `91f123c`: https://github.com/ntnghia1908/ai-animation-studio/actions/runs/39973331889 (lần chạy đầu bị hủy ở bước cài FFmpeg qua apt, chạy lại PASS) |

- Chạy tay (ORCHESTRATOR), asset tổng hợp 1920×1080, 6 shot × 5,5 s (đủ 6 kiểu camera, parallax 3 layer, 3 crossfade, phụ đề có dấu, giọng sine 4,5 s / shot, nhạc 20 s lặp):
  - `film.mp4` 1920×1080, 30/1, h264 + aac, 33,000 s (kỳ vọng 33,0); SRT khớp ranh giới 5,5 s; integrated −16,0 LUFS.
  - Frame trích ra: push / pull / pan đúng hướng, giữa crossfade là ảnh pha trộn, cut đúng ranh giới, parallax layer trên trôi nhiều hơn layer dưới, dấu tiếng Việt đúng.
  - Rung camera đo bằng tương quan chéo giữa các frame (dòng 150): pan dịch 0 → ~3 px / frame theo smoothstep, không đảo chiều; tốc độ dao động ±0,4 px giữa các frame (bước 0,5 px output do canvas 2×); shot `static` nhiễu nền 0,05 px.
  - Thời gian render 33 s phim: 2 phút 20 giây (1 thread); đổi layer 1 shot: `built=1 reused=5`, 1 phút; PCM sha256 giống nhau giữa hai lần render.
- Diff + / − (app, test): app +195 / −25; test +216 / −7; README +13.
- Helper mới (đã tìm, lý do không tái dùng): tìm bằng `rg -n 'def |loudnorm|sidechain|srt|ffmpeg' src tests`. Tách chung: `run_ffmpeg`, `srt_cues`, `subtitle_filter` (từ `build_animatic` / `_run`), `shots._asset`. Mới: `render._segment` (animatic pad + có audio; render cần cover, chuyển động, video-only), `render._audio` (chưa có mixer / ducking / loudnorm), `build_render`; helper test `frame`, `box`, `pcm`.
- Review: ORCHESTRATOR review diff-first; không có finding chặn. CI lần đầu fail (10 test): FFmpeg của runner in dòng tiến độ sau JSON `loudnorm`, `json.loads` lỗi `Extra data`. Vòng sửa: `-nostats` + `JSONDecoder.raw_decode`, thêm `test_loudnorm_measurement_ignores_trailing_progress` (app +3 / −2, test +17). CI lần hai fail `test_loudness_ducking_resume_pcm_and_atomic_output[True]` (PCM hash khác giữa hai lần render): runner `ubuntu-latest` dùng FFmpeg 8.0, server dùng 6.1. ORCHESTRATOR tái hiện bằng FFmpeg 8.0.1 (conda-forge, env tạm ngoài repo): `sidechaincompress` với hai input không tất định (5 hash / 6 lần) vì cỡ frame thay đổi theo lịch thread của input. Vòng sửa 2: `asetnsamples=n=1024` ở cả hai đầu vào sidechain (app +4 / −2); 20/20 lần cùng hash ở mức filter graph, test lặp 6 lần song song trên FFmpeg 8 đều PASS. Nhỏ, không sửa: `build_render` đọc lại `shots.json` để lấy `music` (đã validate trong `load_shots`).
- Important findings / decisions:
  - Chống rung: upscale lanczos lên canvas 3840×2160 (parallax 4608×2592) một lần rồi loop; `zoompan` (push / pull / pan) hoặc `crop` theo frame (parallax) trên canvas đó, rồi scale về 1080p.
  - Encode giữ 1 thread (`VIDEO` của animatic, `-filter_complex_threads 1`).
  - Ducking: `sidechaincompress` threshold 0,005, ratio 20; đo trong test giảm khoảng 23 dB.
  - Asset thử đầu tiên của ORCHESTRATOR có layer PNG trong suốt hoàn toàn (`drawbox` không đặt alpha) nên shot parallax chỉ thấy nền; tạo lại asset thì đúng. Đây là limitation đã ghi ở P1a.2; đề xuất P1a.4 cảnh báo layer có alpha = 0 toàn bộ.
- Known limitations: biên độ / easing / thời lượng crossfade cố định; ảnh không 16:9 bị crop; dao động tốc độ ±0,4 px khi pan (nếu HUMAN LEAD thấy giật ở P1a.4 thì nâng canvas lên 4×, đổi lại chậm hơn); resume chỉ tái dùng segment video, audio và encode cuối luôn chạy lại.
- PR: https://github.com/ntnghia1908/ai-animation-studio/pull/9
