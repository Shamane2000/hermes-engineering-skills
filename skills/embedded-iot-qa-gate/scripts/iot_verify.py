#!/usr/bin/env python3
"""Deterministic Embedded/IoT project build & protocol test verifier."""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def find_project_python(ws: Path) -> str:
    candidates = [
        ws / ".venv" / "bin" / "python",
        ws / "venv" / "bin" / "python",
        ws / "backend" / ".venv" / "bin" / "python",
        ws / "backend" / "venv" / "bin" / "python",
        ws.parent / ".venv" / "bin" / "python",
        ws.parent / "venv" / "bin" / "python",
    ]
    srv_dev = Path("/srv/dev")
    if srv_dev.is_dir():
        for name in {ws.name.lower(), ws.parent.name.lower()}:
            candidates.extend([
                srv_dev / name / "backend" / ".venv" / "bin" / "python",
                srv_dev / name / ".venv" / "bin" / "python",
            ])
    for cand in candidates:
        if cand.is_file() and os.access(cand, os.X_OK):
            res = subprocess.run([str(cand), "-m", "pytest", "--version"], capture_output=True, text=True)
            if res.returncode == 0:
                return str(cand)
    return sys.executable


def run_cmd(cmd, cwd: Path, env=None):
    print(f"[iot_verify] Running: {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True, text=True)
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

    for mk_dir in [proj, proj / "sim"]:
        if (mk_dir / "Makefile").exists() and shutil.which("make"):
            rc = run_cmd(["make"], mk_dir)
            if rc != 0:
                print(f"FAIL: Makefile build failed in {mk_dir}.")
                return 1
            checks_run += 1

    has_root_tests = bool(list(proj.glob("tests/test_*.py")) or list(proj.glob("test_*.py")))
    has_backend_tests = bool(list(proj.glob("backend/tests/test_*.py")))
    if has_root_tests or has_backend_tests:
        py_bin = find_project_python(proj)
        test_cwd = proj / "backend" if has_backend_tests and not has_root_tests else proj
        cmd = [py_bin, "-m", "pytest", "-q", "-o", "addopts="]
        env = os.environ.copy()
        shm = Path("/dev/shm")
        if shm.is_dir() and os.access(shm, os.W_OK):
            cmd.extend(["--basetemp", str(shm / f"pytest-iot-{os.getpid()}")])
            env["TMPDIR"] = str(shm)
            env["SQLITE_TMPDIR"] = str(shm)
            env.setdefault("DATABASE_URL", f"sqlite:///{shm}/pytest-qa-{os.getpid()}.db")
        rc = run_cmd(cmd, test_cwd, env=env)
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
