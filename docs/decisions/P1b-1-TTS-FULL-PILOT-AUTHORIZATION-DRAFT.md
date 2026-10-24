# P1b-1 Implementation Authorization Boundary — TTS local + pilot đầy đủ

| Metadata | Value |
|---|---|
| Status | ACCEPTED |
| Accepted by | HUMAN LEAD, 2026-10-24 (§7 đã trả lời; D-06 chốt sau E4) |
| Date | 2026-10-24 |
| Basis | `docs/decisions/ADR-001-mvp-architecture-and-phasing.md` (A3 ràng buộc tăng trưởng, A4 thứ tự, A5 D-06 / D-09 / D-12 hoãn tới P1b) |
| Requirement | `docs/product/requirements/REQ-001-animation-studio-mvp.md` (một phần, xem §8) |
| Prerequisite | P1a đạt exit gate (`docs/tasks/P1a.4-output-qc-pilot.md` Result, PR #11) |

Boundary có hiệu lực từ 2026-10-24. Mỗi task P1b-1 vẫn cần task contract được HUMAN LEAD duyệt trước khi implement. Engine TTS chỉ được thêm sau khi D-06 được chốt (§7).

## 1. Chia P1b

HUMAN LEAD 2026-10-24 chọn cả bốn hạng mục roadmap §P1b, thứ tự TTS → pilot đầy đủ, và đồng ý chia thành ba boundary nối tiếp. Bước sau chỉ soạn khi bước trước đạt exit gate.

| Boundary | Nội dung | Điều kiện riêng |
|---|---|---|
| **P1b-1** (file này) | TTS local (D-06, E4) + pilot đầy đủ 60–90 s (D-09, D-12) | không GPU, không chi tiêu |
| P1b-2 | Local AI trên GPU (D-07, E2 / E3) + Review Studio LAN (D-05) | GPU nằm ở máy Windows khác trong LAN (HUMAN LEAD 2026-10-24); xem ghi chú dưới; security model LAN |
| P1b-3 | Router + ledger + budget guard + provider trả phí (D-11, E6) | mỗi lần chi tiêu duyệt riêng, có trần chi phí |

Ghi chú GPU cho P1b-2 (lấy từ `ntnghia1908/youtube-auto-short`, chỉ đọc, **không phải authority**; kiểm lại khi soạn P1b-2):

- Hai máy Windows: RTX 3090 (24 GB, chạy chung Ollama) và RTX 3050 (`docs/guides/enhance-worker-windows.md` bên đó).
- Máy GPU chủ động SSH vào server (tunnel `setup-gpu-node-v4.ps1`); server dùng dịch vụ GPU qua cổng loopback (Ollama `127.0.0.1:11437`), giao việc theo kiểu worker kéo việc qua tunnel (enhance worker). Server không SSH thẳng vào máy GPU; file chuyển bằng `scp` từ phía máy GPU.
- Cả hai card đang làm enhance cho youtube-auto-short (3090 ở mức 100 % GPU, 2026-10-04) → P1b-2 phải chốt cách chia GPU với project đó.

## 2. Mục tiêu P1b-1

Ra **một phim pilot 60–90 s, 12–16 shot**, trong đó giọng kể và giọng nhân vật được **sinh bằng TTS tiếng Việt chạy local trên server (CPU)**, thời lượng shot lấy từ giọng. Ảnh vẫn nhập tay. Không GPU, không AI provider trả phí, không đăng ký dịch vụ.

## 3. Luồng

```text
shots.json (lời kể / thoại theo shot, voice id)
        │
        ▼
  voice  ─► audio/<shot>.wav + manifest (engine, model, voice, text hash)   ← TTS local, cache theo key
        │      thời lượng shot = độ dài giọng (+ đệm)
        ▼
  animatic ─► animatic.mp4    (HUMAN LEAD duyệt nhịp)
        ▼
  render   ─► film.mp4 + render/qc.json
```

- Audio nhập tay (luồng P1a) vẫn dùng được; một shot dùng TTS **hoặc** audio nhập tay.
- Tên lệnh, field `shots.json` và cách ghép nhiều câu thoại trong một shot do task contract chốt.

## 4. Trong boundary

1. **E4 — so sánh TTS** (`docs/research/ANIMATION_WORKFLOW_RESEARCH.md` §9):
   - ứng viên local: VieNeu-TTS v3 Turbo (Apache-2.0) và Piper `vi_VN-vais1000-medium` (đã dùng làm bản xem trước P1a.4); tối đa thêm 1 engine local open-license khác nếu ORCHESTRATOR tìm được;
   - chạy trong env tạm **ngoài repo**, chỉ CPU server; không dịch vụ cần đăng ký tài khoản;
   - đầu vào: 3 đoạn khoảng 30 s (lời kể, thoại nhân vật, đoạn dày từ Hán-Việt);
   - đo: thời gian sinh / giây audio, RAM, kích thước model, license code + weights + voice;
   - HUMAN LEAD nghe và chấm (dễ hiểu, tự nhiên, Hán-Việt, hợp giọng kể chuyện), sau đó chốt D-06;
   - kết quả: `docs/research/TTS_E4_RESULTS.md`, audio mẫu không commit.
2. **Lệnh `voice`** (phần tối thiểu của M4) dùng engine đã chốt ở D-06:
   - adapter engine mỏng, đủ thay engine sau này; không xây framework provider chung;
   - giọng kể + ít nhất 2 giọng nhân vật (FR-004), cấu hình theo voice id;
   - cache theo key (engine, model, voice, tham số, text) — không sinh lại khi không đổi, giống resume P1a;
   - manifest ghi engine, phiên bản, model, license; audio đi vào asset manifest như asset P1a;
   - thời lượng shot suy từ giọng; phụ đề lấy từ chính text đã đọc;
   - tất định: cùng input → cùng audio PCM hash, giữ AC-006. Nếu engine đã chốt không tất định, task contract phải nêu cách xử lý (ví dụ chỉ hash file đã cache).
3. **Mở rộng `shots.json`** để mang text / voice theo shot, tương thích ngược với file v1 của P1a.
4. **QC cho phim dài hơn:** khoảng thời lượng hợp lệ của `duration_range` lấy từ cấu hình / project thay vì cố định 30–60 s; các mục QC khác giữ nguyên.
5. **Tăng tốc encode cuối** (§7 P1b-1-4) (hiện 1 thread, bước chậm nhất — Known limitation P1a.4), không đổi output.
6. **Pilot đầy đủ** 60–90 s, 12–16 shot, mở rộng "Tổ kiến và nhà ở" (chỉ demo nội bộ), phong cách theo D-12; chạy trên workspace thật `~/animation-studio-data`. Kèm trang style ngắn (D-12).
7. Dependency: engine TTS đã chốt, đặt trong **optional extra** (ví dụ `[tts]`) để `pip install -e ".[dev]"` và CI không phải tải model. Weights tải về workspace / cache ngoài repo, không commit. Test dùng engine giả (fake), không tải model, không gọi mạng.
8. Tài liệu: task contract, module map trong project-profile, current-state, README mục chạy `voice`.

## 5. Ngoài boundary

- Mọi thứ thuộc P1b-2 / P1b-3: GPU, sinh ảnh / i2v bằng AI trong code, Review Studio / Web UI, router, ledger, budget guard, provider trả phí.
- TTS qua API / dịch vụ cloud, kể cả free tier cần đăng ký.
- **Clone giọng người thật** khi chưa có đồng ý rõ ràng của người đó; không clone giọng người đọc audiobook.
- LLM screenwriter, lip-sync, nhạc sinh bằng AI.
- Đăng phim lên YouTube hay bất kỳ nơi công khai nào (D-13 chưa quyết).

## 6. Quality gate (exit P1b-1)

**Tự động:** 9 mục QC của P1a (`docs/tasks/P1a.4-output-qc-pilot.md`) PASS trên pilot, với `duration_range` = 60–90 s.

**HUMAN LEAD chấm** (thang 1–5, ghi vào task Result của pilot):

- giọng TTS dễ nghe, đọc đúng (kể cả Hán-Việt);
- giọng nhân vật phân biệt được với giọng kể;
- nhịp kể khớp hình, không hụt / thừa;
- hình ảnh nhất quán nhân vật và phong cách qua 12–16 shot;
- tổng thể: "đủ làm phim mẫu dài".

Ngưỡng đề xuất: không mục nào < 3 và mục tổng thể ≥ 4. HUMAN LEAD có thể kết luận không chấm điểm như P1a.4; Result ghi rõ cách kết luận. Chưa đạt thì lặp lại trong P1b-1, chưa mở P1b-2.

## 7. Decision của HUMAN LEAD (2026-10-24)

| ID | Câu hỏi | Quyết định |
|---|---|---|
| P1b-1-1 | Phạm vi §4 / §5 và exit gate §6 | **ACCEPTED** như đề xuất |
| D-06 | Engine TTS | **Chốt sau E4** (task P1b-1.1), dựa trên điểm HUMAN LEAD nghe. Boundary cho phép thêm đúng một engine đã chốt làm optional dependency. Nếu không engine local nào đạt: pilot dùng audio nhập tay / thu âm, TTS quay lại sau |
| D-09 | Số shot pilot | **ACCEPTED**: 12–16 shot, 60–90 s (nhịp 6–9 s/shot; vài shot là reframe của cùng ảnh) |
| D-12 | Phong cách hình ảnh | **ACCEPTED**: giữ 2D Á Đông như pilot P1a, ảnh HUMAN LEAD tạo bằng công cụ ngoài; thêm một trang style ngắn (bảng màu, nét, tham chiếu nhân vật). Không sinh ảnh trong code |
| P1b-1-2 | Truyện cho pilot | **ACCEPTED**: mở rộng "Tổ kiến và nhà ở"; quyền bản dịch chưa xác nhận → chỉ demo nội bộ (D-08) |
| P1b-1-3 | Giọng nhân vật | **ACCEPTED**: 1 giọng kể + 2 giọng nhân vật từ voice có sẵn của engine, không clone |
| P1b-1-4 | Tăng tốc encode cuối | **ACCEPTED**: luôn làm (task P1b-1.3), không đổi output |

## 8. Truy vết tới REQ-001

| REQ-001 | Mức trong P1b-1 |
|---|---|
| FR-004 Voice & timing | có: TTS local, giọng kể + ≥ 2 giọng nhân vật, thời lượng shot từ giọng |
| FR-005 Storyboard & animatic | giữ như P1a, dùng audio TTS |
| FR-008 Manual import | giữ (ảnh; audio nhập tay vẫn dùng được) |
| FR-009 Timeline & render | giữ, phim 60–90 s |
| FR-012 Resume | mở rộng cache cho TTS |
| AC-006 Reproducible render | giữ (xem §4 mục 2) |
| FR-002, FR-003, FR-006 (ngoài phương thức 1), FR-007, FR-010, FR-011 | không (P1b-2 / P1b-3 hoặc sau) |

## 9. Vận hành

- `dual-agent`, Claude Code ORCHESTRATOR; IMPLEMENTER chọn theo task từ danh sách `docs/ai/project-profile.md` §7. Writer = 1.
- Dự kiến 4 task, mỗi task một session:
  1. **P1b-1.1 E4** — chạy so sánh TTS ngoài repo, viết `TTS_E4_RESULTS.md`; HUMAN LEAD nghe, chốt D-06. Không sửa source app.
  2. **P1b-1.2 `voice`** — adapter engine, mở rộng `shots.json`, cache, manifest, QC `duration_range` cấu hình được.
  3. **P1b-1.3** — tăng tốc encode cuối.
  4. **P1b-1.4 pilot đầy đủ** — kịch bản 12–16 shot, ảnh, chạy pilot, QC, HUMAN LEAD chấm.
- Ngân sách diff ≤ khoảng 800 dòng app / PR.
- Branch `feature/p1b1-<task>` (task E4: `docs/p1b1-e4-tts`); READY → push + PR; HUMAN LEAD merge.
