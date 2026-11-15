#!/usr/bin/env python3
"""Deterministic Embedded/IoT project build & protocol test verifier."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd, cwd: Path):
    print(f"[iot_verify] Running: {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if res.stdout:
        print(res.stdout[-1500:])
    if res.stderr:
        print(res.stderr[-1500:], file=sys.stderr)
    return res.returncode


def main():
    ap = argparse.ArgumentParser(description="Verify Embedded/IoT builds and protocol tests")
    ap.add_argument("--project", default=".", help="Project directory")
    ap.add_argument("--max-binary-kb", type=int, default=0, help="Optional maximum firmware binary size in KB")
    args = ap.parse_args()

    proj = Path(args.project).resolve()
    checks_run = 0

    if (proj / "platformio.ini").exists() and shutil.which("pio"):
        rc = run_cmd(["pio", "run"], proj)
        if rc != 0:
            print("FAIL: PlatformIO build failed.")
            return 1
        checks_run += 1

    if list(proj.glob("tests/test_*.py")) or list(proj.glob("test_*.py")):
        rc = run_cmd([sys.executable, "-m", "pytest", "-q"], proj)
        if rc != 0:
            print("FAIL: Protocol/unit test suite failed.")
            return 1
        checks_run += 1

    if args.max_binary_kb > 0:
        for bin_file in list(proj.rglob("*.bin")) + list(proj.rglob("*.elf")):
            if ".pio" in bin_file.parts or "build" in bin_file.parts:
                size_kb = bin_file.stat().st_size / 1024.0
                if size_kb > args.max_binary_kb:
                    print(f"FAIL: Binary {bin_file.name} ({size_kb:.1f} KB) exceeds limit ({args.max_binary_kb} KB).")
                    return 1
                checks_run += 1

    print(f"PASS: Embedded/IoT verification succeeded ({checks_run} active check(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
