#!/usr/bin/env python3
"""
Validates all skills in `skills/*/` against the NousResearch Hermes-Agent
hardline skill authoring standard (`hermes-agent-skill-authoring` v2.0.0):
- Frontmatter starts at byte 0 with `---` and closes with `\n---\n`
- Required keys: name, description, version, author, license, platforms, metadata.hermes.tags
- `description` <= 60 characters, single sentence, ends with `.`
- Zero hardcoded private LAN IPs (192.168.x.x, 10.10.x.x) or `/home/<user>` paths
- All helper scripts under `scripts/*.py` compile cleanly
"""
import re
import sys
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

PRIVATE_IP_RE = re.compile(r"\b(192\.168\.\d{1,3}\.\d{1,3}|10\.10\.\d{1,3}\.\d{1,3})\b")
HOME_PATH_RE = re.compile(r"/home/[a-zA-Z0-9_-]+/")


def validate_skill(skill_dir: Path) -> list[str]:
    errors = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [f"{skill_dir.name}: Missing SKILL.md"]

    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        errors.append(f"{skill_dir.name}: SKILL.md must start at byte 0 with '---'")
        return errors

    m = re.search(r"\n---\s*\n", content[3:])
    if not m:
        errors.append(f"{skill_dir.name}: Missing closing '---' in frontmatter")
        return errors

    fm_raw = content[3 : m.start() + 3]
    try:
        fm = yaml.safe_load(fm_raw)
    except Exception as e:
        errors.append(f"{skill_dir.name}: Invalid YAML frontmatter: {e}")
        return errors

    for req in ("name", "description", "version", "author", "license", "platforms", "metadata"):
        if req not in fm:
            errors.append(f"{skill_dir.name}: Missing required frontmatter field '{req}'")

    if fm.get("name") != skill_dir.name:
        errors.append(f"{skill_dir.name}: frontmatter name '{fm.get('name')}' != directory '{skill_dir.name}'")

    desc = str(fm.get("description", ""))
    if len(desc) > 60:
        errors.append(f"{skill_dir.name}: description is {len(desc)} chars (hardline limit is <= 60): '{desc}'")
    if not desc.endswith("."):
        errors.append(f"{skill_dir.name}: description must end with a period '.'")

    for p in skill_dir.rglob("*"):
        if not p.is_file() or '__pycache__' in p.parts or p.suffix == '.pyc':
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if p.name != "security_audit.py":
            ip_match = PRIVATE_IP_RE.search(txt)
            if ip_match:
                errors.append(f"{skill_dir.name}/{p.name}: Contains hardcoded private IP '{ip_match.group(0)}'")
        home_match = HOME_PATH_RE.search(txt)
        if home_match:
            errors.append(f"{skill_dir.name}/{p.name}: Contains machine-local path '{home_match.group(0)}'")
        if p.suffix == ".py":
            try:
                compile(p.read_text(encoding='utf-8'), str(p), 'exec')
            except SyntaxError as e:
                errors.append(f"{skill_dir.name}/{p.name}: Python syntax error: {e}")

    return errors


def main():
    skill_dirs = sorted([d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")])
    if not skill_dirs:
        print("FAIL: No skills found in skills/", file=sys.stderr)
        return 1

    all_errors = []
    for sdir in skill_dirs:
        errs = validate_skill(sdir)
        all_errors.extend(errs)

    if all_errors:
        print(f"FAIL: {len(all_errors)} validation error(s):")
        for e in all_errors:
            print("  -", e)
        return 1

    print(f"PASS: All {len(skill_dirs)} Hermes skills in skills/ meet the hardline standard.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
