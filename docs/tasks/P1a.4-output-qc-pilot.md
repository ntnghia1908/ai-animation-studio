# Task: P1a.4 — Kiểm output tự động + pilot với asset thật

## Status / Approval

- Status: READY
- Type: FEATURE
- Change class: S1
- Owner: HUMAN LEAD
- Execution profile: dual-agent
- Orchestrator: claude-code
- Implementer: codex (`codex exec`, effort high) — spec rõ, chỉ FFmpeg + stdlib, P1a.2 / P1a.3 cùng adapter; quota còn nhiều (5 h: 21 %, tuần: 3 %); dự phòng `claude-code`
- Human Lead: HUMAN LEAD
- Authorization mode: boundary
- Authorization source: docs/decisions/P1a-VERTICAL-SLICE-AUTHORIZATION-DRAFT.md (ACCEPTED, HUMAN LEAD 2026-10-23) §3 ("tự kiểm output"), §5, §8 task 4
- Parallel group: —
- Owned paths: `src/animation_studio/qc.py` (mới), `src/animation_studio/render.py` (chỉ dựng segment song song), `src/animation_studio/media.py`, `src/animation_studio/assets.py`, `src/animation_studio/__main__.py`, `tests/test_qc.py` (mới), `tests/conftest.py`, `tests/test_assets.py`, `tests/test_render.py` (CLI output + test song song), `tests/test_cli.py`, `README.md`, `docs/ai/project-profile.md` (module map, CLI), `docs/workflow/current-state.md`, `docs/decisions/ADR-001-mvp-architecture-and-phasing.md` + `docs/decisions/P1a-VERTICAL-SLICE-AUTHORIZATION-DRAFT.md` (chỉ dòng D-08, ghi lại lựa chọn truyện của HUMAN LEAD), file này
- Dependencies: P1a.3 merged (PR #9). Phần B (pilot): truyện đã chọn; còn chờ asset pack + duyệt kịch bản (xem §Phần B)
- Base commit / branch: `f44116a` (main sau merge PR #9) / `feature/p1a-qc-pilot`
- Human Lead approval: accepted (HUMAN LEAD 2026-10-23, chat: "Duyệt P1a.4 kèm phần song song"; kịch bản pilot duyệt cùng ngày)
- Implementation authorized: YES

Lifecycle: `boundary` mode = `DRAFT → IN_PROGRESS → READY`. DONE suy ra từ Git sau khi merge.

Task có hai phần (Status READY áp cho Phần A; Phần B ghi tiến độ ở mục Result):

- **Phần A — code QC** (làm được ngay): READY → PR → HUMAN LEAD merge.
- **Phần B — pilot asset thật + HUMAN LEAD chấm** (chặn bởi D-08): không sửa code, chạy trên server sau khi A merge; kết quả ghi vào Result của file này bằng một PR docs riêng. P1a chỉ đóng khi B đạt ngưỡng boundary §5.

## Goal

Sau mỗi lần `render`, HUMAN LEAD thấy ngay phim có đạt quality gate tự động của boundary §5 hay không:

```text
python -m animation_studio render <project>   # dựng phim + in kết quả QC
python -m animation_studio check  <project>   # chỉ chạy QC trên film.mp4 hiện có; exit 2 nếu FAIL
```

Kết quả chi tiết ở `<project>/render/qc.json`. Layer PNG trong suốt hoàn toàn được cảnh báo ngay khi nhập. Sau đó chạy pilot với truyện "Tổ kiến và nhà ở" (Báo Ứng Hiện Đời, tập 1) và asset thật, HUMAN LEAD chấm 5 tiêu chí để quyết mở P1b.

## Scope

- In scope (A):
  - Module `qc.py`: chạy các kiểm tra §5 trên `render/film.mp4` + `shots.json` + `render/subtitles.srt`, ghi `render/qc.json` (atomic).
  - Lệnh `check <project>`; `render` gọi QC sau khi dựng xong.
  - Kiểm tái tạo (AC-006) giữa hai lần `render` cùng input.
  - Cảnh báo ảnh có alpha = 0 ở mọi pixel khi `import-assets` và trong `qc.json`.
  - Dựng segment video của `render` song song (HUMAN LEAD duyệt thêm 2026-10-23: pilot 50 s mất ~5 phút render trên 1/32 core).
- In scope (B): import truyện + asset thật, soạn `shots.json` (ORCHESTRATOR soạn giúp trong chat, boundary §2) từ kịch bản HUMAN LEAD đã duyệt, animatic → HUMAN LEAD xem → render → QC PASS → HUMAN LEAD chấm.
- Out of scope:
  - Sửa pipeline render ngoài phần song song (biên độ camera, canvas 4×, easing, transition mới…). Nếu pilot lộ lỗi chất lượng → task P1a.5 riêng.
  - Ngưỡng QC cấu hình được; QC cho `animatic`.
  - Commit truyện, asset, phim pilot vào repo (repo public).
  - Đăng phim pilot lên YouTube hay bất kỳ đâu (quyền bản dịch chưa xác nhận, xem §Phần B).
  - Mọi thứ thuộc P1b (Web UI, TTS, AI provider, GPU).

## Authority / key decisions

- Boundary P1a §3 (tự kiểm output), §5 (bảng ngưỡng tự động + HUMAN LEAD chấm), §6 P1a-2 (ngưỡng §5 ACCEPTED), D-08 (nguồn + quyền + asset do HUMAN LEAD cung cấp).
- **HUMAN LEAD 2026-10-23 (chat):** pilot dùng truyện "11. Tổ kiến và nhà ở" trong *Báo Ứng Hiện Đời*, tập 1 (Cư sĩ Quả Khanh, Hạnh Đoan dịch, 2013), thay cho truyện Liêu Trai ghi ở D-08. Task này cập nhật dòng D-08 của ADR-001 và boundary P1a để ghi lại lựa chọn đó (không đổi phần khác).
- project-profile §4: nội dung Phật giáo phải phân biệt nguyên văn / diễn giải / sáng tác, không gán lời cho kinh điển, HUMAN LEAD duyệt trước khi sản xuất.
- REQ-001 AC-006 (reproducible render), FR-009.
- Quyết định cục bộ S1:
  - **Kiểm tra trong `qc.json`** (mỗi mục: `name`, `status` ∈ `PASS | FAIL | WARN | SKIP`, `measured`, `threshold`, `detail`):

    | `name` | Điều kiện PASS |
    |---|---|
    | `format` | 1920×1080, SAR 1:1, `r_frame_rate` = `avg_frame_rate` = 30/1, video `h264`, audio `aac` |
    | `duration_match` | \|thời lượng film − Σ `duration_s`\| ≤ 0,1 s |
    | `duration_range` | 30 s ≤ thời lượng film ≤ 60 s |
    | `subtitles` | số cue = số shot có `subtitle`; mỗi cue nằm trong khung thời gian shot của nó ±0,1 s |
    | `black` | `blackdetect` (`d=0.5`, ngưỡng mặc định) không tìm thấy đoạn nào |
    | `freeze` | không có đoạn `freezedetect` (`d=0.5`) nào nằm ngoài vùng cho phép; vùng cho phép = khung thời gian shot `static` (cộng đuôi crossfade 0,5 s nếu có) |
    | `loudness` | `ebur128` integrated trong [−17, −15] LUFS; track im lặng → FAIL |
    | `reproducible` | xem mục tái tạo; FAIL nếu khác, SKIP nếu chưa có lần trước |
    | `layer_alpha` | WARN (không bao giờ FAIL) khi một ảnh dùng trong shot có alpha = 0 ở mọi pixel; PASS nếu không có |

    Kết quả tổng `overall`: FAIL nếu có mục FAIL; WARN / SKIP không làm FAIL.
  - **Freeze:** tham số nhiễu `n` của `freezedetect` giữ mặc định (−60 dB) trừ khi đo cho thấy camera move mượt bị nhận nhầm là đứng hình; nếu đổi, IMPLEMENTER ghi giá trị và lý do trong Result. Đầu / cuối shot có easing chậm (smoothstep) là chuyển động, không được báo đứng hình > 0,5 s với shot ≥ 3 s.
  - **Black:** không có vùng được miễn (phim không có transition qua đen). Cảnh đêm tối của truyện thật có thể chạm ngưỡng; khi đó HUMAN LEAD xem và quyết ở Phần B, không tự nới ngưỡng.
  - **Một lượt decode:** `blackdetect`, `freezedetect` và `ebur128` chạy trong cùng một lệnh FFmpeg (`-f null`) nếu được; hash PCM là một lệnh riêng.
  - **Tái tạo (AC-006):** `qc.json` lưu `input_key` (sha256 `canonical_json` của nội dung `shots.json` đã parse + sha256 của mọi asset được tham chiếu + tên pipeline render), `duration_s`, `shots` (danh sách `[id, start_s, end_s]` theo thứ tự), `audio_pcm_sha256` (sha256 audio của `film.mp4` decode ra `s16le`, 48 kHz, stereo). Lệnh `render` đọc `qc.json` cũ trước khi dựng; nếu `input_key` trùng thì so `duration_s` (±0,1 s), `shots` và `audio_pcm_sha256` → PASS / FAIL; khác key hoặc không có file → SKIP. Lệnh `check` không đánh giá lại tái tạo: giữ mục `reproducible` của `qc.json` hiện có khi `input_key` trùng, ngược lại SKIP.
  - **Exit code:** `render` giữ hành vi hiện tại (exit 0 khi dựng xong, kể cả QC FAIL), in thêm `qc <overall> -> <path qc.json>` và một dòng cho mỗi mục FAIL / WARN. `check`: exit 0 khi `overall` ≠ FAIL, exit 2 khi FAIL, exit 1 (`error: …`) khi chưa có `film.mp4` hoặc `shots.json` không hợp lệ. QC không xóa hay sửa `film.mp4`.
  - **Render song song:** các segment cần dựng (cache miss) chạy đồng thời qua `concurrent.futures.ThreadPoolExecutor`, mỗi worker một process FFmpeg vẫn 1 thread (`VIDEO`, `-filter_complex_threads 1`), nên byte output, key cache, `built` / `reused` không đổi. Số worker = `min(số segment cần dựng, os.cpu_count() or 1, 8)`. Một segment lỗi → chờ các worker đang chạy dừng, raise `UserError` của segment đầu tiên lỗi theo thứ tự shot; không để file dở trong `segments/` (giữ cơ chế thư mục tạm + `replace`). Dựng track audio có thể chạy song song với segment nếu đơn giản; không bắt buộc. Không thêm cấu hình.
  - **Alpha = 0:** helper trong `media.py` (vd `fully_transparent(path) -> bool`) chỉ decode khi `pix_fmt` có kênh alpha; dùng FFmpeg (`alphaextract` + `signalstats` hoặc decode raw), không thêm dependency. `import-assets --kind image`: in `warning: <file>: alpha = 0 everywhere (fully transparent)` ra stderr, **vẫn nhập** (không đổi lô all-or-nothing, không đổi schema manifest).

## Implementation approach

- `qc.py` (mới): `check_render(workspace, project_id, previous: dict | None) -> dict` (hoặc tương đương), validate qua `load_shots` trước; các hàm kiểm tra nhỏ nhận số liệu đã đo (để test bằng clip lavfi rẻ, không cần render 30 s); ghi `qc.json` bằng `atomic_write_json`.
- Tái dùng: `media._ffprobe` (probe film), `animatic.run_ffmpeg`, `animatic.srt_cues` (mốc kỳ vọng), `hashing.canonical_json` / `sha256_file`, `workspace.atomic_write_json` / `read_json`, `shots.load_shots`. Helper PCM: chuyển `pcm()` của `tests/test_render.py` vào app nếu khớp hành vi, test dùng lại.
- `__main__.py`: lệnh `check`; `render` gọi QC sau `build_render` (không đổi chữ ký `build_render`).
- Test: clip tổng hợp bằng lavfi (`testsrc2` chuyển động, `color` tĩnh, `color=black`, `sine` / `anullsrc`) ở độ phân giải nhỏ cho từng kiểm tra; một test tích hợp chạy `render` + `check` trên project ngắn (kỳ vọng `duration_range` FAIL, các mục khác PASS / WARN đúng). Mỗi lệnh test < 5 phút.
- Ngân sách: khoảng ≤ 200 dòng app, ≤ 220 dòng test.

## Phải giữ nguyên

- `import-story`, `import-assets` (trừ dòng cảnh báo stderr), `animatic`, `render`: hành vi, exit code, layout output (thêm `render/qc.json` là mới), key cache segment; toàn bộ test hiện có PASS.
- Không runtime dependency Python mới; chỉ FFmpeg / ffprobe hệ thống (kiểm `blackdetect`, `freezedetect`, `ebur128`, `alphaextract`, `signalstats` có trong FFmpeg 6.1 server và FFmpeg của CI).
- `node scripts/quality-gate.mjs` giữ các bước hiện có.

## Code bị thay / xóa

- Helper `pcm()` trong `tests/test_render.py` nếu chuyển vào app: test dùng bản app, không để bản trùng. Ngoài ra không có.

## Acceptance Criteria

Phần A:

1. `format`, `duration_match`, `duration_range`: clip sai từng điều kiện (độ phân giải, fps, codec, lệch thời lượng > 0,1 s, < 30 s, > 60 s) → mục tương ứng FAIL; clip đúng → PASS (biên 30 s / 60 s / ±0,1 s tính PASS).
2. `subtitles`: cue lệch > 0,1 s khỏi khung shot hoặc thiếu cue → FAIL; SRT do `render` sinh → PASS.
3. `black`: clip có đoạn đen ≥ 0,6 s → FAIL, `measured` nêu khoảng thời gian; clip không đen → PASS.
4. `freeze`: đoạn đứng hình ≥ 0,6 s trong shot không phải `static` → FAIL; cùng đoạn đó nằm trong shot `static` → PASS; shot `push_in` / `pan_left` / `parallax` dài ≥ 3 s do `render` dựng → không bị báo.
5. `loudness`: film do `render` dựng có giọng → PASS; audio −30 LUFS hoặc im lặng → FAIL.
6. `reproducible`: `render` hai lần cùng input → lần 2 `reproducible` PASS; `qc.json` cũ có `audio_pcm_sha256` khác (sửa tay trong test) với cùng `input_key` → FAIL; đổi input → SKIP. `check` giữ nguyên mục này như mô tả ở quyết định.
7. `layer_alpha` + import: PNG alpha = 0 mọi pixel → `import-assets` exit 0, nhập vào manifest, stderr có `warning:` nêu tên file; shot dùng ảnh đó → `layer_alpha` WARN, `overall` không vì thế mà FAIL. PNG có một vùng alpha > 0 (fixture `patch`) và ảnh không alpha → không cảnh báo.
8. CLI: `render` exit 0 và in `qc <overall> -> …/render/qc.json`; `check` exit 2 khi FAIL, 0 khi PASS / WARN, 1 khi chưa có `film.mp4`; `qc.json` ghi atomic, không đụng `film.mp4`.
9. Song song: project ≥ 3 segment cần dựng → FFmpeg segment được gọi đồng thời (test đo bằng `run_ffmpeg` giả có rào chắn / đếm đồng thời, không dựa vào thời gian); kết quả `film.mp4` và tên file segment giống hệt khi chạy 1 worker (monkeypatch số worker = 1); segment lỗi → `UserError`, `segments/` không có file dở, `film.mp4` cũ giữ nguyên.
10. `python -m pytest -q` PASS; test không gọi mạng, media sinh bằng FFmpeg trong `tmp_path`.
11. `node scripts/quality-gate.mjs` PASS trong env `animation-studio`; CI "Quality" xanh trên PR.

Phần B (pilot, sau khi A merge và D-08 có đủ):

12. Phim pilot: 5–8 shot, 30–60 s, ≥ 1 shot `parallax` 2–3 layer, ≥ 1 crossfade, phụ đề tiếng Việt, giọng đọc thật; `check` → `overall` PASS (WARN chấp nhận nếu ORCHESTRATOR giải thích được), `reproducible` PASS ở lần render thứ hai.
13. HUMAN LEAD chấm 1–5: camera mượt, phụ đề dễ đọc / đúng dấu, nhịp kể khớp giọng, parallax có chiều sâu, tổng thể "đủ làm phim mẫu". Đạt khi không mục nào < 3 và tổng thể ≥ 4 → đề xuất đóng P1a, mở P1b. Không đạt → ghi nguyên nhân, ORCHESTRATOR đề xuất task P1a.5 (vẫn trong P1a).

## Required verification

IMPLEMENTER (Codex, sandbox `workspace-write`, mỗi lệnh < 5 phút):

- `python -m pytest -q tests/test_qc.py tests/test_assets.py tests/test_render.py` — AC1–AC9.
- `python -m pytest -q` — AC10, không regression.

ORCHESTRATOR (ngoài sandbox):

- `node scripts/quality-gate.mjs` trong env `animation-studio` — AC11.
- Chạy tay `render` + `check` trên workspace tạm với asset tổng hợp 1920×1080 (dùng lại bộ thử của P1a.3: 6 shot × 5,5 s, đủ 6 kiểu camera, 33 s): `overall` PASS, `freeze` không báo nhầm, thời gian QC; render lần 2 → `reproducible` PASS; xóa `segments/` rồi render lần 3 → `reproducible` PASS (dựng lại toàn bộ video) — AC4–AC6, AC8. Đo thời gian render pilot 50 s trước / sau song song — AC9.
- Link CI run xanh trên PR — AC11.
- Phần B: chạy pilot trên server (workspace `~/animation-studio-data`), ghi `qc.json` tóm tắt + điểm HUMAN LEAD vào Result — AC12, AC13.

Tất cả required verification của Phần A phải chạy và PASS trước READY của Phần A.

## Phần B — pilot "Tổ kiến và nhà ở"

**Nguồn:** *Báo Ứng Hiện Đời*, tập 1, truyện 11 "Tổ kiến và nhà ở" (tr. 30–31). Tác giả: Cư sĩ Quả Khanh; dịch: Hạnh Đoan (29/03/2013). PDF do HUMAN LEAD cung cấp 2026-10-23; không commit PDF hay văn bản truyện vào repo.

**Quyền:** sách là bản dịch "gởi tặng" (sách biếu), không ghi điều khoản cho phép làm tác phẩm phái sinh hay đăng tải. Pilot chỉ dùng **nội bộ**, không đăng; `import-story --rights` ghi đúng trạng thái này (vd `"Sách biếu, chưa xác nhận quyền phái sinh; chỉ demo nội bộ"`). Muốn đăng sau này → HUMAN LEAD xác nhận quyền với dịch giả / đơn vị ấn tống (D-08 còn mở phần này).

**Nội dung Phật giáo (project-profile §4):** truyện ~700 chữ, phim 30–60 s nên lời kể là **diễn giải** rút gọn; lời Hòa thượng giữ sát nguyên văn bản dịch và ghi là lời nhân vật trong truyện, không gán cho kinh điển. HUMAN LEAD duyệt kịch bản dưới đây (sửa thoải mái) trước khi làm asset.

Kịch bản: HUMAN LEAD duyệt 2026-10-23, rồi chỉnh theo 6 ảnh HUMAN LEAD gửi (8 file, `s05` là 3 layer) thành 8 shot, 50,0 s. Gói pilot (ngoài repo): `~/animation-studio-pilot/to-kien/` (`shots.json`, `script.tsv`, `run.sh`, ảnh, giọng, nhạc, truyện nguyên văn).

| # | Ảnh | Camera | Lời kể / phụ đề (`[NV]` = sát bản dịch) | s | Sau shot |
|---|---|---|---|---|---|
| 1 | s01 tìm nhà | `push_in` | Sang nước ngoài định cư đã ba năm, gia đình bốn người vẫn chưa mua được ngôi nhà nào. | 5,2 | crossfade |
| 2 | s02 bất đồng | `pull_out` | Chồng ưa thì vợ không chịu, con thích thì cha mẹ lắc đầu. Đến khi cả nhà cùng ưng, chủ nhà lại không bán. | 7,0 | crossfade |
| 3 | s03 Ngũ Đài Sơn | `pan_right` | Nghĩ phúc báo mình chưa đủ, họ lên Ngũ Đài Sơn, xin Hòa thượng Diệu Pháp giải nghi. | 5,7 | cut |
| 4 | s04 Hòa thượng | `push_in` | Hòa thượng mỉm cười hỏi: [NV] "Hai con tinh nghịch, có ưa chọc phá tổ kiến hay không vậy?" | 5,2 | crossfade |
| 5 | s05 3 layer | `parallax` | Người mẹ cười kể: hồi nhỏ hai cháu mê đào tổ kiến, xem cung điện kiến chúa, kho lương thực, quên cả ăn uống. | 7,1 | crossfade |
| 6 | s04 Hòa thượng | `pull_out` | Hòa thượng nói: [NV] "Hủy đi bao ngôi nhà lũ kiến tạo dựng nên… Vì lí do đó mà ngày nay các con ở đâu cũng không yên, tìm nhà không ra!" | 8,0 | cut |
| 7 | s06 sám hối | `static` | Cha mẹ biết lỗi, nguyện về sám hối, tụng kinh hồi hướng công đức cho loài kiến. | 5,5 | cut |
| 8 | s06 sám hối | `push_in` | Hòa thượng dặn: [NV] "Tất cả chúng sinh đều có khả năng thành Phật, cho nên không được xem thường loài vật." | 6,3 | — |

Asset (HUMAN LEAD giao ORCHESTRATOR quyết giọng + nhạc):

- Ảnh: HUMAN LEAD tạo bằng công cụ ngoài, 1672×941 (16:9, render upscale lên canvas 2×).
- Giọng bản xem trước: Piper TTS 1.8.0 offline, giọng `vi_VN-vais1000-medium` (dataset VAIS-1000, CC BY 4.0), cài trong env tạm ngoài repo, không phải dependency của project; 0,3 s lặng đầu mỗi file.
- Giọng chính (mặc định trong `run.sh`): audiobook *Báo Ứng Hiện Đời* tập 1 do HUMAN LEAD cung cấp 2026-10-23; truyện 11 nằm ở track `006` từ 7:59 đến 12:29 (track `007` mở đầu truyện 12, track `008` là truyện 14–15). Mốc từng từ bằng faster-whisper 1.2.1 model `medium` (offline, env tạm ngoài repo); 8 đoạn cắt nguyên văn lời đọc (bỏ bớt vài vế để phim ≤ 60 s), phụ đề khớp lời đọc (`shots-audiobook.json`, 59,9 s). Quyền bản thu như sách: chỉ demo nội bộ.
- Nhạc: pad ngũ cung tổng hợp bằng FFmpeg `aevalsrc` (CC0, tự tạo), −16,4 LUFS trước khi render hạ −18 dB.
- Bản xem trước (workspace tạm, trước Phần A): 1920×1080, 30 fps, 50,000 s, −16,0 LUFS, không có khung đen, đứng hình chỉ trong shot `static` (38,2–43,7 s); lượt chạy đầu mất 7 phút 8 giây (render ~5 phút, 1 core).

**Còn chờ HUMAN LEAD:**

1. ~~Duyệt kịch bản, ảnh, `config.toml`, công cụ tạo ảnh (ChatGPT)~~ (xong).
2. Chạy pilot thật sau khi Phần A merge: `bash ~/animation-studio-pilot/to-kien/run.sh` (`VOICE=piper` cho bản TTS), xem phim, chấm 5 tiêu chí.

Media pilot và `film.mp4` chỉ nằm trong workspace `~/animation-studio-data`, không commit.

## Manual test checklist (Tech Lead)

Không chạm database, security model hay public API contract (CLI nội bộ). Manual test Phần A là điểm danh; Phần B là gate đóng P1a.

- [ ] Phần A: `render` một project, đọc dòng `qc …` và `qc.json`; `check` trả exit 2 khi phim < 30 s; render nhanh hơn rõ trên server.
- [ ] Phần B: xem `animatic.mp4` rồi `film.mp4` của pilot, chấm 5 tiêu chí.

## Handoff

Không dùng.

## Result

- Main changes (Phần A): `qc.py` mới (9 mục kiểm, `render/qc.json` atomic, tái tạo theo `input_key`); lệnh `check` (exit 0 / 2 / 1), `render` in kết quả QC; `media.fully_transparent` + cảnh báo khi `import-assets`; `render` dựng segment song song (`ThreadPoolExecutor`, ≤ 8 worker, FFmpeg mỗi worker 1 thread); README mục "Kiểm output".
- IMPLEMENTER: `codex exec` (effort high, sandbox `workspace-write`), 1 lượt + 1 vòng sửa (`codex exec resume`), 116k + 148k tokens.
- Tests (`python -m pytest -q`: 106 passed, FFmpeg 6.1.1):

  | AC | Test |
  |---|---|
  | AC1 | `test_qc.py::test_format`, `test_duration_boundaries`, `test_lavfi_measurements` |
  | AC2 | `test_qc.py::test_subtitles`, `test_render.py::test_timeline_format_subtitles_and_silence` |
  | AC3 | `test_qc.py::test_lavfi_measurements` (đen ≥ 0,6 s) |
  | AC4 | `test_qc.py::test_lavfi_measurements`, `test_moving_render_no_freeze` (3 camera ≥ 3 s), các ca biên freeze ở ranh giới shot (vòng sửa) |
  | AC5 | `test_qc.py::test_lavfi_measurements`, `test_render.py::test_loudness_ducking_resume_pcm_and_atomic_output` |
  | AC6, AC7, AC8 | `test_qc.py::test_reproducibility_alpha_atomic_and_cli`, `test_assets.py::test_fully_transparent_warning`, test render / loudness (exit code, output CLI, giữ phim) |
  | AC9 | `test_render.py::test_parallel_segments_identity_and_failure` (barrier, byte giống hệt 1 worker, lỗi worker) |
  | AC10 | full suite 106 passed |
  | AC11 | `node scripts/quality-gate.mjs` PASS trong env `animation-studio`; CI: xem PR |

- Chạy tay (ORCHESTRATOR), dùng asset pilot thật thay bộ tổng hợp của P1a.3 (đủ 5 kiểu camera + `static`, parallax 3 layer, 4 crossfade, giọng + nhạc):
  - Bản giọng Piper (50,0 s): `check` → PASS cả 9 mục (`reproducible` SKIP lần đầu), QC mất 17 s. Render lần 1 (8 segment) 132 s so với ~300 s tuần tự; lần 2 (cache) 94 s; lần 3 sau khi xóa `segments/` 133 s; `reproducible` PASS ở lần 2 và 3; `film.mp4` song song giống từng byte bản dựng tuần tự.
  - Bản giọng audiobook (59,9 s): QC PASS, render 156 s (chạy cùng lúc quality gate).
- Diff + / − (app, test): app +210 / −8; test +219 / −6; README +14.
- Helper mới (đã tìm, lý do không tái dùng): tìm bằng `rg -n 'def .*|pipeline|pcm|transparent|blackdetect|freezedetect|ebur128' src tests`. `media.fully_transparent` (chưa có kiểm alpha), `media._ffmpeg_bytes` (`run_ffmpeg` trả log text, cần stdout nhị phân), `qc.pcm` (chuyển từ `tests/test_render.py`, bản test đã xóa), các hàm kiểm thuần và `check_render`.
- Review: ORCHESTRATOR review diff-first. F1 (vòng sửa): freeze bị coi là lỗi khi kéo dài một frame qua ranh giới shot `static` → `push_in` (pilot thật PASS chỉ nhờ trùng đúng 43,700 s); sửa: chỉ FAIL khi phần nằm ngoài cửa sổ `static` ≥ 0,5 s (qc +17 / −3, test +17). Không còn finding chặn.
- Important findings / decisions:
  - `freezedetect` dùng `n=-70dB`: −60 dB báo nhầm đoạn đầu / cuối easing của `push_in` 3 s trên ảnh thưa.
  - Song song chỉ tăng tốc bước segment (~2,3× toàn lệnh trên pilot); phần còn lại chủ yếu là encode cuối (`xfade` + burn phụ đề, 1 thread) ~75 s và QC 17 s.
  - Lỗi trong một worker: chờ mọi worker xong, raise lỗi của shot đầu tiên theo thứ tự; segment thành công giữ trong cache.
- Pilot (Phần B): bản xem trước đã có (`~/animation-studio-pilot/to-kien/preview/`), chưa chạy trên workspace thật, chưa có điểm HUMAN LEAD.
- Known limitations: encode cuối vẫn 1 thread (bước chậm nhất; tăng thread không ảnh hưởng AC-006 nhưng cần task riêng); QC `black` không miễn cảnh tối; ngưỡng QC cố định.
- PR:
