#!/usr/bin/env python3
"""
Generate README.md from profile.config.json and data/github_data.json.

Produces a polished, dark-theme GitHub Profile Dashboard
with terminal card, animated typing, and visual rhythm.
"""

import json
import os
import sys


# ── Badge helpers ──────────────────────────────────────────────

LOGO_MAP = {
    "python": "python", "javascript": "javascript", "typescript": "typescript",
    "html5": "html5", "css3": "css3", "react": "react", "nextdotjs": "nextdotjs",
    "nodejs": "nodedotjs", "express": "express", "fastapi": "fastapi",
    "postgresql": "postgresql", "mongodb": "mongodb", "sqlite": "sqlite",
    "git": "git", "github": "github", "visualstudiocode": "visualstudiocode",
    "linux": "linux", "docker": "docker", "tailwindcss": "tailwindcss",
}

COLOR_MAP = {
    "Python": "3776AB", "JavaScript": "F7DF1E", "TypeScript": "3178C6",
    "HTML5": "E34F26", "CSS3": "1572B6", "React": "61DAFB",
    "Next.js": "000000", "Node.js": "339933", "Express": "000000",
    "FastAPI": "009688", "PostgreSQL": "4169E1", "MongoDB": "47A248",
    "SQLite": "003B57", "Git": "F05032", "GitHub": "181717",
    "VS Code": "007ACC", "Linux": "FCC624", "Docker": "2496ED",
    "Tailwind CSS": "06B6D4",
}

DARK_TEXT = {"JavaScript", "Next.js", "Linux"}


def badge(name: str, icon: str) -> str:
    logo = LOGO_MAP.get(icon.lower(), icon.lower())
    color = COLOR_MAP.get(name, "10b981")
    lc = "black" if name in DARK_TEXT else "white"
    return (f'![{name}](https://img.shields.io/badge/{name}-{color}'
            f'?style=flat-square&logo={logo}&logoColor={lc})')


def social_badge(label: str, url: str, color: str, icon: str) -> str:
    return (f'[![{label}](https://img.shields.io/badge/{label}-{color}'
            f'?style=flat-square&logo={icon}&logoColor=white)]({url})')


def wave() -> str:
    return '\n<img src="assets/stats/wave-divider.svg" width="100%" alt="" />\n'


# ── Section builders ──────────────────────────────────────────

def build_hero(config: dict) -> str:
    name = config["name"]
    username = config["username"]
    headline = config.get("headline", "")
    avatar = config["avatar_url"]
    accent = config["design"]["colors"]["accent"]
    social = config.get("social", {})

    links = []
    if social.get("github"):
        links.append(social_badge("GitHub", social["github"], "181717", "github"))
    if social.get("linkedin"):
        links.append(social_badge("LinkedIn", social["linkedin"], "0A66C2", "linkedin"))
    if social.get("twitter"):
        links.append(social_badge("Twitter", social["twitter"], "1DA1F2", "twitter"))
    if social.get("portfolio"):
        links.append(social_badge("Portfolio", social["portfolio"], accent, "aboutdotme"))
    if social.get("email"):
        links.append(social_badge("Email", f'mailto:{social["email"]}', "D14836", "gmail"))
    if not links:
        links.append(social_badge("GitHub", f'https://github.com/{username}', "181717", "github"))

    links_str = " \n".join(links)

    return f"""<div align="center">

<a href="https://github.com/{username}">
  <img src="{avatar}" width="130" height="130" style="border-radius:50%;border:4px solid {accent};" alt="{name}'s avatar" />
</a>

<h1 style="margin:4px 0;">{name}</h1>

<img src="assets/stats/typing-card.svg" alt="{headline}" />

<br/><br/>

{links_str}

</div>
"""


