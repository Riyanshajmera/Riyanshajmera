"""
update_readme.py

Fetches live data from the GitHub REST API (public repo count, follower
count, and the most recently updated public repo) and writes it into
README.md between two marker comments. Meant to be run on a schedule via
GitHub Actions so the README updates itself.

Markers expected in README.md:
    <!--START_SECTION:live-stats-->
    ...content is replaced here...
    <!--END_SECTION:live-stats-->

Usage:
    python scripts/update_readme.py --username riyansh-ajmera --readme README.md

Environment:
    GITHUB_TOKEN  Optional. If set, used as a Bearer token to raise the
                  API rate limit (5000/hr vs 60/hr unauthenticated).
                  In GitHub Actions this is provided automatically as
                  secrets.GITHUB_TOKEN.
"""

import argparse
import datetime
import os
import re
import sys
import urllib.request
import json

API_BASE = "https://api.github.com"
START_MARKER = "<!--START_SECTION:live-stats-->"
END_MARKER = "<!--END_SECTION:live-stats-->"


def api_get(path: str, token: str | None):
    req = urllib.request.Request(f"{API_BASE}{path}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "profile-readme-bot")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_stats(username: str, token: str | None) -> dict:
    user = api_get(f"/users/{username}", token)
    repos = api_get(f"/users/{username}/repos?sort=updated&per_page=5", token)

    latest_repo = repos[0] if repos else None

    return {
        "public_repos": user.get("public_repos", 0),
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "latest_repo_name": latest_repo["name"] if latest_repo else None,
        "latest_repo_url": latest_repo["html_url"] if latest_repo else None,
        "latest_repo_desc": (latest_repo.get("description") or "").strip() if latest_repo else None,
    }


def render_section(stats: dict) -> str:
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"**Public repos:** {stats['public_repos']} &nbsp;|&nbsp; "
        f"**Followers:** {stats['followers']} &nbsp;|&nbsp; "
        f"**Following:** {stats['following']}",
        "",
    ]
    if stats["latest_repo_name"]:
        desc = f" — {stats['latest_repo_desc']}" if stats["latest_repo_desc"] else ""
        lines.append(f"🔧 Latest activity: [`{stats['latest_repo_name']}`]({stats['latest_repo_url']}){desc}")
        lines.append("")
    lines.append(f"<sub>Last updated {now}</sub>")
    return "\n".join(lines)


def update_readme(readme_path: str, section_text: str) -> bool:
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    if START_MARKER not in content or END_MARKER not in content:
        print(
            f"Markers not found in {readme_path}. "
            f"Add {START_MARKER} and {END_MARKER} where you want live stats to appear.",
            file=sys.stderr,
        )
        return False

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL
    )
    replacement = f"{START_MARKER}\n{section_text}\n{END_MARKER}"
    new_content = pattern.sub(replacement, content)

    if new_content == content:
        print("No changes needed.")
        return False

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated {readme_path}")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--readme", default="README.md")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    stats = fetch_stats(args.username, token)
    section = render_section(stats)
    update_readme(args.readme, section)


if __name__ == "__main__":
    main()
