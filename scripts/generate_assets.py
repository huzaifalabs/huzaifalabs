#!/usr/bin/env python3
"""
Generate SVG dashboard assets from GitHub data.

Reads data/github_data.json and produces:
  assets/stats/github-stats.svg
  assets/stats/languages.svg
  assets/stats/activity.svg
"""

import json
import os
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

# ── Design System ────────────────────────────────────────────────
COLORS = {
    "bg": "#0d1117",
    "surface": "#161b22",
    "border": "#30363d",
    "text_primary": "#e6edf3",
    "text_secondary": "#8b949e",
    "accent": "#10b981",
    "accent_light": "#34d399",
    "accent_muted": "rgba(16,185,129,0.12)",
}

# Standard language colors (from GitHub linguist)
LANG_COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#F7DF1E",
    "TypeScript": "#3178C6",
    "HTML": "#E34F26",
    "CSS": "#563D7C",
    "Java": "#B07219",
    "C++": "#F34B7D",
    "C": "#555555",
    "Go": "#00ADD8",
    "Rust": "#DEA584",
    "Ruby": "#701516",
    "PHP": "#4F5D95",
    "Swift": "#F05138",
    "Kotlin": "#A97BFF",
    "Shell": "#89E051",
    "Dart": "#00B4AB",
    "Vue": "#41B883",
    "Svelte": "#FF3E00",
    "Jupyter Notebook": "#DA5B0B",
    "Dockerfile": "#384D54",
    "Lua": "#000080",
    "Zig": "#EC915C",
    "Nix": "#7E7EFF",
    "SCSS": "#C6538C",
}


def prettify_svg(elem: ET.Element) -> str:
    """Return a pretty-printed SVG string."""
    rough = ET.tostring(elem, encoding="unicode")
    parsed = minidom.parseString(rough)
    # Remove extra blank lines
    lines = [l for l in parsed.toprettyxml(indent="  ").split("\n") if l.strip()]
    return "\n".join(lines) + "\n"


def _rect(parent, x, y, w, h, fill, rx=12, stroke=None, stroke_width=1):
    """Helper: add a rounded rectangle."""
    attribs = {
        "x": str(x), "y": str(y),
        "width": str(w), "height": str(h),
        "rx": str(rx), "fill": fill,
    }
    if stroke:
        attribs["stroke"] = stroke
        attribs["stroke-width"] = str(stroke_width)
    ET.SubElement(parent, "rect", attribs)


def _text(parent, x, y, content, fill, size=14, weight="400", anchor="start", font_family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"):
    """Helper: add text element."""
    attribs = {
        "x": str(x), "y": str(y),
        "fill": fill,
        "font-size": str(size),
        "font-weight": weight,
        "text-anchor": anchor,
        "font-family": font_family,
    }
    el = ET.SubElement(parent, "text", attribs)
    el.text = str(content)
    return el


def generate_stats_svg(data: dict, out_path: str):
    """Generate github-stats.svg with key metrics in a card layout."""
    user = data.get("user", {})
    stats = data.get("repo_stats", {})

    metrics = [
        {"label": "Repositories", "value": user.get("public_repos", 0), "icon": "\U0001F4E6"},
        {"label": "Stars", "value": stats.get("total_stars", 0), "icon": "\u2B50"},
        {"label": "Followers", "value": user.get("followers", 0), "icon": "\U0001F465"},
        {"label": "Following", "value": user.get("following", 0), "icon": "\U0001F517"},
        {"label": "Forks", "value": stats.get("total_forks", 0), "icon": "\U0001F500"},
    ]

    card_w = 490
    card_h = 155
    pad = 24
    stat_w = (card_w - pad * 2 - (len(metrics) - 1) * 10) // len(metrics)

    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "width": str(card_w),
        "height": str(card_h),
        "viewBox": f"0 0 {card_w} {card_h}",
        "role": "img",
        "aria-label": "GitHub statistics dashboard",
    })

    # Background card
    _rect(svg, 0, 0, card_w, card_h, COLORS["surface"], rx=16, stroke=COLORS["border"])

    # Title
    _text(svg, pad, 30, "\U0001F4CA  GitHub Statistics", COLORS["text_primary"], size=15, weight="600")

    # Stat boxes
    for i, m in enumerate(metrics):
        x = pad + i * (stat_w + 10)
        y = 50

        # Stat card background
        _rect(svg, x, y, stat_w, 82, COLORS["bg"], rx=10, stroke=COLORS["border"])

        # Value
        val_str = str(m["value"])
        val_x = x + stat_w // 2
        _text(svg, val_x, y + 42, val_str, COLORS["accent"], size=28, weight="700", anchor="middle")

        # Label
        _text(svg, val_x, y + 66, m["label"], COLORS["text_secondary"], size=11, weight="500", anchor="middle")

    with open(out_path, "w") as f:
        f.write(prettify_svg(svg))
    print(f"  [+] Generated {out_path}")


