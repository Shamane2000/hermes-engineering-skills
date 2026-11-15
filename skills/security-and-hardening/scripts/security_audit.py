#!/usr/bin/env python3
"""Deterministic static security & hygiene scanner for Hermes Agent repositories."""
import argparse
import re
import subprocess
import sys
from pathlib import Path

RULES = [
    ("SECRET_ASSIGNMENT", re.compile(r"(?i)(api[_-]?key|secret|password|passwd|access[_-]?token|auth[_-]?token)\s*[:=]\s*['\"][A-Za-z0-9_\-/.+=]{8,}['\"]"), "Potential hardcoded secret/token"),
    ("PRIVATE_KEY", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA |PRIVATE )?KEY-----"), "Embedded private key"),
    ("SHELL_INJECTION", re.compile(r"(os\.system\s*\(|subprocess\.(Popen|run|call|check_output)\([^)]*shell\s*=\s*True)"), "Shell execution with shell=True or os.system"),
    ("UNSAFE_DESERIALIZATION", re.compile(r"(pickle\.loads?\s*\(|yaml\.load\s*\([^)]*(?!Loader=yaml\.SafeLoader))"), "Unsafe deserialization (pickle or unsafe yaml.load)"),
    ("UNSAFE_EVAL", re.compile(r"\b(eval|exec)\s*\("), "Dynamic code execution via eval/exec"),
]

SKIP_DIRS = {".git", "venv", ".venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}
CODE_EXTS = {".py", ".js", ".ts", ".tsx", ".sh", ".yaml", ".yml", ".json", ".toml", ".env"}


def scan_lines(lines_with_meta):
    findings = []
    for filepath, lineno, line in lines_with_meta:
        if "# nosec" in line or "example" in line.lower() or "placeholder" in line.lower():
            continue
        for rule_id, pattern, msg in RULES:
            if rule_id == "UNSAFE_DESERIALIZATION" and ("SafeLoader" in line or "SafeHALoader" in line):
                continue
            if pattern.search(line):
                findings.append((filepath, lineno, rule_id, msg, line.strip()[:120]))
    return findings


def collect_diff_lines(repo: Path):
    res = subprocess.run(["git", "-C", str(repo), "diff", "HEAD"], capture_output=True, text=True)
    if not res.stdout.strip():
        res = subprocess.run(["git", "-C", str(repo), "diff", "--cached"], capture_output=True, text=True)
    items = []
    cur_file = None
    lineno = 0
    for raw in res.stdout.splitlines():
        if raw.startswith("+++ b/"):
            cur_file = raw[6:]
        elif raw.startswith("@@ "):
            m = re.search(r"\+(\d+)", raw)
            lineno = int(m.group(1)) - 1 if m else 0
        elif raw.startswith("+") and not raw.startswith("+++"):
            lineno += 1
            if cur_file:
                items.append((cur_file, lineno, raw[1:]))
        elif not raw.startswith("-"):
            lineno += 1
    return items


def collect_repo_lines(repo: Path):
    items = []
    for p in repo.rglob("*"):
        if not p.is_file() or any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix.lower() not in CODE_EXTS:
            continue
        if p.name == "security_audit.py":
            continue
        try:
            for idx, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                items.append((p.relative_to(repo).as_posix(), idx, line))
        except Exception:
            pass
    return items


def main():
    ap = argparse.ArgumentParser(description="Hermes deterministic security scanner")
    ap.add_argument("--repo", default=".", help="Repository path")
    ap.add_argument("--diff-only", action="store_true", help="Scan only git diff")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    lines = collect_diff_lines(repo) if args.diff_only else collect_repo_lines(repo)
    findings = scan_lines(lines)

    if findings:
        print(f"FAIL: {len(findings)} security finding(s) detected:")
        for fpath, lno, rid, msg, snippet in findings:
            print(f"  [{rid}] {fpath}:{lno} — {msg}\n    > {snippet}")
        return 1

    print(f"PASS: 0 security findings across {len(lines)} scanned line(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
