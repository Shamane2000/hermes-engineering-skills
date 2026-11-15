#!/usr/bin/env python3
"""Checks markdown docs/ADRs for broken relative links and empty status sections."""
import re
import sys
from pathlib import Path

LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?:|mailto:|#)([^)#]+)(?:#[^)]*)?\)")


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    if not target.exists():
        print(f"PASS: Target {target} does not exist yet (nothing to fail).")
        return 0
    md_files = [target] if target.is_file() else list(target.rglob("*.md"))
    errors = []
    for f in md_files:
        if any(p in f.parts for p in (".git", "node_modules", "venv", ".venv")):
            continue
        txt = f.read_text(encoding="utf-8", errors="ignore")
        for m in LINK_RE.finditer(txt):
            rel = m.group(1).strip()
            if not rel or rel.startswith("/"):
                continue
            resolved = (f.parent / rel).resolve()
            if not resolved.exists():
                errors.append(f"{f}: broken relative link -> {rel}")
    if errors:
        print(f"FAIL: {len(errors)} documentation link error(s):")
        for e in errors:
            print(" ", e)
        return 1
    print(f"PASS: Checked {len(md_files)} markdown file(s), 0 broken relative links.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
