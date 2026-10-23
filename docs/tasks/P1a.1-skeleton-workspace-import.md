# Task: P1a.1 — Package skeleton, workspace, import truyện / asset

## Status / Approval

- Status: READY
- Type: FEATURE
- Change class: S1
- Owner: HUMAN LEAD
- Execution profile: dual-agent
- Orchestrator: claude-code
- Implementer: claude-code (subagent `implementer`) — task đầu tiên đặt khung package / convention, cần bám repo sát; dự phòng `codex`
- Human Lead: HUMAN LEAD
- Authorization mode: boundary
- Authorization source: docs/decisions/P1a-VERTICAL-SLICE-AUTHORIZATION-DRAFT.md (ACCEPTED, HUMAN LEAD 2026-10-23) §3
- Parallel group: —
- Owned paths: `pyproject.toml`, `.gitignore`, `config.example.toml`, `src/animation_studio/`, `tests/conftest.py`, `tests/test_*.py`, `.github/workflows/quality.yml`, `README.md`, `docs/ai/project-profile.md` (module map §, setup §9), `docs/workflow/current-state.md`, file này
- Dependencies: PR #5 merged (boundary P1a ACCEPTED)
- Base commit / branch: `1894c9e` (main sau merge PR #5) / `feature/p1a-skeleton-import`
- Human Lead approval: accepted (HUMAN LEAD 2026-10-23)
- Implementation authorized: YES

Lifecycle: `boundary` mode = `DRAFT → IN_PROGRESS → READY`. DONE suy ra từ Git sau khi merge.

## Goal

Trên server, trong conda env `animation-studio`, HUMAN LEAD chạy được:

```text
python -m animation_studio import-story <project> story.txt --title … --source … --rights …
python -m animation_studio import-assets <project> --kind image|audio --license … --source-tool … <files…>
```

Kết quả: truyện được lưu nguyên văn kèm provenance, asset được chép vào workspace `~/animation-studio-data` kèm manifest (sha256, nguồn, license, kích thước / thời lượng). Đây là đầu vào cho P1a.2 (animatic).

## Scope

- In scope:
  - Package `src/animation_studio/` (hatchling src-layout, Python ≥ 3.12, **không runtime dependency**; extra `dev` = `pytest`).
  - CLI `python -m animation_studio` (argparse) với 2 lệnh: `import-story`, `import-assets`.
  - Config: `config.toml` (gitignored) với khóa `workspace`; `config.example.toml` commit sẵn `workspace = "~/animation-studio-data"`; cờ `--workspace` ghi đè.
  - Helper chung: atomic write, đọc JSON, UTC timestamp, sha256, canonical JSON, probe media bằng `ffprobe`.
  - Test pytest; `tests/conftest.py` có guard chặn kết nối mạng và fixture sinh ảnh / audio bằng FFmpeg.
  - CI: `quality.yml` cài Python 3.12, FFmpeg, `pip install -e ".[dev]"` để gate chạy được pytest.
  - README: hướng dẫn tạo env và chạy 2 lệnh (ngắn).
- Out of scope:
  - `shots.json`, animatic, render, phụ đề, font (P1a.2–P1a.3).
  - Resume / stage runner (`run_stage`, `check_up_to_date`): chưa cần cho import; đưa vào task render.
  - Sửa / xóa truyện hay asset đã nhập, liệt kê thư viện, Web UI.
  - Dependency Python ngoài `pytest`.

## Authority / key decisions

- `docs/decisions/P1a-VERTICAL-SLICE-AUTHORIZATION-DRAFT.md` §3, §6 (D-04, P1a-1).
- `docs/decisions/ADR-001-mvp-architecture-and-phasing.md` A3: chỉ tạo module slice cần.
- REQ-001 FR-001 (tối thiểu), FR-008.
- Quyết định cục bộ S1:
  - Layout workspace: `<workspace>/projects/<project_id>/story/{source.txt,story.json}`, `<…>/assets/{images,audio}/<sha256[:12]>-<tên gốc>`, `<…>/assets/manifest.json`.
  - `project_id`: `^[a-z0-9][a-z0-9-]{0,63}$`. Tạo thư mục khi nhập lần đầu (không có lệnh `init`).
  - Truyện bất biến: nhập lại cùng nội dung → no-op; khác nội dung → từ chối.

## Implementation approach

- Module (dự kiến, chốt khi implement): `__main__.py` (CLI), `config.py`, `workspace.py` (atomic IO + đường dẫn project), `hashing.py`, `media.py` (ffprobe), `story.py`, `assets.py`.
- Chép có chọn lọc từ `youtube-auto-short@f47813d` (cùng tác giả; ghi nguồn trong docstring module):
  - `src/auto_short/workspace.py`: `atomic_write_bytes`, `atomic_write_json`, `utc_now` (+ đọc JSON tolerant nếu có);
  - `src/auto_short/hashing.py`: `sha256_file`, `canonical_json`;
  - `tests/conftest.py`: pattern `_no_real_services` (chặn mọi host không phải loopback).
  - Không chép `Workspace` class / episode / manifest stage.
- `media.py`: `ffprobe -show_streams -show_format -of json`; trả width / height / pix_fmt (ảnh) hoặc duration_s / sample_rate / channels (audio). Lỗi probe → exception rõ ràng.
- `import-assets`: validate đuôi (`.png .jpg .jpeg` / `.wav .mp3`) và probe **trước** khi chép; chép vào file tạm rồi rename; cập nhật manifest một lần (atomic) sau khi mọi file hợp lệ.
- Ngân sách: khoảng ≤ 400 dòng app, ≤ 300 dòng test.

## Phải giữ nguyên

- `node scripts/quality-gate.mjs` vẫn chạy mọi bước hiện có (framework-check, product-check, `node --test`, forbidden files); chỉ thêm pytest (đã có sẵn trong gate khi có `pyproject.toml`).
- `scripts/*.mjs`, `tests/*.test.mjs` không đổi.
- `config.toml` không bao giờ bị track.

## Code bị thay / xóa

Không có (chỉ thêm mới; sửa `quality.yml` và `README.md` tại chỗ).

## Acceptance Criteria

1. Trong env `animation-studio` (Python 3.12): `pip install -e ".[dev]"` thành công; `python -m animation_studio --help` liệt kê `import-story`, `import-assets`. Package không khai runtime dependency.
2. Workspace lấy từ `--workspace`, nếu không có thì từ `config.toml` (khóa `workspace`, mở rộng `~`). Thiếu cả hai, hoặc `project_id` sai định dạng → thông báo rõ, exit ≠ 0, không tạo file. `.gitignore` có `config.toml`; `config.example.toml` được commit.
3. `import-story`: chép **nguyên byte** file truyện (UTF-8) vào `story/source.txt`; `story.json` có `id`, `title`, `source`, `author`, `translator`, `genre`, `rights`, `review_status = "pending"`, `sha256`, `imported_at`. `--source` và `--rights` bắt buộc. Nhập lại cùng nội dung → exit 0, báo unchanged, không ghi gì. Khác nội dung → exit ≠ 0, `source.txt` và `story.json` cũ không đổi.
4. `import-assets`: mỗi file được chép vào workspace; manifest có `sha256`, `kind`, `path` (tương đối project), `original_name`, `source_tool`, `model` (tùy chọn), `declared_cost_usd` (mặc định 0), `license`, `imported_at` và metadata probe (ảnh: `width`, `height`, `pix_fmt`; audio: `duration_s`). PNG có alpha nhận được và `pix_fmt` phản ánh alpha. `--license` bắt buộc.
5. Cùng sha256 nhập lại → không tạo bản sao, không thêm entry. Có file sai đuôi / probe lỗi trong lô → exit ≠ 0, manifest và thư mục asset không đổi.
6. Mọi file JSON / file chép ghi atomic (tạm + rename). Helper chép từ youtube-auto-short có ghi nguồn `youtube-auto-short@f47813d:<path>`.
7. `python -m pytest -q` PASS; test không gọi mạng (guard autouse); media test sinh bằng FFmpeg trong `tmp_path`, không commit file media.
8. `node scripts/quality-gate.mjs` PASS (có bước pytest) local trong env; CI "Quality" xanh trên PR.

## Required verification

IMPLEMENTER (mỗi lệnh < 5 phút):

- `python -m pytest -q` — AC1 (import package), AC2–AC7.
- `python -m animation_studio --help` — AC1.

ORCHESTRATOR:

- `pip install -e ".[dev]"` trong env mới `animation-studio` — AC1.
- `node scripts/quality-gate.mjs` — AC8.
- Chạy tay 2 lệnh với file thật nhỏ vào workspace tạm, xem `story.json` / `manifest.json` — AC3, AC4.
- `git check-ignore config.toml` — AC2.
- Link CI run xanh trên PR — AC8.

Tất cả required verification phải chạy và PASS trước READY.

## Manual test checklist (Tech Lead)

Không chạm database, security model hay public API contract (CLI nội bộ). Manual test là điểm danh.

- [ ] Tạo `config.toml` từ `config.example.toml`, chạy `import-story` với một file truyện thử, xem `~/animation-studio-data/projects/<id>/story/`.
- [ ] Chạy `import-assets` với 1 PNG + 1 WAV, xem `manifest.json`.

## Handoff

Không dùng.

## Result

- Main changes: package `src/animation_studio/` (`__main__`, `config`, `workspace`, `hashing`, `media`, `story`, `assets`), `pyproject.toml`, `.gitignore`, `config.example.toml`; CI cài Python 3.12 + FFmpeg + package; README setup / usage.
- Tests (`python -m pytest -q`: 18 passed):

  | AC | Test |
  |---|---|
  | AC1 | `test_cli.py::test_help_lists_commands`; `pip install -e ".[dev]"` trong env `animation-studio` (ORCHESTRATOR) |
  | AC2 | `test_cli.py::test_workspace_from_config_expands_home`, `::test_bad_project_id_no_files` (param ×3), `::test_missing_workspace_and_config`, `::test_gitignore_and_example`; `git check-ignore config.toml` |
  | AC3 | `test_story.py::test_import_verbatim_and_metadata`, `::test_required_flags`, `::test_reimport_same_unchanged_different_rejected` |
  | AC4 | `test_assets.py::test_image_manifest_and_alpha` (param alpha), `::test_audio_manifest`, `::test_license_required` |
  | AC5 | `test_assets.py::test_duplicate_sha_not_copied`, `::test_bad_file_in_batch_changes_nothing` (param `.gif` / PNG hỏng) |
  | AC6 | `test_assets.py::test_atomic_write_leaves_no_temp`; nguồn ghi trong docstring `workspace.py`, `hashing.py`, `media.py`, `conftest.py` |
  | AC7 | guard autouse `tests/conftest.py::_no_real_services`; media sinh bằng FFmpeg trong `tmp_path` |
  | AC8 | `node scripts/quality-gate.mjs` PASS local (có bước pytest); CI: xem PR |

- Diff + / − (app, test): app +332 / −0 (`src/` 313 + `pyproject.toml` 19); test +227 / −0; `quality.yml` +7 / −0; `README.md` +26 / −1.
- Helper mới (đã tìm, lý do không tái dùng): repo chưa có source trước task. Chép từ `youtube-auto-short@f47813d`: `atomic_write_bytes`, `atomic_write_json`, `utc_now`, `sha256_file`, guard `_no_real_services`, dạng probe. Viết mới (không có bản tương đương): `read_json`, `validate_project_id`, `project_dir`, `UserError`, `resolve_workspace`, `media.probe`.
- Review: ORCHESTRATOR review diff-first, không có finding chặn. Đã sửa tại chỗ: bỏ `canonical_json` (chưa dùng, ADR-001 A3; chép lại khi render key cần); `import-story` ghi `story.json` trước `source.txt` để crash giữa chừng được làm lại; bỏ import thừa trong test.
- Important findings / decisions: thư mục `assets/audio/` (không phải `audios`); manifest thêm `size_bytes`, audio thêm `sample_rate`, `channels`; `media.probe` từ chối ảnh thiếu `width` / `height` / `pix_fmt` (ffprobe nhận file text là video stream). Chạy tay: `import-story` (imported → unchanged), `import-assets` PNG RGBA (`pix_fmt: rgba`) + WAV 3 s (`duration_s: 3.0`) vào workspace tạm: đạt.
- Known limitations: lô asset chỉ all-or-nothing ở bước validate; lỗi IO khi đang chép có thể để lại file asset mồ côi (manifest không đổi, nhập lại sẽ ghi đè cùng tên). `project_id` bắt đầu bằng `-` bị argparse hiểu là option.
- PR:
