#!/usr/bin/env python3
"""Validates that a Markdown specification contains all mandatory verifiable sections."""
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    ("Objective", re.compile(r"^##+\s+.*Objective", re.I | re.M)),
    ("Invariants & Constraints", re.compile(r"^##+\s+.*(Invariant|Constraint)", re.I | re.M)),
    ("Acceptance Criteria & Verification", re.compile(r"^##+\s+.*(Acceptance|Verification)", re.I | re.M)),
    ("Out of Scope", re.compile(r"^##+\s+.*Out of Scope", re.I | re.M)),
]


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_spec.py <spec.md>", file=sys.stderr)
        return 2
    p = Path(sys.argv[1])
    if not p.exists():
        print(f"FAIL: Spec file not found: {p}", file=sys.stderr)
        return 1
    text = p.read_text(encoding="utf-8", errors="replace")
    missing = [name for name, rx in REQUIRED_SECTIONS if not rx.search(text)]
    has_code_or_cmd = bool(re.search(r"`[^`]+`|```", text))
    if missing:
        print(f"FAIL: Spec {p.name} is missing mandatory section(s): {', '.join(missing)}")
        return 1
    if not has_code_or_cmd:
        print(f"FAIL: Spec {p.name} contains no runnable verification commands in backticks.")
        return 1
    print(f"PASS: Spec {p.name} contains all 4 mandatory sections and runnable commands.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
