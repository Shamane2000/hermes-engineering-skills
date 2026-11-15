---
name: api-and-interface-design
description: "Design consistent REST, RPC, and module API contracts."
version: 1.0.0
author: Frank (Shamane2000), Hermes Agent (adapted from Addy Osmani agent-skills)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [api, rest, interface-design, contracts, migration, backward-compatibility]
    related_skills: [spec-driven-development, test-driven-development]
---

# API and Interface Design Skill

Contract-first design and safe evolution for HTTP APIs, CLI interfaces, and internal library modules. Ensures predictable schemas, explicit error envelopes, idempotency, and non-breaking migrations.

## When to Use

- Designing or modifying a REST/HTTP endpoint, WebSocket message format, CLI subcommand, or public module signature
- Deprecating or migrating an existing interface used by external callers or other services
- Don't use for: purely internal private helper functions within a single file

## Procedure

1. **Audit existing callers and conventions first:**
   - Use `search_files` across the repository to locate all callers of the target endpoint or function and read 2–3 sibling endpoints via `read_file` to match naming, pagination, and error conventions.
   - *Completion criterion:* Every existing caller and response schema is identified before editing.
2. **Enforce strict contract rules:**
   - **Input validation at the boundary:** Validate types, ranges, and required fields before business logic executes; return `400`/`422` with structured field errors on invalid input.
   - **Consistent error envelope:** Never mix plain-text 500s with JSON errors; return a consistent structure (`{"error": {"code": "...", "message": "..."}}`).
   - **Idempotency & timeouts:** State-mutating retries (`PUT`, `DELETE`, or keyed `POST`) must be safe to repeat.
   - *Completion criterion:* Boundary validation and error responses are covered by unit/integration tests.
3. **Safe deprecation & migration (Expand-Migrate-Contract):**
   - When renaming or changing a field/endpoint, **expand** (accept both old and new formats), **migrate** callers via `patch`, and **contract** only after `search_files` confirms zero remaining uses of the old signature.
   - *Completion criterion:* `search_files` shows 0 unmigrated callers and test suite exits `0`.

## Pitfalls

- **Silent breaking changes:** Changing a JSON key name or return type from `list` to `dict` without checking frontend/client consumers breaks production immediately.
- **Unbounded list endpoints:** Every collection endpoint must enforce a default `limit` cap.

## Verification

Run the project's API/contract test suite via `terminal` and confirm `Exit Code 0` for both happy-path and invalid-input (`4xx`) test cases.
