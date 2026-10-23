# Implementation Roadmap

| Metadata | Value |
|---|---|
| Status | PROPOSAL — NOT AUTHORITY (thứ tự phase: ADR-001 A4) |
| Date | 2026-10-23 |
| Basis | Kickoff §10; `docs/architecture/ARCHITECTURE_PROPOSAL.md`; Option A đã chọn (`docs/decisions/ADR-001-mvp-architecture-and-phasing.md`) |

Mỗi phase cần authorization riêng của HUMAN LEAD. Roadmap này không authorize phase nào. Checkpoint và task cụ thể sẽ được lập thành task contract sau khi boundary của phase được duyệt.

## P0 — Research & Framework Bootstrap (đã review)

Deliverable: 11 tài liệu của kickoff §12 cộng task contract `docs/tasks/P0-research-bootstrap.md` (PR #1). HUMAN LEAD review 2026-10-23: chấp nhận research + hướng Option A; tách P1 thành P0.1 → P1a → P1b (ADR-001).

## P0.1 — Checker fix, quality gate, CI (kế tiếp)

Sửa `product-check.mjs`, thêm `scripts/quality-gate.mjs` + test `node --test`, CI GitHub Actions trên PR, cài `requirement-to-task.yml`. Boundary nháp: `docs/decisions/P0.1-QUALITY-GATE-AUTHORIZATION-DRAFT.md`; task: `docs/tasks/P0.1-checker-quality-gate-ci.md`.

## P1a — Offline vertical slice (rất nhỏ)

Nhập truyện + ảnh / layer + giọng (nhập tay) → `shots.json` → animatic → một đoạn phim 30–60 s có chuyển động (camera move, 1 shot parallax, transition, phụ đề, nhạc nền). Chỉ CLI + FFmpeg; không Web UI, không AI provider, không GPU. Exit = quality gate tự động + HUMAN LEAD chấm điểm video. Boundary nháp: `docs/decisions/P1a-VERTICAL-SLICE-AUTHORIZATION-DRAFT.md`.

| Task (dự kiến) | Nội dung |
|---|---|
| P1a.1 | Skeleton package, workspace / atomic IO / hashing, import truyện + asset (manifest, provenance) |
| P1a.2 | `shots.json` + animatic |
| P1a.3 | Motion render: camera move, parallax, transition, phụ đề, nhạc nền, loudness |
| P1a.4 | Kiểm output tự động + chạy thật trên asset của HUMAN LEAD |

## P1b — Mở rộng sau khi xem video P1a

Chỉ xem xét **sau khi HUMAN LEAD xem video P1a**, theo thứ tự ưu tiên HUMAN LEAD chọn lúc đó:

- Review Studio LAN (D-05).
- Local AI: keyframe nhất quán, i2v Wan trên GPU server (D-07; experiment E2 / E3).
- TTS local (D-06, E4).
- Router + ledger + budget guard; tích hợp provider trả phí (D-11, E6).
- Pilot đầy đủ 60–90 s (D-09, D-12).

Experiment E1–E8 (`docs/research/ANIMATION_WORKFLOW_RESEARCH.md` §9): E1 (FFmpeg camera / parallax) thực chất được kiểm trong P1a. Các experiment còn lại chạy khi chuẩn bị P1b, mỗi cái cần HUMAN LEAD cho phép.

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
PR #1 merge + D-01/D-14 ─► P0.1 ─► (D-04, D-08) ─► P1a.1 ─► P1a.2 ─► P1a.3 ─► P1a.4 ─► HUMAN LEAD xem video
                                                                                         └► P1b (chọn hạng mục)
D-07 + E2/E3 ─► P2 (local AI)      E6 + D-11 ─► P3 (premium)
```

Writer thực tế là 1 (`docs/ai/project-profile.md` §7), nên các checkpoint chạy tuần tự trừ khi HUMAN LEAD duyệt pilot worktree.
