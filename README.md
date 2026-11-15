# Hermes Engineering & Multi-Domain QA Skills (`hermes-engineering-skills`)

Native, deterministic software-engineering and multi-domain Quality Assurance (QA) skills for [**Hermes Agent**](https://github.com/NousResearch/hermes-agent), strictly authored to the official `hermes-agent-skill-authoring` v2.0 hardline specification.

## Why This Repository Exists

1. **100% Hermes-Native (Zero Claude Code Lock-in):**
   Many popular community skill collections (such as [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills)) target Claude Code conventions (`CLAUDE.md`, `.cursorrules`, slash commands, Claude subagent tools) that do not exist natively in Hermes Agent. This repository adapts those engineering methodologies into native Hermes tool invocations (`terminal`, `read_file`, `search_files`, `patch`, `delegate_task`).
2. **Engineered for Cost-Effective & Open-Weight Models (DeepSeek, Qwen, GLM, Flash):**
   Mid-tier and open-weight models suffer from context dilution when fed long prose essays and often claim *"I verified all edge cases"* without running a single check. Every QA skill in this collection ships with a **deterministic Python helper script (`scripts/*.py`)** that outputs a hard **`Exit Code 0` (`PASS`) or `1` (`FAIL`)**, making hallucinated QA impossible.
3. **Zero Machine-Local Paths or Hardcoded IPs:**
   All skills and helper scripts are 100% portable and configured via standard environment variables or CLI flags.

---

## Quick Start (Hermes Skills Hub Tap)

Add this repository as a first-class skill tap in Hermes:

```bash
hermes skills tap add Shamane2000/hermes-engineering-skills
```

Browse, install, and automatically update skills:

```bash
# Search or inspect skills
hermes skills search qa-gate

# Install individual skills
hermes skills install Shamane2000/hermes-engineering-skills/skills/security-and-hardening
hermes skills install Shamane2000/hermes-engineering-skills/skills/spec-driven-development
hermes skills install Shamane2000/hermes-engineering-skills/skills/api-and-interface-design
hermes skills install Shamane2000/hermes-engineering-skills/skills/performance-and-observability
hermes skills install Shamane2000/hermes-engineering-skills/skills/architecture-decision-records
hermes skills install Shamane2000/hermes-engineering-skills/skills/smart-home-qa-gate
hermes skills install Shamane2000/hermes-engineering-skills/skills/embedded-iot-qa-gate
hermes skills install Shamane2000/hermes-engineering-skills/skills/multi-domain-qa-gate

# Update all installed hub skills anytime
hermes skills update
```

---

## Included Skills

| Skill | Category | Description (`<= 60 chars`) | Bundled Deterministic Gate (`scripts/`) |
| :--- | :--- | :--- | :--- |
| **`security-and-hardening`** | `software-development` | `Audit diffs and codebases for secrets, injection, auth.` | `scripts/security_audit.py` |
| **`spec-driven-development`** | `software-development` | `Write and verify structured specs before implementation.` | `scripts/validate_spec.py` |
| **`api-and-interface-design`** | `software-development` | `Design consistent REST, RPC, and module API contracts.` | — |
| **`performance-and-observability`** | `software-development` | `Profile bottlenecks and add structured logs and metrics.` | — |
| **`architecture-decision-records`** | `software-development` | `Author concise ADRs and keep architecture docs synced.` | `scripts/adr_check.py` |
| **`smart-home-qa-gate`** | `smart-home` | `Validate Home Assistant YAML and live entity contracts.` | `scripts/ha_verify.py` (via `HASS_URL` & `HASS_TOKEN`) |
| **`embedded-iot-qa-gate`** | `software-development` | `Verify firmware builds, binary budgets, protocol frames.` | `scripts/iot_verify.py` |
| **`multi-domain-qa-gate`** | `devops` | `Run mandatory domain QA gates with hard exit-code checks.` | `scripts/qa_runner.py` |

*(Works seamlessly alongside Hermes' built-in bundled skills: `requesting-code-review`, `simplify-code`, `systematic-debugging`, `test-driven-development`, `dogfood`, and `sdlc-review`.)*

---

## Automated Upstream Radar & CI Validation

- **Hardline Validator (`.github/workflows/validate-skills.yml`):** Every commit and PR is validated by `scripts/validate_hermes_skills.py` to enforce `description <= 60` chars, valid frontmatter, zero private IPs/paths, and clean Python compilation.
- **Weekly Upstream Radar (`.github/workflows/upstream-radar.yml`):** Checks `addyosmani/agent-skills` and `obra/superpowers` every Monday and opens an automated tracking issue whenever new upstream commits land.

## License

MIT License. Adapted in part from [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) (MIT).
