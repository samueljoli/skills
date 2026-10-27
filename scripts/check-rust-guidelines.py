#!/usr/bin/env python3
"""Track upstream Rust guideline repositories and open assigned issues for updates."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

API_ROOT = "https://api.github.com"
STATE_PATH = Path(".github/rust-guidelines-state.json")

SOURCES = (
    {
        "key": "microsoft",
        "repo": "microsoft/rust-guidelines",
        "ref": "main",
        "name": "Microsoft Pragmatic Rust Guidelines",
        "checklist": "https://microsoft.github.io/rust-guidelines/guidelines/checklist/index.html",
    },
    {
        "key": "rust-api",
        "repo": "rust-lang/api-guidelines",
        # This repository uses master. Its published book is built from gh-pages.
        "ref": "master",
        "name": "Rust API Guidelines",
        "checklist": "https://rust-lang.github.io/api-guidelines/checklist.html",
    },
)


def github_request(method: str, path: str, payload: dict | None = None) -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is not set")

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "rust-guidelines-tracker",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    request = Request(API_ROOT + path, method=method, headers=headers, data=data)
    try:
        with urlopen(request, timeout=30) as response:
            raw = response.read()
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {method} {path} failed ({error.code}): {detail}") from error
    except URLError as error:
        raise RuntimeError(f"GitHub API {method} {path} failed: {error.reason}") from error

    if not raw:
        return {}
    return json.loads(raw)


def current_commit(source: dict) -> str:
    response = github_request(
        "GET",
        f"/repos/{source['repo']}/commits/{quote(source['ref'], safe='')}",
    )
    sha = response.get("sha")
    if not sha:
        raise RuntimeError(f"No commit SHA returned for {source['repo']}:{source['ref']}")
    return sha


def comparison(source: dict, base: str, head: str) -> dict:
    revision_range = quote(f"{base}...{head}", safe=".")
    return github_request("GET", f"/repos/{source['repo']}/compare/{revision_range}")


def existing_issue(title: str) -> dict | None:
    repository = os.environ.get("GITHUB_REPOSITORY")
    if not repository:
        raise RuntimeError("GITHUB_REPOSITORY is not set")

    query = urlencode({"q": f'repo:{repository} is:issue is:open in:title "{title}"'})
    response = github_request("GET", f"/search/issues?{query}")
    for issue in response.get("items", []):
        if issue.get("title") == title:
            return issue
    return None


def commit_line(commit: dict) -> str:
    metadata = commit.get("commit", {})
    message = metadata.get("message", "").splitlines()[0].strip()
    message = message.replace("\n", " ")
    if len(message) > 160:
        message = message[:157] + "..."
    date = metadata.get("author", {}).get("date", "unknown date")
    author = metadata.get("author", {}).get("name", "unknown author")
    sha = commit.get("sha", "")
    url = commit.get("html_url", "")
    return f"- [`{sha[:12]}`]({url}) — {message} ({author}, {date})"


def issue_body(source: dict, base: str, head: str, result: dict, commits: list[dict]) -> str:
    compare_url = result.get("html_url") or (
        f"https://github.com/{source['repo']}/compare/{base}...{head}"
    )
    lines = [
        "This issue was opened automatically by the monthly upstream tracker.",
        "",
        f"- Repository: [`{source['repo']}`](https://github.com/{source['repo']})",
        f"- Branch: `{source['ref']}`",
        f"- Previous tracked commit: [`{base[:12]}`](https://github.com/{source['repo']}/commit/{base})",
        f"- Current commit: [`{head[:12]}`](https://github.com/{source['repo']}/commit/{head})",
        f"- Comparison: [{result.get('status', 'unknown')}]({compare_url})",
        f"- Checklist: {source['checklist']}",
        "",
        "## Commits",
        "",
    ]
    if commits:
        lines.extend(commit_line(commit) for commit in commits)
    else:
        lines.append("The upstream branch changed, but GitHub returned no comparable commit list.")

    if result.get("ahead_by", 0) > len(commits):
        lines.extend(
            [
                "",
                f"GitHub reports {result['ahead_by']} commits ahead. The API returned only {len(commits)} commit entries.",
            ]
        )

    lines.extend(
        [
            "",
            "## Review checklist",
            "",
            "- [ ] Read the upstream changes.",
            "- [ ] Update the matching skill in `skills/rust/` if needed.",
            "- [ ] Add or update tests for changed workflow behavior.",
            "- [ ] Update the tracked baseline after review.",
        ]
    )
    return "\n".join(lines) + "\n"


def open_issue(source: dict, base: str, head: str, result: dict) -> None:
    title = f"Update {source['name']} ({base[:7]}..{head[:7]})"
    existing = existing_issue(title)
    if existing:
        print(f"Issue already exists: #{existing.get('number')} {title}")
        return

    assignee = os.environ.get("ISSUE_ASSIGNEE", "").strip()
    payload = {
        "title": title,
        "body": issue_body(source, base, head, result, result.get("commits", [])),
    }
    if assignee:
        payload["assignees"] = [assignee]

    issue = github_request("POST", "/repos/%s/issues" % os.environ["GITHUB_REPOSITORY"], payload)
    print(f"Opened issue #{issue.get('number')}: {title}")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_state() -> dict:
    if not STATE_PATH.exists():
        return {"checked_at": None, "sources": {}}
    with STATE_PATH.open(encoding="utf-8") as stream:
        return json.load(stream)


def write_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = STATE_PATH.with_suffix(".json.tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(state, stream, indent=2)
        stream.write("\n")
    temporary.replace(STATE_PATH)


def write_summary(lines: list[str]) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    with open(summary_path, "a", encoding="utf-8") as stream:
        stream.write("\n".join(lines) + "\n")


def main() -> int:
    state = read_state()
    previous_sources = state.get("sources", {})
    next_sources = {}
    summary = ["## Upstream Rust guideline check", ""]
    initialized = not previous_sources

    for source in SOURCES:
        head = current_commit(source)
        previous = previous_sources.get(source["key"], {})
        base = previous.get("sha")
        same_source = previous.get("repo") == source["repo"] and previous.get("ref") == source["ref"]

        if not base or not same_source:
            print(f"Initializing {source['repo']} at {head[:12]}")
            summary.append(f"- Initialized `{source['repo']}` at `{head[:12]}`")
        elif base == head:
            print(f"No changes: {source['repo']} at {head[:12]}")
            summary.append(f"- No changes: `{source['repo']}` at `{head[:12]}`")
        else:
            result = comparison(source, base, head)
            ahead_by = result.get("ahead_by", 0)
            commits = result.get("commits", [])
            if ahead_by > 0 or commits:
                open_issue(source, base, head, result)
                summary.append(
                    f"- Changes found: `{source['repo']}` `{base[:12]}` to `{head[:12]}` ({ahead_by} commits ahead)"
                )
            else:
                print(f"No new commits: {source['repo']} moved from {base[:12]} to {head[:12]}")
                summary.append(f"- No new commits: `{source['repo']}` moved to `{head[:12]}`")

        next_sources[source["key"]] = {
            "repo": source["repo"],
            "ref": source["ref"],
            "sha": head,
        }

    state = {"checked_at": utc_now(), "sources": next_sources}
    write_state(state)
    summary.append("")
    if initialized:
        summary.append("The initial baseline was recorded. No issue was opened for existing commits.")
    write_summary(summary)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
