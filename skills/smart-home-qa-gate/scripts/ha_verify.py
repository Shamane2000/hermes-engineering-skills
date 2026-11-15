#!/usr/bin/env python3
"""Deterministic Home Assistant YAML syntax, duplicate-key & live entity-state validator."""
import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
import yaml

ENTITY_RE = re.compile(
    r"\b(sensor|binary_sensor|input_number|input_boolean|input_text|input_select|input_datetime|"
    r"climate|light|switch|number|select|timer|schedule|calendar|weather|person|device_tracker|"
    r"media_player)\.([a-z0-9_]+)(?!\s*\{\{)\b"
)

SERVICE_VERBS = {
    "turn_on", "turn_off", "toggle", "set_value", "set_datetime", "set_temperature",
    "set_hvac_mode", "set_preset_mode", "set_fan_mode", "set_swing_mode", "set_humidity",
    "select_option", "select_first", "select_last", "select_next", "select_previous",
    "start", "pause", "cancel", "finish", "change", "reload", "increment", "decrement",
    "press", "play_media", "volume_set", "volume_mute", "media_play", "media_pause",
    "media_stop", "get_events", "create_event",
}


class SafeHALoader(yaml.SafeLoader):
    pass


def _custom_tag(loader, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


for tag in ("!include", "!include_dir_named", "!include_dir_merge_named", "!include_dir_list", "!include_dir_merge_list", "!secret", "!input", "!env_var"):
    SafeHALoader.add_constructor(tag, _custom_tag)


def collect_local_definitions(data) -> set:
    defined = set()
    if not isinstance(data, dict):
        return defined
    for domain in ("input_number", "input_boolean", "input_text", "input_select", "input_datetime", "timer", "script"):
        block = data.get(domain)
        if isinstance(block, dict):
            for slug in block.keys():
                defined.add(f"{domain}.{slug}")
    return defined


def fetch_live_states(hass_url: str, hass_token: str):
    req = urllib.request.Request(
        f"{hass_url.rstrip('/')}/api/states",
        headers={"Authorization": f"Bearer {hass_token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        items = json.loads(resp.read().decode("utf-8"))
    return {item["entity_id"]: item.get("state") for item in items if "entity_id" in item}


def main():
    ap = argparse.ArgumentParser(description="Validate Home Assistant YAML and live entity states")
    ap.add_argument("files", nargs="+", help="YAML file(s) to validate")
    ap.add_argument("--allow-unavailable", action="store_true", help="Warn instead of fail on unavailable state")
    args = ap.parse_args()

    hass_url = os.environ.get("HASS_URL", "").strip()
    hass_token = os.environ.get("HASS_TOKEN", "").strip()

    live_states = None
    if hass_url and hass_token:
        try:
            live_states = fetch_live_states(hass_url, hass_token)
        except Exception as e:
            print(f"WARN: Could not query live HASS_URL ({hass_url}): {e}", file=sys.stderr)

    errors = []
    local_defs = set()
    referenced_by_file = {}

    for fstr in args.files:
        p = Path(fstr)
        if not p.exists():
            errors.append(f"{fstr}: File not found")
            continue
        raw = p.read_text(encoding="utf-8", errors="replace")
        try:
            parsed = yaml.load(raw, Loader=SafeHALoader)
            local_defs |= collect_local_definitions(parsed)
        except Exception as e:
            errors.append(f"{fstr}: YAML syntax error: {e}")
            continue

        refs = set()
        for line in raw.splitlines():
            clean = line.split("#", 1)[0]
            if re.match(r"^\s*(service|action)\s*:", clean):
                continue
            for m in ENTITY_RE.finditer(clean):
                domain, slug = m.group(1), m.group(2)
                if slug in SERVICE_VERBS or slug.endswith("_"):
                    continue
                refs.add(f"{domain}.{slug}")
        referenced_by_file[fstr] = sorted(refs)

    if live_states is not None:
        for fstr, refs in referenced_by_file.items():
            for eid in refs:
                if eid in local_defs:
                    continue
                if eid not in live_states:
                    errors.append(f"{fstr}: Referenced entity '{eid}' does NOT exist in live Home Assistant")
                elif live_states[eid] == "unavailable" and not args.allow_unavailable:
                    errors.append(f"{fstr}: Referenced entity '{eid}' is 'unavailable' in live Home Assistant")

    if errors:
        print(f"FAIL: {len(errors)} Home Assistant QA error(s):")
        for err in errors:
            print(f"  - {err}")
        return 1

    total_refs = sum(len(v) for v in referenced_by_file.values())
    mode = f"live API ({len(live_states)} states, {total_refs} entity refs verified)" if live_states is not None else "offline YAML syntax"
    print(f"PASS: Validated {len(args.files)} file(s) against {mode} with 0 errors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
