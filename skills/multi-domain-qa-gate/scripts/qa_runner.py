#!/usr/bin/env python3
"""Universal Multi-Domain QA Gate Runner for Hermes Agent."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
import yaml

FORBIDDEN_TREE_DIRS = {"venv", ".venv", "node_modules", "__pycache__"}


def check_git_pollution(ws: Path) -> list:
    errors = []
    if (ws / ".git").exists():
        res = subprocess.run(["git", "-C", str(ws), "status", "--porcelain"], capture_output=True, text=True)
        for line in res.stdout.splitlines():
            path_str = line[3:].strip()
            parts = Path(path_str).parts
            if any(p in FORBIDDEN_TREE_DIRS for p in parts):
                errors.append(f"Git pollution: '{path_str}' (virtual environment or cache must be in .gitignore)")
    return errors


def check_syntax(ws: Path) -> tuple[list, int]:
    errors = []
    checked = 0
    for p in ws.rglob("*"):
        if not p.is_file() or any(part in FORBIDDEN_TREE_DIRS or part == ".git" for part in p.parts):
            continue
        if p.suffix == ".py":
            checked += 1
            try:
                compile(p.read_text(encoding='utf-8'), str(p), 'exec')
            except SyntaxError as e:
                errors.append(f"Python syntax error in {p.relative_to(ws)}: {e}")
        elif p.suffix == ".json":
            checked += 1
            try:
                json.loads(p.read_text(encoding="utf-8"))
            except Exception as e:
                errors.append(f"JSON syntax error in {p.relative_to(ws)}: {e}")
        elif p.suffix == ".sh":
            checked += 1
            res = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
            if res.returncode != 0:
                errors.append(f"Bash syntax error in {p.relative_to(ws)}: {res.stderr.strip()}")
    return errors, checked


def run_tests_if_present(ws: Path) -> list:
    errors = []
    py_tests = [
        p for p in list(ws.rglob("test_*.py")) + list(ws.rglob("*_test.py"))
        if not any(part in FORBIDDEN_TREE_DIRS or part == ".git" for part in p.parts)
    ]
    if py_tests:
        res = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=str(ws), capture_output=True, text=True)
        if res.returncode != 0:
            errors.append(f"pytest failed (exit {res.returncode}):\n{(res.stdout + res.stderr)[-1000:]}")
    return errors


def main():
    ap = argparse.ArgumentParser(description="Multi-Domain QA Gate Runner")
    ap.add_argument("--workspace", default=".", help="Target workspace directory")
    ap.add_argument("--skip-tests", action="store_true", help="Run syntax and hygiene checks only")
    args = ap.parse_args()

    ws = Path(args.workspace).resolve()
    errors = []
    errors.extend(check_git_pollution(ws))
    syn_errors, checked_count = check_syntax(ws)
    errors.extend(syn_errors)
    if not args.skip_tests:
        errors.extend(run_tests_if_present(ws))

    if errors:
        print(f"FAIL: Multi-Domain QA Gate detected {len(errors)} issue(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"PASS: Multi-Domain QA Gate verified {checked_count} file(s) in '{ws.name}' with 0 errors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
