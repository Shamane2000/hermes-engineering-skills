---
name: security-and-hardening
description: "Audit diffs and codebases for secrets, injection, auth."
version: 1.0.0
author: Frank (Shamane2000), Hermes Agent (adapted from Addy Osmani agent-skills)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [security, hardening, secrets, injection, owasp, audit, pre-commit]
    related_skills: [requesting-code-review, test-driven-development]
---

# Security and Hardening Skill

Deterministic security verification for code changes and repositories before commit or deployment. Combines automated static pattern checks (`scripts/security_audit.py`) with targeted verification of trust boundaries, authentication, and input handling.

## When to Use

- Before committing or merging code that touches authentication, APIs, shell execution, SQL, file paths, or external network calls
- When auditing a repository for leaked credentials, hardcoded private IPs, or injection vulnerabilities
- Don't use for: offensive penetration testing or network port scanning

## How to Run

Run the bundled deterministic scanner via `terminal`:

```
terminal(command="python3 ~/.hermes/skills/software-development/security-and-hardening/scripts/security_audit.py --repo .", timeout=60)
```

Or scan only staged/working git changes:

```
terminal(command="python3 ~/.hermes/skills/software-development/security-and-hardening/scripts/security_audit.py --repo . --diff-only", timeout=60)
```

## Procedure

1. **Run the deterministic security scanner** via `terminal` (`scripts/security_audit.py`).
   - *Completion criterion:* Command exits with code `0`, or every flagged line is inspected via `read_file`.
2. **Verify trust boundaries on modified endpoints/inputs:**
   - Use `search_files` and `read_file` on modified files to confirm all external inputs (HTTP params, webhook payloads, CLI args, filenames) are validated and parameterized before reaching SQL, shell, or filesystem sinks.
   - *Completion criterion:* Zero unparameterized SQL strings, zero `shell=True` with user input, and path traversal checks (`Path.resolve().is_relative_to(...)`) on file uploads/reads.
3. **Verify secret & network hygiene:**
   - Ensure credentials are read exclusively from environment variables or secret stores, never committed in source or skill files.
   - *Completion criterion:* `security_audit.py` reports `0` secret leaks and `0` unexpected hardcoded private IPs.
4. **Fix and re-verify:**
   - Apply fixes with `patch` and re-run `scripts/security_audit.py`.
   - *Completion criterion:* `security_audit.py` exits `0` (`PASS`).

## Pitfalls

- **Do not silence findings with comments unless verified safe:** If a regex matches a dummy test token in `tests/`, verify it is clearly synthetic before adding `# nosec`.
- **Outgoing HTTP timeouts:** Every `requests.*` or `httpx.*` call must pass an explicit `timeout=`, otherwise a hung upstream blocks worker threads indefinitely.

## Verification

A security pass is complete **only** when `scripts/security_audit.py` returns `EXIT 0 (PASS)` in `terminal` output.