def generate_languages_svg(data: dict, out_path: str):
    """Generate languages.svg with a horizontal bar chart."""
    languages = data.get("repo_stats", {}).get("languages", [])

    card_w = 490
    row_h = 30
    bar_h = 10
    pad = 24
    title_h = 40
    bottom_pad = 12

    if not languages:
        # Empty state
        card_h = title_h + 40 + bottom_pad
        svg = ET.Element("svg", {
            "xmlns": "http://www.w3.org/2000/svg",
            "width": str(card_w), "height": str(card_h),
            "viewBox": f"0 0 {card_w} {card_h}",
            "role": "img", "aria-label": "Language statistics",
        })
        _rect(svg, 0, 0, card_w, card_h, COLORS["surface"], rx=16, stroke=COLORS["border"])
        _text(svg, pad, 30, "\U0001F4C2  Top Languages", COLORS["text_primary"], size=15, weight="600")
        _text(svg, card_w // 2, title_h + 24, "Start pushing code to see your language breakdown",
              COLORS["text_secondary"], size=12, weight="400", anchor="middle")
        with open(out_path, "w") as f:
            f.write(prettify_svg(svg))
        print(f"  [+] Generated {out_path} (empty state)")
        return

    # Limit to top 6
    languages = languages[:6]
    card_h = title_h + len(languages) * row_h + bottom_pad

    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "width": str(card_w), "height": str(card_h),
        "viewBox": f"0 0 {card_w} {card_h}",
        "role": "img", "aria-label": "Language statistics",
    })

    _rect(svg, 0, 0, card_w, card_h, COLORS["surface"], rx=16, stroke=COLORS["border"])
    _text(svg, pad, 30, "\U0001F4C2  Top Languages", COLORS["text_primary"], size=15, weight="600")

    label_w = 95
    pct_w = 48
    bar_area = card_w - pad * 2 - label_w - pct_w - 12
    max_pct = max(l["percentage"] for l in languages) or 1

    for i, lang in enumerate(languages):
        y = title_h + i * row_h
        color = LANG_COLORS.get(lang["name"], COLORS["accent"])

        # Language name
        _text(svg, pad, y + 20, lang["name"], COLORS["text_primary"], size=13, weight="500")

        # Bar background
        bar_x = pad + label_w
        _rect(svg, bar_x, y + 10, bar_area, bar_h, COLORS["bg"], rx=5, stroke=COLORS["border"], stroke_width=0.5)

        # Bar fill
        fill_w = max((lang["percentage"] / max_pct) * bar_area, 4) if max_pct > 0 else 4
        _rect(svg, bar_x, y + 10, fill_w, bar_h, color, rx=5)

        # Percentage
        _text(svg, card_w - pad, y + 20, f"{lang['percentage']}%",
              COLORS["text_secondary"], size=12, weight="500", anchor="end")

    with open(out_path, "w") as f:
        f.write(prettify_svg(svg))
    print(f"  [+] Generated {out_path}")


def generate_activity_svg(data: dict, out_path: str):
    """Generate activity.svg with weekly contribution bars."""
    weeks = data.get("activity", [])

    card_w = 490
    pad = 24
    title_h = 40
    bottom_pad = 30
    bar_max_h = 80
    bar_w = 28
    bar_gap = 8

    # Ensure exactly 12 weeks
    while len(weeks) < 12:
        weeks.append({"label": "", "count": 0})
    weeks = weeks[:12]

    bars_area_w = 12 * bar_w + 11 * bar_gap
    bars_start_x = (card_w - bars_area_w) // 2

    card_h = title_h + bar_max_h + bottom_pad
    max_count = max((w["count"] for w in weeks), default=1) or 1

    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "width": str(card_w), "height": str(card_h),
        "viewBox": f"0 0 {card_w} {card_h}",
        "role": "img", "aria-label": "Contribution activity",
    })

    _rect(svg, 0, 0, card_w, card_h, COLORS["surface"], rx=16, stroke=COLORS["border"])
    _text(svg, pad, 30, "\U0001F4C8  Contribution Activity", COLORS["text_primary"], size=15, weight="600")

    for i, week in enumerate(weeks):
        x = bars_start_x + i * (bar_w + bar_gap)
        count = week["count"]
        bar_h = max((count / max_count) * bar_max_h, 3) if max_count > 0 else 3
        y = title_h + bar_max_h - bar_h

        # Bar
        _rect(svg, x, y, bar_w, bar_h, COLORS["accent"], rx=4)

        # Count label on top of bar
        if count > 0:
            _text(svg, x + bar_w // 2, y - 4, str(count),
                  COLORS["accent_light"], size=10, weight="600", anchor="middle")

        # Week label
        label = week.get("label", "")
        if label:
            _text(svg, x + bar_w // 2, title_h + bar_max_h + 16, label,
                  COLORS["text_secondary"], size=9, weight="400", anchor="middle")

    with open(out_path, "w") as f:
        f.write(prettify_svg(svg))
    print(f"  [+] Generated {out_path}")


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base, "data", "github_data.json")
    assets_dir = os.path.join(base, "assets", "stats")
    os.makedirs(assets_dir, exist_ok=True)

    if not os.path.exists(data_path):
        print("ERROR: data/github_data.json not found. Run fetch_data.py first.")
        sys.exit(1)

    with open(data_path, "r") as f:
        data = json.load(f)

    print("[*] Generating SVG assets...")
    generate_stats_svg(data, os.path.join(assets_dir, "github-stats.svg"))
    generate_languages_svg(data, os.path.join(assets_dir, "languages.svg"))
    generate_activity_svg(data, os.path.join(assets_dir, "activity.svg"))
    print("[+] All SVG assets generated.")


if __name__ == "__main__":
    main()
