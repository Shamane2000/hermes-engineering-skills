---
name: performance-and-observability
description: "Profile bottlenecks and add structured logs and metrics."
version: 1.0.0
author: Frank (Shamane2000), Hermes Agent (adapted from Addy Osmani agent-skills)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [performance, profiling, observability, logging, metrics, optimization]
    related_skills: [systematic-debugging, requesting-code-review]
---

# Performance and Observability Skill

Measure-first performance optimization and production observability. Prevents premature micro-optimization by requiring a baseline measurement before changes and structured telemetry for runtime verification.

## When to Use

- Investigating slow endpoints, high CPU/RAM usage, N+1 database queries, or memory leaks
- Adding logging, health checks, or metrics to a service or background job
- Don't use for: cosmetic refactoring without a measurable performance or observability goal

## Procedure

1. **Measure baseline before touching code:**
   - Reproduce and quantify the bottleneck using `terminal` (e.g., `pytest --durations=10`, `python3 -m cProfile`, `time`, SQL query count, or memory rss).
   - *Completion criterion:* Exact baseline metric (ms, MB, or query count) recorded before any edit.
2. **Eliminate high-leverage bottlenecks first:**
   - Check for N+1 queries/requests inside loops, unindexed lookups, synchronous blocking I/O in async loops, and unbounded in-memory list growth (`search_files` + `read_file`).
   - Apply targeted fix via `patch`.
   - *Completion criterion:* Re-running the exact baseline command via `terminal` shows a measurable improvement without breaking tests.
3. **Enforce structured observability rules:**
   - Log actionable context (operation, entity ID, duration_ms, error type) rather than bare strings.
   - **Never log secrets, tokens, or raw passwords.**
   - **Guard metric cardinality:** Never place unbounded IDs (`user_id`, `request_id`, raw URLs) into metric labels; keep high-cardinality fields in logs/traces.
   - *Completion criterion:* Health/log output verified via `terminal` and existing test suite passes (`Exit Code 0`).

## Pitfalls

- **Optimizing without a baseline:** If you cannot measure the before/after difference, revert the complexity.
- **Running heavy benchmarks on resource-constrained coordinator nodes:** Run heavy profiling on the designated build/dev host when available.

## Verification

Compare recorded `Before` vs `After` measurements from `terminal` output and verify all tests pass (`Exit Code 0`).