def build_tech_stack(config: dict) -> str:
    skills = config.get("skills", {})
    lines = []
    lines.append("")
    lines.append(f'<p align="center"><b>{"  ".join(badge(s["name"], s["icon"]) for s in skills.get("languages", []))}</b></p>')
    lines.append(f'<p align="center">{"  ".join(badge(s["name"], s["icon"]) for s in skills.get("frontend", []))}</p>')
    lines.append(f'<p align="center">{"  ".join(badge(s["name"], s["icon"]) for s in skills.get("backend", []))}</p>')
    lines.append(f'<p align="center">{"  ".join(badge(s["name"], s["icon"]) for s in skills.get("databases", []))}</p>')
    lines.append(f'<p align="center">{"  ".join(badge(s["name"], s["icon"]) for s in skills.get("tools", []))}</p>')
    lines.append("")
    return "\n".join(lines)


def build_current_focus(config: dict) -> str:
    focus = config.get("current_focus", {})
    if not any(focus.values()):
        return ""

    building = focus.get("building", [])
    learning = focus.get("learning", [])
    exploring = focus.get("exploring", [])

    max_len = max(len(building), len(learning), len(exploring), 1)
    while len(building) < max_len: building.append("")
    while len(learning) < max_len: learning.append("")
    while len(exploring) < max_len: exploring.append("")

    rows = []
    headers = ["\U0001F6E0\ufe0f Building", "\U0001F4DA Learning", "\U0001F52D Exploring"]
    for i in range(max_len):
        rows.append(f'  <tr><td>{building[i] or " "}</td><td>{learning[i] or " "}</td><td>{exploring[i] or " "}</td></tr>')

    return f"""

<table align="center">
  <tr>
    <th>{headers[0]}</th>
    <th>{headers[1]}</th>
    <th>{headers[2]}</th>
  </tr>
  {chr(10).join(rows)}
</table>

"""


def build_stats_section() -> str:
    return f"""
<div align="center">
  <img src="assets/stats/github-stats.svg" width="520" alt="GitHub Statistics" />
  <br/><br/>
  <img src="assets/stats/languages.svg" width="520" alt="Top Languages" />
  <br/><br/>
  <img src="assets/stats/activity.svg" width="520" alt="Contribution Activity" />
</div>

"""


def build_footer(config: dict) -> str:
    username = config["username"]
    social = config.get("social", {})
    links = []
    if social.get("github"):
        links.append(social_badge("GitHub", social["github"], "181717", "github"))
    if social.get("linkedin"):
        links.append(social_badge("LinkedIn", social["linkedin"], "0A66C2", "linkedin"))
    if social.get("email"):
        links.append(social_badge("Email", f'mailto:{social["email"]}', "D14836", "gmail"))
    if not links:
        links.append(social_badge("GitHub", f'https://github.com/{username}', "181717", "github"))

    links_str = " \n".join(links)
    return f"""
<div align="center">

{links_str}

<br/>
<sub>Automated with GitHub Actions</sub>

</div>
"""


# ── Main ─────────────────────────────────────────────────────

def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base, "profile.config.json")
    data_path = os.path.join(base, "data", "github_data.json")
    readme_path = os.path.join(base, "README.md")

    with open(config_path, "r") as f:
        config = json.load(f)

    data = {}
    if os.path.exists(data_path):
        with open(data_path, "r") as f:
            data = json.load(f)

    sections = [
        build_hero(config),
        wave(),
        '<div align="center">',
        '<img src="assets/stats/terminal-card.svg" width="520" alt="About Huzaifa" />',
        '</div>',
        "\n---\n",
        '<p align="center"><b>\u26A1 Tech Stack</b></p>',
        build_tech_stack(config),
        wave(),
        build_current_focus(config),
        wave(),
        build_stats_section(),
        wave(),
        build_footer(config),
    ]

    readme = "\n".join(sections)

    with open(readme_path, "w") as f:
        f.write(readme)

    print(f"\n[+] README.md generated ({len(readme)} bytes)")


if "__main__" == __name__:
    main()
