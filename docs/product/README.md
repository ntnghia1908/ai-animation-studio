# Product / Requirement Layer

Canonical requirement path:

`docs/product/requirements/REQ-<number>-<slug>.md`

Canonical Product Agent instructions:

`docs/product/PRODUCT_AGENT.md`

## Purpose

Convert:

```
IDEA → DISCOVERY → REQUIREMENT → READINESS → READY → configured ORCHESTRATOR adapter
```

The Product Agent runs through the configured product adapter. No local Product Agent CLI/API runner is required by Framework Core.

## What the Product Agent does

- interviews HUMAN LEAD;
- understands the user problem and workflow;
- captures functional requirements, rules and edge cases;
- writes observable acceptance criteria;
- validates readiness;
- creates the REQ file, branch, commit and GitHub PR.

It does not write application code or authorize implementation.

## Status

- `DRAFT`
- `NEEDS_CLARIFICATION`
- `READY`
- `OBSOLETE`

## READY meaning

`READY` means **ready for development planning**.

It does not mean architecture approved, task approved, implementation authorized or merge authorized.

## Next step

A READY requirement PR can be consumed by the configured ORCHESTRATOR adapter, which creates DRAFT task contracts using the existing task template.
