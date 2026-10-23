# Implementation Roadmap

| Metadata | Value |
|---|---|
| Status | PROPOSAL — NOT AUTHORITY |
| Date | 2026-10-23 |
| Basis | Kickoff §10; `docs/architecture/ARCHITECTURE_PROPOSAL.md` (Option A, chưa duyệt) |

Mỗi phase cần authorization riêng của HUMAN LEAD. Roadmap này không authorize phase nào. Checkpoint và task cụ thể sẽ được lập thành task contract sau khi boundary của phase được duyệt.

## P0 — Research & Framework Bootstrap (đang ở gate review)

Deliverable: 11 tài liệu của kickoff §12 cộng task contract `docs/tasks/P0-research-bootstrap.md`. Gate: **P0 READY FOR HUMAN REVIEW — P1 NOT YET AUTHORIZED**.

## P0.5 — Experiments không tốn phí (đề xuất, chạy song song đầu P1)

E1 (FFmpeg camera / parallax), E4 (TTS tiếng Việt), E5 (lip-sync tối thiểu) chạy trên laptop. E2 / E3 (Wan, Qwen-Image-Edit) chạy trên GPU server khi D-07 được xác nhận. Kết quả ghi vào `docs/research/experiments/`. Đây là việc **nghiên cứu**, không phải code sản phẩm; vẫn cần HUMAN LEAD cho phép vì cài model / phần mềm.

## P1 — Offline MVP (animatic-first, không cần GPU, không trả phí)

Mục tiêu: đi hết quy trình tới MP4 cho pilot bằng phương thức 1 (still + camera) và 5 (nhập tay).

| Checkpoint | Nội dung | Module |
|---|---|---|
| P1.0 | Skeleton package, config, storage (atomic IO, hashing), test guard; pilot S1 của framework | storage |
| P1.1 | Story Library + Adaptation revision (nhập tay / LLM Ollama tùy chọn), provenance | M1, M2 |
| P1.2 | Bible + Asset registry (nhập ảnh, approval) | M3, M10 |
| P1.3 | Voice: nhập audio + (nếu D-06 duyệt) 1 engine TTS local; đo thời lượng | M4 |
| P1.4 | Storyboard + animatic render (FFmpeg: still + camera, subtitle, audio) | M5, M8 |
| P1.5 | Router (luật) + adapter `ManualImport` / `StillCamera` + ledger + budget guard (chưa có paid adapter) | M6, M7, M10 |
| P1.6 | Timeline + final render 16:9 + music / SFX | M8 |
| P1.7 | Review Studio LAN tối thiểu (overview, script, bible, animatic, shot, render; approve / reject / regenerate request) | M9 |
| P1.8 | Pilot run: truyện pilot → animatic → MP4 (premium shot = nhập tay nếu HUMAN LEAD tự sinh ngoài) | tất cả |

Exit: AC-001…AC-008 của REQ-001. AC-007 (so sánh phương thức) có thể đạt bằng still so với clip nhập tay.

## P2 — Local Animation

- `ComfyUIWorker` adapter + giao thức lease cho GPU node (tái dùng thiết kế CP13.1).
- Wan 2.2 i2v (theo kết quả E2); keyframe nhất quán bằng image-edit local (E3).
- Đánh giá cutout / puppet (E7) và lip-sync (E5) cho nhân vật lặp lại.
- Tối ưu style đồng nhất (LUT, grain), cost / quality.

## P3 — Premium AI Integration

- So sánh provider (E6) và chọn 1 provider (decision).
- 1 paid adapter + `BudgetGuard` đầy đủ + approval từng lần sinh + retry theo shot.
- Tùy chọn: Figma Weave như sandbox, output nhập tay.

## P4 — Production Studio

Review tốt hơn, batch, template nhân vật / bối cảnh tái dùng giữa các phim, phim 7–10 phút, có thể SQLite cho ledger.

## P5 — Buddhist Stories

Workflow source-fidelity riêng: xác minh nguồn, review nội dung, template lời dẫn / phong cách, quy tắc trích dẫn kinh điển.

## Phụ thuộc chính

```text
D-02/03/04/05 ─► P1.0 ─► P1.1 ─► P1.2 ─► P1.4 ─► P1.6 ─► P1.8
                           └► P1.3 ┘   └► P1.5 ┘   P1.7 (song song sau P1.2, writer = 1)
D-07 + E2/E3 ─► P2      E6 + D-11 ─► P3
```

Writer thực tế là 1 (`docs/ai/project-profile.md` §7), nên các checkpoint chạy tuần tự trừ khi HUMAN LEAD duyệt pilot worktree.
