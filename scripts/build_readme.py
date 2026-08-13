#!/usr/bin/env python3
"""
Generate README.md from profile.config.json and data/github_data.json.

Produces a polished, dark-theme GitHub Profile Dashboard.
"""

import json
import os
import sys


# ── Badge helpers ──────────────────────────────────────────────

def tech_badge(name: str, icon: str) -> str:
    """Generate a shields.io flat-square badge for a technology."""
    logo_map = {
        "python": "python",
        "javascript": "javascript",
        "typescript": "typescript",
        "html5": "html5",
        "css3": "css3",
        "react": "react",
        "nextdotjs": "nextdotjs",
        "nodejs": "nodedotjs",
        "express": "express",
        "fastapi": "fastapi",
        "postgresql": "postgresql",
        "mongodb": "mongodb",
        "sqlite": "sqlite",
        "git": "git",
        "github": "github",
        "visualstudiocode": "visualstudiocode",
        "linux": "linux",
        "docker": "docker",
        "tailwindcss": "tailwindcss",
        "graphql": "graphql",
        "redis": "redis",
        "firebase": "firebase",
        "supabase": "supabase",
        "vercel": "vercel",
        "nginx": "nginx",
        "figma": "figma",
    }
    logo = logo_map.get(icon.lower(), icon.lower())
    color_map = {
        "Python": "3776AB", "JavaScript": "F7DF1E", "TypeScript": "3178C6",
        "HTML5": "E34F26", "CSS3": "1572B6", "React": "61DAFB",
        "Next.js": "000000", "Node.js": "339933", "Express": "000000",
        "FastAPI": "009688", "PostgreSQL": "4169E1", "MongoDB": "47A248",
        "SQLite": "003B57", "Git": "F05032", "GitHub": "181717",
        "VS Code": "007ACC", "Linux": "FCC624", "Docker": "2496ED",
        "Tailwind CSS": "06B6D4", "GraphQL": "E10098", "Redis": "DC382D",
        "Firebase": "FFCA28", "Supabase": "3FCF8E", "Vercel": "000000",
        "Nginx": "009639", "Figma": "F24E1E",
    }
    color = color_map.get(name, "10b981")
    # Use white text for dark badge backgrounds
    white_text = ["JavaScript", "Next.js", "Express", "Linux"]
    logo_color = "white" if name in white_text else "white"
    if name == "JavaScript":
        logo_color = "black"
    return f"![{name}](https://img.shields.io/badge/{name}-{color}?style=flat-square&logo={logo}&logoColor={logo_color})"


def social_badge(label: str, url: str, color: str = "10b981", icon: str = "") -> str:
    """Generate a social link badge."""
    logo_param = f"&logo={icon}" if icon else ""
    return f"[{label}]({url})"


def divider() -> str:
    """A subtle emerald-accented divider line."""
    return f'\n<img src="https://raw.githubusercontent.com/huzaifalabs/huzaifalabs/main/assets/stats/divider.svg" width="100%" alt="" />\n'


# ── Section builders ──────────────────────────────────────────

def build_hero(config: dict) -> str:
    """Build the hero/banner section."""
    name = config["name"]
    username = config["username"]
    headline = config["headline"]
    tagline = config["tagline"]
    avatar = config["avatar_url"]
    social = config.get("social", {})
    accent = config["design"]["colors"]["accent"]

    # Social link badges
    links = []
    if social.get("github"):
        links.append(f'[![GitHub](https://img.shields.io/badge/GitHub-{username}-181717?style=flat-square&logo=github&logoColor=white)]({social["github"]})')
    if social.get("linkedin"):
        links.append('[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](' + social["linkedin"] + ")")
    if social.get("twitter"):
        links.append('[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=flat-square&logo=twitter&logoColor=white)](' + social["twitter"] + ")")
    if social.get("portfolio"):
        links.append(f'[![Portfolio](https://img.shields.io/badge/Portfolio-{accent}?style=flat-square&logo=aboutdotme&logoColor=white)]({social["portfolio"]})')
    if social.get("email"):
        links.append(f'[![Email](https://img.shields.io/badge/Email-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:{social["email"]})')

    links_html = " \n".join(links) if links else f'[![GitHub](https://img.shields.io/badge/GitHub-{username}-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/{username})'

    return f"""<div align="center">

<img src="{avatar}" width="110" height="110" style="border-radius: 50%; border: 3px solid {accent};" alt="{name}'s avatar" />

<h1>Hi, I'm {name}</h1>

<b>{headline}</b><br/>
<span style="color: #8b949e; font-size: 1.05em;">{tagline}</span>

<br/><br/>

{links_html}

</div>
"""


