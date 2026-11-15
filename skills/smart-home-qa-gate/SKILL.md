---
name: smart-home-qa-gate
description: "Validate Home Assistant YAML and live entity contracts."
version: 1.0.0
author: Frank (Shamane2000), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [home-assistant, smart-home, yaml, entity-validation, qa, automation]
    related_skills: [requesting-code-review, systematic-debugging]
---

# Smart Home QA Gate Skill

Deterministic pre- and post-deploy verification for Home Assistant YAML packages, templates, scripts, and automations. Prevents ghost entities, broken Jinja templates, and silent `unavailable` states by validating YAML syntax and checking every referenced entity ID against the live Home Assistant `/api/states` API.

## When to Use

- Before and after modifying any Home Assistant `.yaml` file (automations, scripts, packages, templates, dashboards)
- When debugging why a Home Assistant automation, heating zone, or light control is not behaving as expected
- Don't use for: non-Home-Assistant YAML files (e.g., GitHub Actions or Docker Compose)

## Prerequisites

- Environment variables `HASS_URL` (e.g., `http://localhost:8123`) and `HASS_TOKEN` (Long-Lived Access Token) for live entity verification. Without them, the script runs in offline YAML-syntax & duplicate-key mode.

## How to Run

Run `scripts/ha_verify.py` via `terminal` against modified Home Assistant YAML files:

```
terminal(command="python3 ~/.hermes/skills/smart-home/smart-home-qa-gate/scripts/ha_verify.py path/to/package.yaml", timeout=60)
```

## Procedure

1. **Pre-edit baseline check:**
   - Read the target YAML file via `read_file` and check for competing triggers (e.g., duplicate `time_pattern`, legacy `schedule.*`, or conflicting `automation.*` writing to the same target entity).
   - *Completion criterion:* Single Source of Truth (SSoT) for the target actuator/state is identified.
2. **Run deterministic YAML & Live Entity validation (`scripts/ha_verify.py`):**
   - Execute `scripts/ha_verify.py <file.yaml>` via `terminal`.
   - The script verifies YAML syntax (supporting `!include`, `!secret`, `!input`), checks for duplicate mapping keys, and queries `$HASS_URL/api/states` to verify every referenced entity exists and is not `unavailable`.
   - *Completion criterion:* `ha_verify.py` exits with code `0` (`PASS`).
3. **Post-reload live readback:**
   - After reloading scripts/automations/templates in Home Assistant, wait 2–5 seconds and re-run `ha_verify.py` (or query `/api/states/<entity_id>`) to prove the live state matches expectations.
   - *Completion criterion:* Live state readback confirmed in `terminal` output.

## Pitfalls

- **Assuming an entity name without API verification:** Never guess `sensor.<room>_temperature`; always verify via `ha_verify.py` or `/api/states`.
- **Self-defined entities inside the same package:** `ha_verify.py` automatically recognizes `input_*`, `timer.*`, `script.*`, `automation.*`, and `sensor` definitions declared within the same YAML file so new definitions are not false-flagged before reload.

## Verification

Task is complete **only** when `scripts/ha_verify.py` exits `0` (`PASS`) and live entity states are verified.
