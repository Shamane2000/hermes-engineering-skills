---
name: multi-domain-qa-gate
description: "Run mandatory domain QA gates with hard exit-code checks."
version: 1.0.0
author: Frank (Shamane2000), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [qa, quality-gate, verification, testing, pre-commit, multi-domain]
    related_skills: [requesting-code-review, test-driven-development, sdlc-review]
---

# Multi-Domain QA Gate Skill

Universal, zero-prose quality gate for software, Smart Home, IoT/embedded, and infrastructure tasks. Automatically detects the project domain and executes deterministic syntax, hygiene, secret, and test checks with a hard `0`/`1` exit code so agents cannot claim completion without machine-verified proof.

## When to Use

- Mandatory final verification before committing, pushing, or moving any task to `review`/`done`
- When working across diverse domains (Python, JS/TS, Home Assistant YAML, Embedded/IoT, Shell/Infra)
- Don't use for: read-only research queries that modify zero files

## How to Run

Execute `scripts/qa_runner.py` via `terminal` in the target workspace:

```
terminal(command="python3 ~/.hermes/skills/devops/multi-domain-qa-gate/scripts/qa_runner.py --workspace .", timeout=120)
```

## Procedure

1. **Run the universal QA runner (`scripts/qa_runner.py`):**
   - Inspects git working tree for accidental virtualenv/artifact pollution (`venv/`, `node_modules/`, `.pyc`, `__pycache__`).
   - Byte-compiles / syntax-checks all modified `.py`, `.sh`, `.json`, and `.yaml` files.
   - Scans diff for hardcoded secrets or dangerous shell patterns.
   - Runs the repository's native test suite (`pytest`, `npm test`, `cargo test`, `go test`) if present.
   - *Completion criterion:* `qa_runner.py` outputs `PASS` and exits with code `0`.
2. **Paste the real QA output into the task handoff:**
   - Never summarize QA as "tests passed" without including the exact `qa_runner.py` summary line.
   - *Completion criterion:* Verbatim `PASS` summary included in final response or Kanban comment.

## Pitfalls

- **Committing `venv/` or `node_modules/`:** `qa_runner.py` immediately fails (`EXIT 1`) if untracked or staged virtual environments exist inside a skill or project directory.

## Verification

Task is complete **only** when `scripts/qa_runner.py` exits `0` (`PASS`).