def build_about(config: dict) -> str:
    """Build the About Me section."""
    about = config.get("about", "")
    if not about:
        return ""
    return f"""### \u258E About Me

> {about}
"""


def build_tech_stack(config: dict) -> str:
    """Build the Tech Stack section with organized badge groups."""
    skills = config.get("skills", {})
    lines = ["### \u258E Tech Stack", ""]

    category_labels = {
        "languages": "Languages",
        "frontend": "Frontend",
        "backend": "Backend",
        "databases": "Databases",
        "tools": "Tools & Platforms",
    }

    for key, label in category_labels.items():
        items = skills.get(key, [])
        if not items:
            continue
        badges = " ".join(tech_badge(item["name"], item["icon"]) for item in items)
        lines.append(f"**{label}**\n")
        lines.append(badges)
        lines.append("")

    return "\n".join(lines).rstrip()


def build_current_focus(config: dict) -> str:
    """Build the Current Focus section as a clean table."""
    focus = config.get("current_focus", {})
    if not any(focus.values()):
        return ""

    building = focus.get("building", [])
    learning = focus.get("learning", [])
    exploring = focus.get("exploring", [])

    # Pad lists to same length
    max_len = max(len(building), len(learning), len(exploring), 1)
    while len(building) < max_len:
        building.append("")
    while len(learning) < max_len:
        learning.append("")
    while len(exploring) < max_len:
        exploring.append("")

    rows = []
    for i in range(max_len):
        b = building[i] or ""
        l = learning[i] or ""
        e = exploring[i] or ""
        rows.append(f"| {b} | {l} | {e} |")

    header = "| \U0001F535 Building | \U0001F7E2 Learning | \U0001F7E1 Exploring |"
    sep = "|---|---|---|"

    return f"""### \u258E Current Focus

{header}
{sep}
{chr(10).join(rows)}
"""


def build_featured_projects(config: dict, data: dict) -> str:
    """Build Featured Projects section."""
    # Check config first, then auto-detect from data
    featured = config.get("featured_projects", [])
    if featured:
        return _format_featured_list(featured)

    # Auto-detect: use top repos from data
    repos = data.get("repo_stats", {}).get("top_repos", [])
    non_empty = [r for r in repos if r.get("description")]
    if not non_empty:
        return ""

    lines = ["### \u258E Featured Projects", ""]
    for r in non_empty[:4]:
        name = r["name"]
        desc = r.get("description", "")
        lang = r.get("language", "")
        stars = r.get("stargazers_count", 0)
        url = r.get("html_url", "")
        homepage = r.get("homepage", "")

        meta_parts = []
        if lang:
            meta_parts.append(lang)
        if stars > 0:
            meta_parts.append(f"\u2B50 {stars}")
        meta = " \u00B7 ".join(meta_parts)

        link = f"[**{name}**]({url})"
        demo = f" \u00B7 [Live Demo]({homepage})" if homepage else ""
        lines.append(f"{link}{demo}")
        if desc:
            lines.append(f"> {desc}")
        if meta:
            lines.append(f"<sub>{meta}</sub>")
        lines.append("")

    return "\n".join(lines).rstrip()


