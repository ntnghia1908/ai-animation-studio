# Requirement → Task handoff

When a requirement is READY, Claude acts as ORCHESTRATOR.

Read, in order:
1. AGENTS.md
2. docs/ai/project-profile.md
3. docs/workflow/current-state.md
4. the READY REQ-xxx file
5. relevant source/tests and the task template

Then:
1. Classify the work as S0/S1/S2.
2. Detect decision gates.
3. Split the requirement into vertical task slices.
4. Create docs/tasks/TASK-*.md from the existing template.
5. Add Requirement: REQ-xxx and Requirement elements: FR-/AC- IDs.
6. Set every generated task to DRAFT.
7. Keep Implementation authorized: NO.
8. Stop and report what HUMAN LEAD must approve.

Do not implement application code during requirement handoff.

REQ READY is never interpreted as Implementation authorized: YES.