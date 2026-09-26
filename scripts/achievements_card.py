#!/usr/bin/env python3
"""Create a dependency-free achievements card for a GitHub profile README.

Reads public profile statistics from the GitHub REST API. No third-party
service and no third-party packages: the standard library only.

Star and fork totals cover owned, non-fork repositories, since stars on a
fork are not earned by this account. The repository count is GitHub's own
public_repos figure so it matches what the profile page reports.
"""

import argparse
import datetime as dt
import html
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

OUT = Path(__file__).resolve().parents[1] / "assets" / "achievements-card.svg"
USER = "felixren7"
API = "https://api.github.com"
LEFT, WIDTH = 32, 900
try:
    SINGAPORE = ZoneInfo("Asia/Singapore")
except KeyError:  # no system tzdata; Singapore has no DST, so a fixed offset is exact
    SINGAPORE = dt.timezone(dt.timedelta(hours=8), "SGT")


def get_json(path, token):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USER}-profile-card",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(API + path, headers=headers), timeout=20) as response:
        return json.load(response)


def stats(token):
    user = get_json(f"/users/{USER}", token)
    repos, page = [], 1
    while page <= 5:  # 5 pages is 500 owned repos; ample headroom
        batch = get_json(f"/users/{USER}/repos?per_page=100&type=owner&page={page}", token)
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    owned = [repo for repo in repos if not repo["fork"]]
    return (
        ("Stars", sum(repo["stargazers_count"] for repo in owned)),
        ("Forks", sum(repo["forks_count"] for repo in owned)),
        ("Followers", user["followers"]),
        ("Repositories", user["public_repos"]),
    )


def render(values, now):
    step = (WIDTH - 2 * LEFT) / len(values)
    updated = now.strftime("%d %b %Y, %H:%M SGT")
    def esc(value):
        return html.escape(str(value), quote=True)
    cells = []
    for index, (label, value) in enumerate(values):
        x = LEFT + index * step
        cells.append(f'  <text x="{x:.0f}" y="96" fill="#ffffff" font-family="Arial, sans-serif" font-size="32" font-weight="bold">{esc(value)}</text>')
        cells.append(f'  <text x="{x:.0f}" y="121" fill="#a5b4fc" font-family="Arial, sans-serif" font-size="14" font-weight="bold">{esc(label.upper())}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="180" viewBox="0 0 900 180" role="img" aria-label="GitHub achievements: {esc(', '.join(f'{label} {value}' for label, value in values))}">
  <defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#0f172a"/><stop offset="1" stop-color="#312e81"/></linearGradient></defs>
  <rect width="900" height="180" rx="20" fill="url(#bg)"/>
  <text x="32" y="36" fill="#a5b4fc" font-family="Arial, sans-serif" font-size="16" font-weight="bold">ACHIEVEMENTS</text>
{chr(10).join(cells)}
  <text x="32" y="165" fill="#cbd5e1" font-family="Arial, sans-serif" font-size="12">Updated {esc(updated)} · Public repository statistics · GitHub REST API</text>
</svg>
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="Generate a preview without an API call")
    args = parser.parse_args()
    now = dt.datetime.now(SINGAPORE)
    if args.offline:
        values = (("Stars", 0), ("Forks", 0), ("Followers", 0), ("Repositories", 0))
    else:
        try:
            values = stats(os.environ.get("GITHUB_TOKEN"))
        except (OSError, ValueError, KeyError, TypeError, TimeoutError) as exc:
            if OUT.exists():
                print(f"Stats unavailable ({exc}); keeping the last generated card")
                return
            values = (("Stars", "—"), ("Forks", "—"), ("Followers", "—"), ("Repositories", "—"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(values, now), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
