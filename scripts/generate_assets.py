#!/usr/bin/env python3
"""
Generate SVG dashboard assets from GitHub data and profile config.

Produces:
  assets/stats/typing-card.svg      — animated tagline with cursor
  assets/stats/terminal-card.svg     — whoami terminal card
  assets/stats/github-stats.svg      — stats card with gradient accent
  assets/stats/languages.svg         — language progress bars
  assets/stats/activity.svg          — weekly activity bars
  assets/stats/wave-divider.svg      — section divider wave
"""

import json
import math
import os
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom


# ── Design System ────────────────────────────────────────────
C = {
    "bg": "#0d1117",
    "surface": "#161b22",
    "border": "#30363d",
    "text": "#e6edf3",
    "text2": "#8b949e",
    "text3": "#6e7681",
    "accent": "#10b981",
    "accent_lt": "#34d399",
    "green_prompt": "#3fb950",
    "term_bg": "#0d1117",
    "red": "#ff5f57",
    "yellow": "#febc2e",
    "green_dot": "#28c840",
}

FF = "'-apple-system',BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
FF_MONO = "'SF Mono',SFMono-Regular,Consolas,'Liberation Mono',Menlo,monospace"

LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#F7DF1E", "TypeScript": "#3178C6",
    "HTML": "#E34F26", "CSS": "#563D7C", "Java": "#B07219",
    "C++": "#F34B7D", "C": "#555555", "Go": "#00ADD8",
    "Rust": "#DEA584", "Ruby": "#701516", "PHP": "#4F5D95",
    "Swift": "#F05138", "Kotlin": "#A97BFF", "Shell": "#89E051",
    "Vue": "#41B883", "Svelte": "#FF3E00", "Dart": "#00B4AB",
    "SCSS": "#C6538C",
}


def svg_str(elem: ET.Element) -> str:
    rough = ET.tostring(elem, encoding="unicode")
    parsed = minidom.parseString(rough)
    lines = [l for l in parsed.toprettyxml(indent="  ").split("\n") if l.strip()]
    return "\n".join(lines) + "\n"


def R(p, x, y, w, h, fill, rx=12, stroke=None, sw=1):
    a = {"x":str(x),"y":str(y),"width":str(w),"height":str(h),"rx":str(rx),"fill":fill}
    if stroke: a.update({"stroke":stroke,"stroke-width":str(sw)})
    ET.SubElement(p, "rect", a)


def T(p, x, y, txt, fill, sz=14, w="400", anc="start", ff=FF):
    a = {"x":str(x),"y":str(y),"fill":fill,"font-size":str(sz),
         "font-weight":w,"text-anchor":anc,"font-family":ff}
    el = ET.SubElement(p, "text", a); el.text = str(txt); return el


# ── Typing Card ─────────────────────────────────────────────
def gen_typing(config: dict, out: str):
    """Animated typing tagline with blinking emerald cursor."""
    tagline = config.get("tagline", "")
    roles = config.get("typing_roles", [
        "Full-Stack Developer",
        "Open Source Contributor",
        "Python & JavaScript",
    ])
    headline = config.get("headline", "")
    tw = 420
    th = 42

    svg = ET.Element("svg", {
        "xmlns":"http://www.w3.org/2000/svg", "width":str(tw), "height":str(th),
        "viewBox":f"0 0 {tw} {th}", "role":"img", "aria-label":headline,
    })
    # Background
    R(svg, 0, 0, tw, th, C["surface"], rx=21, stroke=C["border"])

    # Prompt chevron
    T(svg, 16, 27, "\u276F", C["accent"], sz=13, w="600", ff=FF_MONO)

    # Build animated text group with role cycling
    mid_x = 32
    if roles:
        for idx, role in enumerate(roles):
            begin_show = idx * 3.5
            begin_hide = begin_show + 3.0
            g = ET.SubElement(svg, "g")
            ET.SubElement(g, "set", {"attributeName":"opacity","to":"0"})
            ET.SubElement(g, "set", {"attributeName":"opacity","to":"1","begin":f"{begin_show}s"})
            ET.SubElement(g, "set", {"attributeName":"opacity","to":"0","begin":f"{begin_hide}s"})
            T(g, mid_x, 28, role, C["text"], sz=14, w="500", ff=FF_MONO)
    else:
        T(svg, mid_x, 28, headline, C["text"], sz=14, w="500", ff=FF_MONO)

    # Blinking cursor
    cursor_x = mid_x + len(roles[0]) * 8.2 + 6 if roles else mid_x + len(headline) * 8.2 + 6
    # Use a fixed reasonable x
    cursor_x = min(cursor_x, tw - 30)
    r = ET.SubElement(svg, "rect", {
        "x":str(cursor_x), "y":"14", "width":"2", "height":"18",
        "rx":"1", "fill":C["accent"]
    })
    ET.SubElement(r, "animate", {
        "attributeName":"opacity", "values":"1;0;1", "dur":"1.1s", "repeatCount":"indefinite"
    })

    with open(out, "w") as f:
        f.write(svg_str(svg))
    print(f"  [+] {out}")


