---
name: spec-driven-development
description: "Write and verify structured specs before implementation."
version: 1.0.0
author: Frank (Shamane2000), Hermes Agent (adapted from Addy Osmani agent-skills)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [specification, planning, requirements, acceptance-criteria, architecture]
    related_skills: [test-driven-development, requesting-code-review]
---

# Spec-Driven Development Skill

Enforces a concise, machine-checkable specification before non-trivial implementation starts. Prevents scope drift and hallucinated requirements by requiring explicit invariants and runnable verification commands for every requirement.

## When to Use

- Before implementing a multi-file feature, architectural change, or complex bug fix
- When requirements have ambiguities or competing constraints that need a clear contract
- Don't use for: trivial one-line fixes or typos

## How to Run

Validate a specification file with `scripts/validate_spec.py` via `terminal`:

```
terminal(command="python3 ~/.hermes/skills/software-development/spec-driven-development/scripts/validate_spec.py path/to/spec.md", timeout=30)
```

## Procedure

1. **Inspect existing codebase & constraints first:**
   - Use `search_files` and `read_file` to map existing interfaces, data models, and test runners before drafting the spec.
   - *Completion criterion:* Every file to be modified or extended is listed by its real repository path.
2. **Draft a structured spec (`write_file`) containing these 4 mandatory sections:**
   - `## Objective`: 2–3 sentences stating the exact problem and target outcome.
   - `## Invariants & Constraints`: Bullet list of hard rules that must not break (e.g., backward compatibility, memory limits, latency bounds).
   - `## Acceptance Criteria & Verification Commands`: Numbered criteria where each item includes a concrete runnable command (`pytest ...`, `curl ...`, etc.).
   - `## Out of Scope`: Explicit list of what will NOT be touched in this slice.
   - *Completion criterion:* `scripts/validate_spec.py <spec.md>` exits with code `0`.
3. **Implement against the spec:**
   - Execute implementation in small, testable slices (`test-driven-development`), running each verification command from the spec after each slice.
   - *Completion criterion:* All verification commands listed in the spec exit `0`.

## Pitfalls

- **Prose criteria without commands:** "System should be fast and reliable" is invalid. Replace with a measurable command and expected output.
- **Inventing file paths:** Never reference files in a spec that you have not verified with `search_files(target='files')`.

## Verification

Spec phase is complete when `scripts/validate_spec.py` exits `0` (`PASS`).
