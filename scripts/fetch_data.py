#!/usr/bin/env python3
"""
Fetch public GitHub profile data via the REST API.

Outputs a normalized JSON file to data/github_data.json.

Requires GITHUB_TOKEN env var (or falls back to unauthenticated requests).
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error

API_BASE = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github.v3+json", "User-Agent": "profile-dashboard-builder"}


def api_get(path: str, token: str | None = None) -> dict | list:
    """Make a GitHub API GET request with optional auth and rate-limit backoff."""
    headers = dict(HEADERS)
    if token:
        headers["Authorization"] = f"token {token}"

    url = f"{API_BASE}{path}"
    req = urllib.request.Request(url, headers=headers)

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                remaining = resp.headers.get("X-RateLimit-Remaining", "?")
                print(f"  GET {path}  [rate-limit remaining: {remaining}]")
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 403 and "rate limit" in (e.read().decode() or "").lower():
                reset = int(e.headers.get("X-RateLimit-Reset", time.time() + 60))
                wait = max(reset - int(time.time()), 5) + 2
                print(f"  Rate limited. Waiting {wait}s before retry {attempt + 1}/3...")
                time.sleep(wait)
            elif e.code == 404:
                print(f"  404 Not found: {path}")
                return None
            else:
                print(f"  HTTP {e.code} on {path}: {e.reason}")
                return None
        except Exception as e:
            print(f"  Error fetching {path}: {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                return None
    return None


def fetch_user(username: str, token: str | None) -> dict:
    """Fetch core user profile data."""
    print(f"\n[*] Fetching user profile for {username}...")
    data = api_get(f"/users/{username}", token)
    if not data or not isinstance(data, dict):
        print("  WARNING: Could not fetch user profile. Using defaults.")
        return {"login": username, "public_repos": 0, "followers": 0, "following": 0}

    return {
        "login": data.get("login", username),
        "name": data.get("name"),
        "avatar_url": data.get("avatar_url", ""),
        "bio": data.get("bio"),
        "blog": data.get("blog", ""),
        "location": data.get("location"),
        "public_repos": data.get("public_repos", 0),
        "followers": data.get("followers", 0),
        "following": data.get("following", 0),
        "created_at": data.get("created_at", ""),
    }


def fetch_repos(username: str, token: str | None) -> list[dict]:
    """Fetch all public repos (paginated, 100 per page)."""
    print(f"\n[*] Fetching repositories for {username}...")
    all_repos = []
    page = 1

    while True:
        data = api_get(f"/users/{username}/repos?type=owner&sort=updated&per_page=100&page={page}", token)
        if not data or not isinstance(data, list) or len(data) == 0:
            break
        all_repos.extend(data)
        if len(data) < 100:
            break
        page += 1
        time.sleep(0.5)  # polite delay between pages

    print(f"  Found {len(all_repos)} repositories")
    return all_repos


def compute_repo_stats(repos: list[dict]) -> dict:
    """Derive statistics from the repository list."""
    stars_total = 0
    forks_total = 0
    languages: dict[str, int] = {}
    topics: list[str] = []
    repo_details = []

    for r in repos:
        # Skip forks for language/star stats to avoid skew
        is_fork = r.get("fork", False)

        stars_total += r.get("stargazers_count", 0)
        forks_total += r.get("forks_count", 0)

        lang = r.get("language")
        if lang and not is_fork:
            # Weight by repo size as a rough proxy for code volume
            size = max(r.get("size", 1), 1)
            languages[lang] = languages.get(lang, 0) + size

        if not is_fork:
            repo_topics = r.get("topics", []) or []
            topics.extend(t for t in repo_topics if t not in topics)

        repo_details.append({
            "name": r.get("name", ""),
            "full_name": r.get("full_name", ""),
            "description": r.get("description", "") or "",
            "html_url": r.get("html_url", ""),
            "homepage": r.get("homepage", "") or "",
            "language": lang,
            "stargazers_count": r.get("stargazers_count", 0),
            "forks_count": r.get("forks_count", 0),
            "fork": is_fork,
            "topics": r.get("topics", []) or [],
            "updated_at": r.get("updated_at", ""),
            "created_at": r.get("created_at", ""),
        })

    # Sort languages by usage descending
    sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
    total_lang_size = sum(v for _, v in sorted_langs)
    lang_percentages = []
    for name, size in sorted_langs[:8]:
        pct = round((size / total_lang_size * 100), 1) if total_lang_size > 0 else 0
        lang_percentages.append({"name": name, "percentage": pct, "size": size})

    # Top repos by stars (non-fork)
    non_fork_repos = [r for r in repo_details if not r["fork"]]
    top_repos = sorted(non_fork_repos, key=lambda x: x["stargazers_count"], reverse=True)[:6]

    return {
        "total_stars": stars_total,
        "total_forks": forks_total,
        "languages": lang_percentages,
        "topics": topics[:20],
        "top_repos": top_repos,
        "total_non_fork": len(non_fork_repos),
    }


def fetch_activity(username: str, token: str | None) -> list[dict]:
    """Fetch recent activity (events) for the past ~12 weeks."""
    print(f"\n[*] Fetching recent activity for {username}...")
    data = api_get(f"/users/{username}/events/public?per_page=100", token)
    if not data or not isinstance(data, list):
        return []

    # Group events by week
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    weeks: list[dict] = []
    for i in range(12):
        week_start = now - timedelta(weeks=11 - i)
        week_end = week_start + timedelta(days=7)
        weeks.append({
            "label": week_start.strftime("%b %d"),
            "start": week_start.isoformat() + "Z",
            "end": week_end.isoformat() + "Z",
            "count": 0,
        })

    for event in data:
        event_date = event.get("created_at", "")
        if not event_date:
            continue
        try:
            event_dt = datetime.fromisoformat(event_date.replace("Z", "+00:00")).replace(tzinfo=None)
            for week in weeks:
                ws = datetime.fromisoformat(week["start"].replace("Z", "+00:00")).replace(tzinfo=None)
                we = datetime.fromisoformat(week["end"].replace("Z", "+00:00")).replace(tzinfo=None)
                if ws <= event_dt < we:
                    week["count"] += 1
                    break
        except (ValueError, IndexError):
            continue

    print(f"  Processed {len(data)} events across 12 weeks")
    return weeks


def main():
    token = os.environ.get("GITHUB_TOKEN")

    # Load config to get username
    config_path = os.path.join(os.path.dirname(__file__), "..", "profile.config.json")
    with open(config_path, "r") as f:
        config = json.load(f)
    username = config["username"]

    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    # Fetch all data
    user = fetch_user(username, token)
    repos = fetch_repos(username, token)
    repo_stats = compute_repo_stats(repos)
    activity = fetch_activity(username, token)

    # Assemble output
    output = {
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "user": user,
        "repo_stats": repo_stats,
        "activity": activity,
    }

    out_path = os.path.join(data_dir, "github_data.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n[+] Data saved to {out_path}")

    return output


if __name__ == "__main__":
    main()