# ── Terminal Card ────────────────────────────────────────────
def gen_terminal(config: dict, out: str):
    """macOS-style terminal card showing whoami output."""
    name = config.get("name", "")
    headline = config.get("headline", "")
    skills = config.get("skills", {})

    cw = 520
    pad = 18
    title_bar_h = 32
    lh = 22

    # Build terminal lines: list of (key, value, value_color)
    lines = [
        ("Name", name, C["text"]),
        ("Role", headline, C["text"]),
    ]

    langs = [s["name"] for s in skills.get("languages", [])]
    if langs:
        lines.append(("Langs", ", ".join(langs), C["accent_lt"]))

    focus = config.get("current_focus", {})
    building = focus.get("building", [])
    if building:
        lines.append(("Building", ", ".join(building[:2]), C["text"]))

    learning = focus.get("learning", [])
    if learning:
        lines.append(("Learning", ", ".join(learning[:2]), C["text"]))

    exploring = focus.get("exploring", [])
    if exploring:
        lines.append(("Exploring", ", ".join(exploring[:2]), C["text"]))

    ch = title_bar_h + pad + (lh + 2) + len(lines) * lh + lh + pad + 8

    svg = ET.Element("svg", {
        "xmlns":"http://www.w3.org/2000/svg", "width":str(cw), "height":str(ch),
        "viewBox":f"0 0 {cw} {ch}", "role":"img", "aria-label":"About Huzaifa",
    })

    # Outer card
    R(svg, 0, 0, cw, ch, C["surface"], rx=12, stroke=C["border"])

    # Title bar
    R(svg, 0, 0, cw, title_bar_h, C["border"], rx=12)
    R(svg, 0, title_bar_h - 6, cw, 6, C["border"], rx=0)

    # Traffic lights
    for i, color in enumerate([C["red"], C["yellow"], C["green_dot"]]):
        cx = 20 + i * 20
        ET.SubElement(svg, "circle", {"cx":str(cx), "cy":"16", "r":"6", "fill":color})

    T(svg, cw // 2, 21, "terminal", C["text3"], sz=12, w="500", anc="middle", ff=FF_MONO)

    y0 = title_bar_h + pad

    # $ whoami prompt
    T(svg, pad, y0, "$ whoami", C["green_prompt"], sz=13, w="600", ff=FF_MONO)
    y0 += lh + 6

    # Output lines using tspan for per-part coloring
    for key, val, val_color in lines:
        g = ET.SubElement(svg, "g")
        # Key (gray, fixed width)
        T(g, pad + 8, y0, key, C["text2"], sz=12, w="400", ff=FF_MONO)
        # Value (colored)
        val_x = pad + 8 + max(len(key), 4) * 8.4 + 16
        T(g, val_x, y0, val, val_color, sz=12, w="400", ff=FF_MONO)
        y0 += lh

    # Blinking cursor prompt
    y0 += 4
    T(svg, pad, y0, "$ ", C["green_prompt"], sz=13, w="600", ff=FF_MONO)
    blink = ET.SubElement(svg, "rect", {
        "x":str(pad + 18), "y":str(y0 - 12), "width":"8", "height":"16",
        "rx":"1", "fill":C["green_prompt"]
    })
    ET.SubElement(blink, "animate", {
        "attributeName":"opacity", "values":"1;0;1", "dur":"1s", "repeatCount":"indefinite"
    })

    with open(out, "w") as f:
        f.write(svg_str(svg))
    print(f"  [+] {out}")


# ── GitHub Stats Card ───────────────────────────────────────
def gen_stats(data: dict, config: dict, out: str):
    """Stats card with gradient top accent bar."""
    user = data.get("user", {})
    stats = data.get("repo_stats", {})

    repos = user.get("public_repos", 0)
    stars = stats.get("total_stars", 0)
    followers = user.get("followers", 0)
    following = user.get("following", 0)

    # If everything is zero, show a cleaner "getting started" card
    is_empty = (repos + stars + followers + following) == 0

    cw = 520
    ch = 155 if not is_empty else 120
    pad = 24
    accent_bar_h = 3

    svg = ET.Element("svg", {
        "xmlns":"http://www.w3.org/2000/svg", "width":str(cw), "height":str(ch),
        "viewBox":f"0 0 {cw} {ch}", "role":"img", "aria-label":"GitHub statistics",
    })

    defs = ET.SubElement(svg, "defs")
    grad = ET.SubElement(defs, "linearGradient", {
        "id":"accentGrad", "x1":"0%", "y1":"0%", "x2":"100%", "y2":"0%"
    })
    ET.SubElement(grad, "stop", {"offset":"0%", "stop-color":C["accent"]})
    ET.SubElement(grad, "stop", {"offset":"100%", "stop-color":C["accent_lt"]})

    # Card bg
    R(svg, 0, 0, cw, ch, C["surface"], rx=12, stroke=C["border"])

    # Gradient accent bar at top
    R(svg, 0, 0, cw, accent_bar_h, "url(#accentGrad)", rx=12)
    # Cover bottom corners of accent bar
    R(svg, 0, accent_bar_h - 2, cw, 2, "url(#accentGrad)", rx=0)

    if is_empty:
        # Clean empty state
        T(svg, pad, 52, "\u26A1", C["accent"], sz=28, w="400")
        T(svg, pad + 44, 52, "Just getting started", C["text"], sz=16, w="600")
        T(svg, pad, 78, "Stars, contributions, and more will appear here as I build.",
          C["text2"], sz=12)
        T(svg, pad, 98, "Watch this space grow.", C["text3"], sz=11)
    else:
        # Title
        T(svg, pad, 38, "\U0001F4CA  GitHub Stats", C["text"], sz=14, w="600")

        metrics = [
            (str(repos), "Repositories"),
            (str(stars), "Stars"),
            (str(followers), "Followers"),
            (str(following), "Following"),
        ]

        box_w = (cw - pad * 2 - 3 * 12) // 4
        for i, (val, label) in enumerate(metrics):
            x = pad + i * (box_w + 12)
            y = 55

            # Mini card
            R(svg, x, y, box_w, 78, C["bg"], rx=8, stroke=C["border"])

            # Value
            T(svg, x + box_w // 2, y + 40, val, C["accent"], sz=26, w="700", anc="middle")

            # Label
            T(svg, x + box_w // 2, y + 62, label, C["text2"], sz=11, w="500", anc="middle")

    with open(out, "w") as f:
        f.write(svg_str(svg))
    print(f"  [+] {out}")


# ── Languages Card ──────────────────────────────────────────
def gen_languages(data: dict, out: str):
    """Language distribution with colored progress bars."""
    languages = data.get("repo_stats", {}).get("languages", [])

    cw = 520
    pad = 20
    title_area = 42
    bottom_pad = 16
    row_h = 32

    if not languages:
        ch = title_area + 50 + bottom_pad
        svg = ET.Element("svg", {
            "xmlns":"http://www.w3.org/2000/svg", "width":str(cw), "height":str(ch),
            "viewBox":f"0 0 {cw} {ch}", "role":"img", "aria-label":"Top languages",
        })
        R(svg, 0, 0, cw, ch, C["surface"], rx=12, stroke=C["border"])
        T(svg, pad, 30, "\U0001F4C2  Top Languages", C["text"], sz=14, w="600")
        # Empty state with subtle icon
        T(svg, cw // 2, title_area + 32, "Push some code and your languages will show up here",
          C["text3"], sz=11, anc="middle")
        with open(out, "w") as f:
            f.write(svg_str(svg))
        print(f"  [+] {out} (empty)")
        return

    languages = languages[:6]
    ch = title_area + len(languages) * row_h + bottom_pad

    svg = ET.Element("svg", {
        "xmlns":"http://www.w3.org/2000/svg", "width":str(cw), "height":str(ch),
        "viewBox":f"0 0 {cw} {ch}", "role":"img", "aria-label":"Top languages",
    })
    R(svg, 0, 0, cw, ch, C["surface"], rx=12, stroke=C["border"])

    # Title
    T(svg, pad, 30, "\U0001F4C2  Top Languages", C["text"], sz=14, w="600")

    label_w = 100
    pct_w = 50
    bar_area = cw - pad * 2 - label_w - pct_w - 16
    max_pct = max(l["percentage"] for l in languages) or 1

    for i, lang in enumerate(languages):
        y = title_area + i * row_h
        color = LANG_COLORS.get(lang["name"], C["accent"])

        T(svg, pad, y + 21, lang["name"], C["text"], sz=12, w="500")

        bar_x = pad + label_w
        # Bar bg
        R(svg, bar_x, y + 11, bar_area, 11, C["bg"], rx=6, stroke=C["border"], sw=0.5)
        # Bar fill
        fill_w = max((lang["percentage"] / max_pct) * bar_area, 5) if max_pct > 0 else 5
        R(svg, bar_x, y + 11, fill_w, 11, color, rx=6)

        # Percentage
        T(svg, cw - pad, y + 21, f'{lang["percentage"]}%',
          C["text2"], sz=11, w="500", anc="end")

    with open(out, "w") as f:
        f.write(svg_str(svg))
    print(f"  [+] {out}")


# ── Activity Card ───────────────────────────────────────────
def gen_activity(data: dict, out: str):
    """Weekly activity bar chart."""
    weeks = data.get("activity", [])
    while len(weeks) < 12:
        weeks.append({"label": "", "count": 0})
    weeks = weeks[:12]

    cw = 520
    pad = 20
    title_area = 42
    bottom_pad = 28
    bar_max_h = 70
    bar_w = 26
    bar_gap = 10

    bars_w = 12 * bar_w + 11 * bar_gap
    start_x = (cw - bars_w) // 2
    max_count = max((w["count"] for w in weeks), default=1) or 1
    ch = title_area + bar_max_h + bottom_pad

    svg = ET.Element("svg", {
        "xmlns":"http://www.w3.org/2000/svg", "width":str(cw), "height":str(ch),
        "viewBox":f"0 0 {cw} {ch}", "role":"img", "aria-label":"Contribution activity",
    })
    R(svg, 0, 0, cw, ch, C["surface"], rx=12, stroke=C["border"])
    T(svg, pad, 30, "\U0001F4C8  Recent Activity", C["text"], sz=14, w="600")

    for i, week in enumerate(weeks):
        x = start_x + i * (bar_w + bar_gap)
        count = week["count"]
        bh = max((count / max_count) * bar_max_h, 3) if max_count > 0 else 3
        y = title_area + bar_max_h - bh

        R(svg, x, y, bar_w, bh, C["accent"], rx=4)

        if count > 0:
            T(svg, x + bar_w // 2, y - 5, str(count),
              C["accent_lt"], sz=9, w="600", anc="middle")

        label = week.get("label", "")
        if label:
            T(svg, x + bar_w // 2, title_area + bar_max_h + 16, label,
              C["text3"], sz=8, w="400", anc="middle")

    with open(out, "w") as f:
        f.write(svg_str(svg))
    print(f"  [+] {out}")


# ── Wave Divider ─────────────────────────────────────────────
def gen_wave(out: str):
    """Subtle emerald wave divider."""
    w, h = 800, 20
    svg = ET.Element("svg", {
        "xmlns":"http://www.w3.org/2000/svg", "width":str(w), "height":str(h),
        "viewBox":f"0 0 {w} {h}", "role":"img", "aria-label":"", "aria-hidden":"true",
    })
    # Build wave path
    points = []
    for x_i in range(0, w + 1, 4):
        y_val = h // 2 + math.sin(x_i * 0.02) * 4 + math.sin(x_i * 0.05) * 2
        points.append(f"{x_i},{y_val:.1f}")
    path_d = "M " + " L ".join(points)

    defs = ET.SubElement(svg, "defs")
    grad = ET.SubElement(defs, "linearGradient", {
        "id":"waveGrad", "x1":"0%", "y1":"0%", "x2":"100%", "y2":"0%"
    })
    ET.SubElement(grad, "stop", {"offset":"0%", "stop-color":"#10b98100"})
    ET.SubElement(grad, "stop", {"offset":"50%", "stop-color":C["accent"]})
    ET.SubElement(grad, "stop", {"offset":"100%", "stop-color":"#10b98100"})

    ET.SubElement(svg, "path", {
        "d":path_d, "fill":"none", "stroke":"url(#waveGrad)",
        "stroke-width":"1.5", "stroke-linecap":"round"
    })

    with open(out, "w") as f:
        f.write(svg_str(svg))
    print(f"  [+] {out}")


# ── Main ─────────────────────────────────────────────────────
def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base, "data", "github_data.json")
    config_path = os.path.join(base, "profile.config.json")
    assets_dir = os.path.join(base, "assets", "stats")
    os.makedirs(assets_dir, exist_ok=True)

    with open(config_path, "r") as f:
        config = json.load(f)

    data = {}
    if os.path.exists(data_path):
        with open(data_path, "r") as f:
            data = json.load(f)

    print("[*] Generating SVG assets...")
    gen_typing(config, os.path.join(assets_dir, "typing-card.svg"))
    gen_terminal(config, os.path.join(assets_dir, "terminal-card.svg"))
    gen_stats(data, config, os.path.join(assets_dir, "github-stats.svg"))
    gen_languages(data, os.path.join(assets_dir, "languages.svg"))
    gen_activity(data, os.path.join(assets_dir, "activity.svg"))
    gen_wave(os.path.join(assets_dir, "wave-divider.svg"))
    print("[+] All assets generated.")


if __name__ == "__main__":
    main()
