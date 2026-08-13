#!/usr/bin/env python3
"""
Generate README.md from profile.config.json and data/github_data.json.

Neon Dark Edition - Cool, visually striking GitHub profile dashboard.
Fixes: shields.io badges use <img> HTML tags (not markdown) to render
properly inside HTML block elements on GitHub.
"""

import json
import os
import sys


# ── Badge helpers (using <img> HTML tags for GitHub compatibility) ──

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


def badge_img(name: str, icon: str) -> str:
    """Return an <img> HTML tag (NOT markdown) for shields.io badges.
    This is critical: markdown ![]() does NOT render inside HTML block
    elements like <p> or <div> on GitHub.
    """
    logo = LOGO_MAP.get(icon.lower(), icon.lower())
    color = COLOR_MAP.get(name, "10b981")
    lc = "black" if name in DARK_TEXT else "white"
    url = f'https://img.shields.io/badge/{name}-{color}?style=flat-square&logo={logo}&logoColor={lc}'
    return f'<img src="{url}" alt="{name}" height="22"/>'


def social_badge(label: str, url: str, color: str, icon: str) -> str:
    """Return a clickable <a> wrapping an <img> badge."""
    badge_url = f'https://img.shields.io/badge/{label}-{color}?style=flat-square&logo={icon}&logoColor=white'
    return f'<a href="{url}"><img src="{badge_url}" alt="{label}" height="22"/></a>'


def wave() -> str:
    return '<img src="assets/stats/wave-divider.svg" width="100%" alt=""/>\n'


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

<img src="assets/stats/banner.svg" width="100%" alt="{name} - {headline}" />

<a href="https://github.com/{username}">
  <img src="{avatar}" width="120" height="120" style="border-radius:50%;border:3px solid {accent};margin-top:-60px;position:relative;z-index:1;background:{config['design']['colors']['bg']};" alt="{name}'s avatar" />
</a>

<br/>

<img src="assets/stats/typing-card.svg" alt="{headline}" />

<br/><br/>

{links_str}

</div>
"""


def build_tech_stack(config: dict) -> str:
    """Build tech stack using custom SVG + fallback shields.io badges as <img>."""
    skills = config.get("skills", {})
    lines = []
    lines.append("")
    lines.append('<div align="center">')
    lines.append('<img src="assets/stats/skills.svg" alt="Tech Stack" />')
    lines.append('</div>')
    lines.append("")
    return "\n".join(lines)


def build_tech_stack_badges(config: dict) -> str:
    """Inline badge fallback using <img> tags (not markdown ![]())."""
    skills = config.get("skills", {})
    lines = []
    lines.append("")

    categories = [
        ("\U0001F4D8 Languages", skills.get("languages", [])),
        ("\U0001F3A8 Frontend", skills.get("frontend", [])),
        ("\u2699\ufe0f Backend", skills.get("backend", [])),
        ("\U0001F5C4\ufe0f Databases", skills.get("databases", [])),
        ("\U0001F6E0\ufe0f Tools", skills.get("tools", [])),
    ]

    for cat_label, items in categories:
        if items:
            badges = " \n".join(badge_img(s["name"], s["icon"]) for s in items)
            lines.append(f'<div align="center">')
            lines.append(f'<b>{cat_label}</b><br/>')
            lines.append(badges)
            lines.append(f'</div>')
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
    while len(building) < max_len:
        building.append("")
    while len(learning) < max_len:
        learning.append("")
    while len(exploring) < max_len:
        exploring.append("")

    rows = []
    for i in range(max_len):
        rows.append(
            f'  <tr>\n'
            f'    <td align="center">{building[i] or "&nbsp;"}</td>\n'
            f'    <td align="center">{learning[i] or "&nbsp;"}</td>\n'
            f'    <td align="center">{exploring[i] or "&nbsp;"}</td>\n'
            f'  </tr>'
        )

    return f"""

<table align="center" width="80%">
  <tr>
    <th align="center">\U0001F6E0\ufe0f Building</th>
    <th align="center">\U0001F4DA Learning</th>
    <th align="center">\U0001F52D Exploring</th>
  </tr>
  {chr(10).join(rows)}
</table>

"""


def build_stats_section() -> str:
    return f"""
<div align="center">
  <img src="assets/stats/github-stats.svg" width="580" alt="GitHub Statistics" />
  <br/><br/>
  <img src="assets/stats/languages.svg" width="580" alt="Top Languages" />
  <br/><br/>
  <img src="assets/stats/activity.svg" width="580" alt="Contribution Activity" />
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
<img src="assets/stats/wave-divider.svg" width="100%" alt=""/>
<sub>Built with Python + SVG + GitHub Actions</sub>

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
        '<img src="assets/stats/terminal-card.svg" width="580" alt="About Huzaifa" />',
        '</div>',
        wave(),
        build_tech_stack(config),
        build_tech_stack_badges(config),
        wave(),
        build_current_focus(config),
        wave(),
        build_stats_section(),
        build_footer(config),
    ]

    readme = "\n".join(sections)

    with open(readme_path, "w") as f:
        f.write(readme)

    print(f"\n[+] README.md generated ({len(readme)} bytes)")


if "__main__" == __name__:
    main()