def _format_featured_list(projects: list) -> str:
    """Format featured projects from config."""
    lines = ["### \u258E Featured Projects", ""]
    for p in projects:
        name = p.get("name", "")
        desc = p.get("description", "")
        url = p.get("url", "")
        demo = p.get("demo_url", "")
        tech = p.get("tech", [])

        link = f"[**{name}**]({url})"
        demo_str = f" \u00B7 [Demo]({demo})" if demo else ""
        tech_str = f"<sub>{' \u00B7 '.join(tech)}</sub>" if tech else ""

        lines.append(f"{link}{demo_str}")
        if desc:
            lines.append(f"> {desc}")
        if tech_str:
            lines.append(tech_str)
        lines.append("")

    return "\n".join(lines).rstrip()


def build_stats_section() -> str:
    """Build the GitHub Statistics section with SVG."""
    return f"""### \u258E GitHub Statistics

![GitHub Statistics](assets/stats/github-stats.svg)
"""


def build_languages_section() -> str:
    """Build the Top Languages section with SVG."""
    return f"""### \u258E Top Languages

![Language Statistics](assets/stats/languages.svg)
"""


def build_activity_section() -> str:
    """Build the Contribution Activity section with SVG."""
    return f"""### \u258E Contribution Activity

![Contribution Activity](assets/stats/activity.svg)
"""


def build_journey_section(config: dict) -> str:
    """Build a Developer Journey section if enough info exists."""
    # For now, build a minimal version based on account age
    # This section can be expanded manually in the config later
    return """### \u258E Developer Journey

| Period | Focus |
|--------|-------|
| 2025 | Started learning web development fundamentals |
| 2026 | Building full-stack applications and exploring open source |
"""


def build_footer(config: dict) -> str:
    """Build the footer/contact section."""
    username = config["username"]
    accent = config["design"]["colors"]["accent"]
    social = config.get("social", {})

    links = []
    if social.get("github"):
        links.append(f'[![GitHub](https://img.shields.io/badge/GitHub-{username}-181717?style=flat-square&logo=github&logoColor=white)]({social["github"]})')
    if social.get("linkedin"):
        links.append('[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](' + social["linkedin"] + ")")
    if social.get("email"):
        links.append(f'[![Email](https://img.shields.io/badge/Email-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:{social["email"]})')

    if not links:
        links.append(f'[![GitHub](https://img.shields.io/badge/GitHub-{username}-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/{username})')

    links_str = " \n".join(links)

    return f"""<div align="center">

### \u258E Let's Connect

{links_str}

<br/>
<sub>Built with care \u00B7 Automated with GitHub Actions</sub>

</div>
"""


# ── Divider SVG generator (inline) ──────────────────────────

def generate_divider_svg(out_path: str):
    """Generate a subtle emerald gradient divider SVG."""
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="2" viewBox="0 0 496 2" fill="none">
  <line x1="0" y1="1" x2="496" y2="1" stroke="#30363d" stroke-width="1"/>
  <line x1="0" y1="1" x2="80" y2="1" stroke="#10b981" stroke-width="2"/>
</svg>
'''
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(svg_content)
    print(f"  [+] Generated divider SVG")


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

    # Generate divider SVG
    divider_path = os.path.join(base, "assets", "stats", "divider.svg")
    generate_divider_svg(divider_path)

    # Build README sections
    sections = []
    sections.append(build_hero(config))
    sections.append("---\n")
    sections.append(build_about(config))
    sections.append(divider())
    sections.append(build_tech_stack(config))
    sections.append(divider())
    sections.append(build_current_focus(config))

    # Featured projects (only if there's data)
    featured = build_featured_projects(config, data)
    if featured:
        sections.append(divider())
        sections.append(featured)

    sections.append(divider())
    sections.append(build_stats_section())
    sections.append("")
    sections.append(build_languages_section())
    sections.append("")
    sections.append(build_activity_section())
    sections.append(divider())
    sections.append(build_journey_section(config))
    sections.append(divider())
    sections.append(build_footer(config))

    readme = "\n".join(sections)

    with open(readme_path, "w") as f:
        f.write(readme)

    print(f"\n[+] README.md generated ({len(readme)} bytes)")


if __name__ == "__main__":
    main()
