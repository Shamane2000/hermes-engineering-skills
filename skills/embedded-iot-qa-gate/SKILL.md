---
name: embedded-iot-qa-gate
description: "Verify firmware builds, binary budgets, protocol frames."
version: 1.0.0
author: Frank (Shamane2000), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [embedded, iot, firmware, platformio, protocol, reverse-engineering, qa]
    related_skills: [systematic-debugging, test-driven-development]
---

# Embedded & IoT QA Gate Skill

Deterministic verification for embedded firmware (ESP32, STM32, AVR, ARM/Coolsand), binary reverse-engineering harnesses, and binary/serial/TCP protocol parsers. Ensures reproducible cross-builds, flash/RAM budget compliance, and byte-exact protocol frame validation.

## When to Use

- Building or modifying embedded C/C++/Rust firmware (`platformio.ini`, `Makefile`, `CMakeLists.txt`)
- Writing or modifying binary protocol parsers, CRC/checksum calculators, or reverse-engineering test harnesses
- Don't use for: pure web frontend or cloud-only CRUD tasks

## How to Run

Run `scripts/iot_verify.py` via `terminal`:

```
terminal(command="python3 ~/.hermes/skills/software-development/embedded-iot-qa-gate/scripts/iot_verify.py --project .", timeout=180)
```

## Procedure

1. **Verify target environment & toolchain:**
   - Check `platformio.ini`, `Makefile`, or project docs via `read_file` to identify the target board, endianness, and build host. Never run heavy cross-compilation on a low-RAM coordinator node if a dedicated build host is configured.
   - *Completion criterion:* Toolchain and project config located.
2. **Verify protocol parser & framing with deterministic test vectors:**
   - Every protocol command/response parser must have unit test vectors covering: valid frame, truncated frame, invalid checksum/CRC, and boundary payload lengths.
   - *Completion criterion:* Test runner exits `0` against byte-level test vectors.
3. **Run build & binary budget gate (`scripts/iot_verify.py`):**
   - Execute `scripts/iot_verify.py` via `terminal` to verify clean compilation and check binary size / test suite exit code.
   - *Completion criterion:* `iot_verify.py` exits with code `0` (`PASS`).

## Pitfalls

- **Blocking loops in firmware:** Never introduce unbounded `while(true)` wait loops without watchdog feed or timeout on hardware targets.
- **Unaligned memory / endianness assumptions:** Always use explicit byte-order unpacking (`struct.unpack('<H', ...)` or `'>H'`) in protocol code.

## Verification

Complete when `scripts/iot_verify.py` exits `0` (`PASS`).
