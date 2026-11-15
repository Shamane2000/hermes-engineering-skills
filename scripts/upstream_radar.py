#!/usr/bin/env python3
"""Checks tracked upstream skill repositories for recent commits and opens a tracking issue."""
import json
import os
import subprocess
import urllib.request
from datetime import datetime, timedelta, timezone


def main():
    since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    upstreams = ["addyosmani/agent-skills", "obra/superpowers"]
    updates = []
    token = os.environ.get("GH_TOKEN", "")

    for repo in upstreams:
        url = f"https://api.github.com/repos/{repo}/commits?since={since}&per_page=10"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "hermes-engineering-skills-radar",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                commits = json.loads(resp.read().decode("utf-8"))
            if commits:
                lines = [f"### `{repo}` ({len(commits)} new commit(s) in the last 7 days)"]
                for c in commits:
                    sha = c["sha"][:7]
                    msg = c["commit"]["message"].splitlines()[0]
                    html_url = c["html_url"]
                    lines.append(f"- [`{sha}`]({html_url}): {msg}")
                updates.append("\n".join(lines))
        except Exception as e:
            print(f"Warn: failed to check {repo}: {e}")

    if updates:
        body = (
            "## Upstream Engineering Skills Update Radar\n\n"
            "New commits were detected in tracked upstream repositories. "
            "Review whether any new patterns or checks should be ported to Hermes-native format "
            "(following `hermes-agent-skill-authoring` hardline rules & deterministic `scripts/` gates):\n\n"
            + "\n\n".join(updates)
        )
        subprocess.run(
            [
                "gh",
                "issue",
                "create",
                "--title",
                f"[Upstream Radar] New upstream skill updates ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})",
                "--body",
                body,
            ],
            check=False,
        )
    else:
        print("No upstream commits in the last 7 days.")


if __name__ == "__main__":
    main()
