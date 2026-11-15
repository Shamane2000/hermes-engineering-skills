---
name: architecture-decision-records
description: "Author concise ADRs and keep architecture docs synced."
version: 1.0.0
author: Frank (Shamane2000), Hermes Agent (adapted from Addy Osmani agent-skills)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [adr, documentation, architecture, decisions, source-driven]
    related_skills: [spec-driven-development, requesting-code-review]
---

# Architecture Decision Records (ADR) Skill

Authors source-verified Architecture Decision Records and keeps living architecture documentation synchronized with actual code. Replaces superseded claims in-place instead of appending contradictory notes.

## When to Use

- Recording a significant architectural, protocol, or infrastructure decision
- Updating documentation after modifying system behavior, schemas, or deployment topology
- Don't use for: routine bug fixes that do not alter architecture or contracts

## How to Run

Validate ADR and documentation integrity with `scripts/adr_check.py`:

```
terminal(command="python3 ~/.hermes/skills/software-development/architecture-decision-records/scripts/adr_check.py docs/", timeout=30)
```

## Procedure

1. **Verify against actual source code first:**
   - Never document from memory. Use `search_files` and `read_file` to confirm every referenced file path, class/function name, port, and configuration key exists in the codebase.
   - *Completion criterion:* Every code symbol or path mentioned in the ADR is verified in the repo.
2. **Consolidate in-place (No Stale Contradictions):**
   - When a new decision supersedes an old behavior, update the active concept/architecture doc in-place (`patch`) and mark any replaced ADR with `Status: Superseded by ADR-NNNN`.
   - *Completion criterion:* `scripts/adr_check.py` exits `0` with no broken file references or missing status headers.

## Pitfalls

- **Appending without cleaning old text:** Leaving outdated parameters in the top half of a doc while appending "Update:" at the bottom causes future agents to read the wrong value.

## Verification

Run `scripts/adr_check.py` via `terminal` and confirm `Exit Code 0`.
