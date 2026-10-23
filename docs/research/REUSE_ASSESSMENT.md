# Reuse Assessment — youtube-auto-short

| Metadata | Value |
|---|---|
| Status | RESEARCH REPORT — NOT AUTHORITY |
| Research date | 2026-10-23 |
| Reference | `ntnghia1908/youtube-auto-short` `main` @ `a94995a` (chỉ đọc; clone tạm ngoài repo) |
| Task | `docs/tasks/P0-research-bootstrap.md` |

Không sửa youtube-auto-short. Không thêm runtime dependency vào nó. Không chép toàn bộ repo. Báo cáo chỉ đề xuất; việc tái dùng cụ thể sẽ nằm trong task contract P1 (mục "Tái dùng" theo `docs/ai/workflow.md` §5).

## 1. Tổng quan reference repo [O]

- Python ≥ 3.11 (conda env, hatchling, src-layout `src/auto_short/`), khoảng 28k dòng `src/`, khoảng 31k dòng `tests/`, khoảng 6,5k dòng web JS / HTML / CSS.
- Pipeline theo stage có manifest (`ingest → transcript → analysis → selection → titling → render`), Ollama qua `urllib`, FFmpeg qua `subprocess`, web FastAPI trong LAN có mật khẩu, job runner theo làn, GPU worker Windows kéo việc qua HTTP lease.
- Đã adopt AI Dev Framework, có audit code-growth (`docs/audit/code-growth-report.md`).
- **License:** repo không có file `LICENSE` (GitHub `licenseInfo: null`) [O]. Cùng chủ sở hữu (HUMAN LEAD) nên chép chọn lọc không vướng bên thứ ba, nhưng nên ghi rõ trong commit / task "nguồn: youtube-auto-short @ <sha>, cùng tác giả". Font `BeVietnamPro-Regular.ttf` đi kèm `OFL.txt` (SIL OFL), tái dùng được nếu giữ OFL.

## 2. Ma trận tái dùng

| Khu vực | Vị trí reference | Khuyến nghị | Lý do / điều chỉnh |
|---|---|---|---|
| Ghi atomic, đọc JSON tolerant, UTC timestamp | `workspace.py` (`atomic_write_bytes`, `atomic_write_json`, `read_json_dict`, `utc_now`) | **Chép code** (nhỏ, khoảng 60 dòng) | Ổn định, đã test. Audit cho thấy các helper này từng bị viết lại 7 lần → đặt một chỗ duy nhất ngay từ đầu |
| Stage runner có manifest, skip khi up-to-date, mark downstream stale, record failure | `workspace.py` (`run_stage`, `check_up_to_date`, `mark_downstream_stale`) | **Tái dùng pattern, viết lại theo domain** | Studio có stage theo *shot* và *project*, không theo *episode*. Giữ ý tưởng `inputs + config_hash → skip / stale` cho resume / recovery |
| Hash file có cache theo mtime, `canonical_json`, `config_hash` | `hashing.py` (47 dòng) | **Chép code** | Cần cho asset registry (M3 / M10) và render key |
| Probe media, concat, normalize encode | `compilation/probe.py`, `compilation/assemble.py` (khoảng 215 dòng) | **Chép có chọn lọc** | Ghép clip shot thành timeline; kiểm tương thích trước concat copy |
| Render FFmpeg: chạy lệnh, kiểm output (số khung, fps), `render_key` để tái dùng output, encode song song | `render/stage.py` (`_run`, `probe_media`, `verify_output`, `render_key`, `_encode_all`) | **Tái dùng pattern** | Layout 9:16 / title Short không dùng được. Lấy cách verify output và render key |
| Đo chữ / ngắt dòng / font tiếng Việt | `render/text.py` + font OFL | **Tái dùng có điều kiện** | Hữu ích cho subtitle burn-in; cân nhắc dùng `subtitles` / ASS của FFmpeg thay vì tự vẽ |
| Config TOML (`tomllib`), `config.example.toml` commit, `config.toml` gitignored | `config.py` (816 dòng) | **Tái dùng convention, không chép file** | File quá lớn, gắn domain cũ |
| Ollama qua `urllib` (không dependency), preflight, prompt có version, validate output, log quyết định AI | `selection/`, `titling/`, `pipeline.py` preflight | **Tái dùng pattern** | Áp cho M2 Screenwriter: prompt versioned, artifact có input reference để review |
| Job runner theo làn (prepare / ai / render), tạm dừng, lưu hàng đợi | `web/jobs.py` (2.055 dòng) | **Không chép**; tham khảo khái niệm | God-file, gắn chặt YouTube. P1 chỉ cần hàng đợi đơn giản 1 worker |
| Web FastAPI LAN + mật khẩu + cookie, phục vụ file có `Range` | `web/app.py`, `docs/decisions/CP8.3-web-contract.md` | **Tái dùng decision / pattern** | Security model LAN đã được HUMAN LEAD duyệt ở project cũ, là tiền lệ tốt; ở project này vẫn là decision gate mới. Tránh lặp `app.py` god-file và `app.js` 3.614 dòng: tách router từ đầu |
| GPU worker kéo việc qua HTTP: lease, heartbeat, token, segment idempotent, may-run / preempt nhường Ollama | `enhance/`, `tools/enhance_worker/`, `docs/decisions/CP13.1-enhance-worker-contract.md` | **Tái dùng thiết kế giao thức (P2)** | Rất khớp với "Optional GPU workers": worker ComfyUI / Wan ở máy GPU kéo shot job từ server; đã giải quyết dùng chung GPU với Ollama |
| Chốt chặn test không gọi dịch vụ thật (autouse fixture chặn cổng Ollama / host ngoài) | `tests/conftest.py` (`_no_real_services`) | **Chép pattern** | Bắt buộc với provider trả phí: test không được gọi API thật |
| Marker `slow`, `pytest -n auto`, fixture video sinh bằng FFmpeg (`make_video`) | `pyproject.toml`, `tests/conftest.py` | **Tái dùng pattern** | |
| Logging theo stage | rải rác | Tái dùng convention | |
| Audit code growth: reuse-before-write, xóa code bị thay, AC → test | `docs/audit/code-growth-report.md` | **Áp dụng từ ngày đầu** | Đã thành rule ở framework v4.4 (FW-GROWTH-01) |

## 3. Không tái dùng

- Ingest YouTube / `yt-dlp`, transcript / Whisper, shot detection, chọn clip, titling, Đọc Kinh, community post, playlist / bộ kinh: domain khác.
- Script bench một lần trong `scripts/`, `tools/` (audit gọi là phần thừa lớn nhất).
- Toàn bộ `web/static/app.js`.

## 4. Cách tái dùng đề xuất

1. Mỗi task P1 khi cần một helper ở trên: chép file / hàm cụ thể, ghi nguồn `youtube-auto-short@a94995a:<path>` trong task Result và trong docstring module. Kèm test tương ứng (chép test gốc nếu có).
2. Không tạo package dùng chung giữa hai repo ở P1. Việc này là significant shared abstraction (decision gate) và tạo coupling. Xem xét lại ở P4 nếu thấy trùng lặp đáng kể.
3. Ưu tiên tái dùng **decision record** (CP2 workspace, CP7 render verify, CP8.3 web, CP13.1 worker) làm tài liệu tham khảo khi soạn decision P1 / P2 của project này. Không trỏ authority sang repo kia.

## 5. Ước lượng

Phần chép trực tiếp (atomic IO, hashing, probe / assemble, test guard) khoảng 400–500 dòng kèm test. Phần còn lại là pattern / thiết kế. Không có runtime dependency mới phát sinh từ việc tái dùng.
