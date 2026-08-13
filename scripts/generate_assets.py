#!/usr/bin/env python3
"""
Generate SVG dashboard assets - COOL EDITION v2

GitHub-safe SVGs: NO <filter> elements (GitHub strips them).
Uses gradients, opacity animations, layered shapes, and
animate (SMIL) for visual effects instead.

Produces:
  assets/stats/banner.svg       — animated gradient banner with waves
  assets/stats/typing-card.svg   — animated typing with cursor
  assets/stats/terminal-card.svg  — sleek terminal card
  assets/stats/skills.svg        — custom skill pills
  assets/stats/github-stats.svg  — glowing stat cards
  assets/stats/languages.svg     — language progress bars
  assets/stats/activity.svg      — weekly activity bars
  assets/stats/wave-divider.svg  — section divider
"""

import json
import math
import os
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom


# ── Design System v2 — Neon Dark (GitHub-safe) ──────────────
C = {
    "bg":           "#0a0a0f",
    "surface":      "#12121a",
    "surface2":     "#1a1a2e",
    "border":       "#2a2a3e",
    "border_lt":    "#3a3a5e",
    "text":         "#eaeaff",
    "text2":        "#8888aa",
    "text3":        "#555577",
    "accent":       "#00f5a0",
    "accent2":      "#00d9f5",
    "purple":       "#a855f7",
    "pink":         "#f472b6",
    "green_prompt": "#00f5a0",
    "red":          "#ff5f57",
    "yellow":       "#febc2e",
    "green_dot":    "#28c840",
}

FF = "sans-serif"
FF_MONO = "Consolas,monospace"

LANG_COLORS = {
    "Python":     "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178C6",
    "HTML":       "#E34F26", "CSS":       "#563D7C", "Java":       "#B07219",
    "C++":        "#F34B7D", "C":         "#555555", "Go":         "#00ADD8",
    "Rust":       "#DEA584", "Ruby":      "#701516", "PHP":        "#4F5D95",
    "Swift":      "#F05138", "Kotlin":    "#A97BFF", "Shell":      "#89E051",
    "Vue":        "#41B883", "Svelte":    "#FF3E00", "Dart":       "#00B4AB",
    "SCSS":       "#C6538C",
}

SKILL_COLORS = {
    "Python":     "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178C6",
    "HTML5":      "#E34F26", "CSS3":      "#1572B6", "React":      "#61DAFB",
    "Next.js":    "#ffffff", "Node.js":    "#339933", "Express":    "#888888",
    "FastAPI":    "#009688", "PostgreSQL": "#4169E1", "MongoDB":    "#47A248",
    "SQLite":     "#003B57", "Git":        "#F05032", "GitHub":     "#888888",
    "VS Code":    "#007ACC", "Linux":      "#FCC624", "Docker":     "#2496ED",
}


def svg_str(elem):
    rough = ET.tostring(elem, encoding="unicode")
    parsed = minidom.parseString(rough)
    lines = [l for l in parsed.toprettyxml(indent="  ").split("\n") if l.strip()]
    return "\n".join(lines) + "\n"


def R(p, x, y, w, h, fill, rx=12, stroke=None, sw=1):
    a = {"x": str(x), "y": str(y), "width": str(w), "height": str(h),
         "rx": str(rx), "fill": fill}
    if stroke:
        a.update({"stroke": stroke, "stroke-width": str(sw)})
    ET.SubElement(p, "rect", a)


def T(p, x, y, txt, fill, sz=14, w="400", anc="start", ff=FF):
    a = {"x": str(x), "y": str(y), "fill": fill, "font-size": str(sz),
         "font-weight": w, "text-anchor": anc, "font-family": ff}
    el = ET.SubElement(p, "text", a)
    el.text = str(txt)
    return el


def add_gradient(defs, grad_id, colors):
    """Add a linear gradient — these work fine on GitHub."""
    grad = ET.SubElement(defs, "linearGradient", {
        "id": grad_id, "x1": "0%", "y1": "0%", "x2": "100%", "y2": "0%"
    })
    n = len(colors)
    for i, color in enumerate(colors):
        ET.SubElement(grad, "stop", {
            "offset": f"{int(i * 100 / (n - 1))}%" if n > 1 else "0%",
            "stop-color": color
        })


def glow_circle(p, cx, cy, r, color, opacity="0.15"):
    """Faux glow using a larger transparent circle behind the main one."""
    ET.SubElement(p, "circle", {
        "cx": str(cx), "cy": str(cy), "r": str(r * 3),
        "fill": color, "opacity": opacity
    })
    ET.SubElement(p, "circle", {
        "cx": str(cx), "cy": str(cy), "r": str(r), "fill": color
    })


def glow_rect(p, x, y, w, h, color, rx=6, opacity="0.12"):
    """Faux glow using a larger transparent rect behind."""
    pad = 4
    ET.SubElement(p, "rect", {
        "x": str(x - pad), "y": str(y - pad),
        "width": str(w + pad * 2), "height": str(h + pad * 2),
        "rx": str(rx + 2), "fill": color, "opacity": opacity
    })


# ── Banner SVG ──────────────────────────────────────────────
def gen_banner(config, out):
    name = config.get("name", "")
    headline = config.get("headline", "")
    tagline = config.get("tagline", "")
    bw, bh = 900, 180

    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "width": str(bw), "height": str(bh),
        "viewBox": f"0 0 {bw} {bh}",
        "role": "img", "aria-label": f"{name} - {headline}",
    })

    defs = ET.SubElement(svg, "defs")
    add_gradient(defs, "bg", ["#0a0a0f", "#12121a", "#0a0a0f"])
    add_gradient(defs, "wg1", [C["accent"], C["accent2"], C["purple"]])
    add_gradient(defs, "wg2", [C["purple"], C["accent2"], C["accent"]])
    add_gradient(defs, "accentLine", [C["accent"], C["accent2"]])

    # Background
    R(svg, 0, 0, bw, bh, "url(#bg)", rx=0)

    # Subtle grid
    for gx in range(0, bw + 1, 50):
        ET.SubElement(svg, "line", {
            "x1": str(gx), "y1": "0", "x2": str(gx), "y2": str(bh),
            "stroke": C["accent"], "stroke-width": "0.3", "opacity": "0.06"
        })
    for gy in range(0, bh + 1, 50):
        ET.SubElement(svg, "line", {
            "x1": "0", "y1": str(gy), "x2": str(bw), "y2": str(gy),
            "stroke": C["accent"], "stroke-width": "0.3", "opacity": "0.06"
        })

    # Wave 1 (back, subtle)
    pts = []
    for x_i in range(0, bw + 1, 5):
        y_val = bh * 0.55 + math.sin(x_i * 0.008 + 1) * 22 + math.sin(x_i * 0.015) * 10
        pts.append(f"{x_i},{y_val:.1f}")
    d = "M0," + str(bh) + " L" + " L".join(pts) + f" L{bw},{bh} Z"
    ET.SubElement(svg, "path", {"d": d, "fill": "url(#wg1)", "opacity": "0.10"})

    # Wave 2 (front)
    pts2 = []
    for x_i in range(0, bw + 1, 5):
        y_val = bh * 0.65 + math.sin(x_i * 0.01 + 3) * 18 + math.sin(x_i * 0.02 + 1) * 8
        pts2.append(f"{x_i},{y_val:.1f}")
    d2 = "M0," + str(bh) + " L" + " L".join(pts2) + f" L{bw},{bh} Z"
    ET.SubElement(svg, "path", {"d": d2, "fill": "url(#wg2)", "opacity": "0.07"})

    # Floating particles with pulse animation
    for i in range(10):
        px = (i * 89 + 30) % bw
        py = 25 + (i * 41) % (bh - 70)
        r = 1.5 + (i % 3)
        c = C["accent"] if i % 2 == 0 else C["accent2"]
        circle = ET.SubElement(svg, "circle", {
            "cx": str(px), "cy": str(py), "r": str(r),
            "fill": c, "opacity": "0.25"
        })
        ET.SubElement(circle, "animate", {
            "attributeName": "opacity", "values": "0.1;0.5;0.1",
            "dur": f"{2 + i * 0.4}s", "repeatCount": "indefinite"
        })

    # Faux glow behind name
    ET.SubElement(svg, "ellipse", {
        "cx": str(bw // 2), "cy": "65", "rx": "180", "ry": "30",
        "fill": C["accent"], "opacity": "0.04"
    })

    # Name
    T(svg, bw // 2, 68, name, C["text"], sz=34, w="800", anc="middle")

    # Headline in accent color
    T(svg, bw // 2, 100, headline, C["accent"], sz=17, w="500", anc="middle")

    # Tagline
    if tagline:
        T(svg, bw // 2, 125, tagline, C["text2"], sz=12, w="400", anc="middle")

    # Bottom accent line
    line = ET.SubElement(svg, "rect", {
        "x": str(int(bw * 0.2)), "y": str(bh - 4),
        "width": str(int(bw * 0.6)), "height": "2",
        "rx": "1", "fill": "url(#accentLine)", "opacity": "0.5"
    })
    ET.SubElement(line, "animate", {
        "attributeName": "opacity", "values": "0.3;0.7;0.3",
        "dur": "3s", "repeatCount": "indefinite"
    })

    with open(out, "w") as f:
        f.write(svg_str(svg))
    print(f"  [+] {out}")


# ── Typing Card ─────────────────────────────────────────────
def gen_typing(config, out):
    roles = config.get("typing_roles", ["Full-Stack Developer", "Open Source Contributor"])
    headline = config.get("headline", "")
    tw, th = 480, 44

    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg", "width": str(tw), "height": str(th),
        "viewBox": f"0 0 {tw} {th}", "role": "img", "aria-label": headline,
    })

    defs = ET.SubElement(svg, "defs")
    add_gradient(defs, "typeGrad", [C["accent"], C["accent2"]])

    # Background pill
    R(svg, 0, 0, tw, th, C["surface"], rx=22, stroke=C["border"], sw=1)

    # Accent dot with faux glow
    glow_circle(svg, 18, th // 2, 4, C["accent"], "0.2")

    # Animated text cycling using <animate> (GitHub strips <set>)
    mid_x = 34
    if roles:
        n = len(roles)
        cycle_dur = n * 3.5
        for idx, role in enumerate(roles):
            # Build values/keyTimes for: hidden -> visible -> hidden
            show_start = idx * 3.5 / cycle_dur
            show_end = (idx * 3.5 + 3.0) / cycle_dur
            g = ET.SubElement(svg, "g")
            vals = f"0;0;1;1;0;0"
            times = f"0;{show_start:.4f};{show_start:.4f};{show_end:.4f};{show_end:.4f};1"
            ET.SubElement(g, "animate", {
                "attributeName": "opacity",
                "values": vals,
                "keyTimes": times,
                "dur": f"{cycle_dur}s",
                "repeatCount": "indefinite"
            })
            T(g, mid_x, 28, role, C["text"], sz=13, w="500", ff=FF_MONO)
    else:
        T(svg, mid_x, 28, headline, C["text"], sz=13, w="500", ff=FF_MONO)

    # Cursor with faux glow
    cursor_x = min(mid_x + 22 * 8.2 + 6, tw - 30)
    glow_rect(svg, cursor_x - 2, 12, 6, 20, C["accent"], rx=2, opacity="0.3")
    r = ET.SubElement(svg, "rect", {
        "x": str(cursor_x), "y": "13", "width": "2", "height": "18",
        "rx": "1", "fill": C["accent"]
    })
    ET.SubElement(r, "animate", {
        "attributeName": "opacity", "values": "1;0;1",
        "dur": "1.1s", "repeatCount": "indefinite"
    })

    with open(out, "w") as f:
        f.write(svg_str(svg))
    print(f"  [+] {out}")


# ── Terminal Card ────────────────────────────────────────────
def gen_terminal(config, out):
    name = config.get("name", "")
    headline = config.get("headline", "")
    skills = config.get("skills", {})

    cw = 580
    pad = 20
    title_bar_h = 36
    lh = 24

    lines = [
        ("name", name, C["text"]),
        ("role", headline, C["accent"]),
    ]

    langs = [s["name"] for s in skills.get("languages", [])]
    if langs:
        lines.append(("langs", ", ".join(langs), C["accent2"]))

    focus = config.get("current_focus", {})
    for key in ["building", "learning", "exploring"]:
        items = focus.get(key, [])
        if items:
            lines.append((key, ", ".join(items[:2]), C["text2"]))

    ch = title_bar_h + pad + (lh + 4) + len(lines) * lh + lh + pad + 12

    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg", "width": str(cw), "height": str(ch),
        "viewBox": f"0 0 {cw} {ch}", "role": "img", "aria-label": f"About {name}",
    })

    defs = ET.SubElement(svg, "defs")
    add_gradient(defs, "termLine", [C["accent"], C["accent2"]])

    # Card background
    R(svg, 0, 0, cw, ch, C["surface"], rx=14, stroke=C["border"], sw=1)

    # Title bar
    R(svg, 0, 0, cw, title_bar_h, C["surface2"], rx=14)
    R(svg, 0, title_bar_h - 4, cw, 4, C["surface2"], rx=0)

    # Gradient accent line under title bar
    ET.SubElement(svg, "rect", {
        "x": "0", "y": str(title_bar_h - 1), "width": str(cw), "height": "1",
        "fill": "url(#termLine)", "opacity": "0.5"
    })

    # Traffic lights
    for i, color in enumerate([C["red"], C["yellow"], C["green_dot"]]):
        cx = 22 + i * 22
        ET.SubElement(svg, "circle", {"cx": str(cx), "cy": "18", "r": "6", "fill": color})

    T(svg, cw // 2, 23, "~/huzaifa", C["text3"], sz=11, w="500", anc="middle", ff=FF_MONO)

    y0 = title_bar_h + pad

    # Prompt with faux glow
    glow_rect(svg, pad - 1, y0 - 12, 90, 18, C["green_prompt"], rx=2, opacity="0.1")
    T(svg, pad, y0, "$ whoami", C["green_prompt"], sz=13, w="600", ff=FF_MONO)
    y0 += lh + 6

    for key, val, val_color in lines:
        T(svg, pad + 10, y0, key + ":", C["text3"], sz=12, w="400", ff=FF_MONO)
        val_x = pad + 10 + max(len(key), 4) * 8.4 + 18
        T(svg, val_x, y0, val, val_color, sz=12, w="500", ff=FF_MONO)
        y0 += lh

    # Blinking prompt
    y0 += 4
    T(svg, pad, y0, "$ ", C["green_prompt"], sz=13, w="600", ff=FF_MONO)
    glow_rect(svg, pad + 18, y0 - 13, 10, 18, C["green_prompt"], rx=2, opacity="0.2")
    blink = ET.SubElement(svg, "rect", {
        "x": str(pad + 20), "y": str(y0 - 13), "width": "8", "height": "16",
        "rx": "1", "fill": C["green_prompt"]
    })
    ET.SubElement(blink, "animate", {
        "attributeName": "opacity", "values": "1;0;1",
        "dur": "1s", "repeatCount": "indefinite"
    })

    with open(out, "w") as f:
        f.write(svg_str(svg))
    print(f"  [+] {out}")


# ── Skill Spectrum ───────────────────────────────────────────
def gen_skills(config, out):
    skills = config.get("skills", {})
    all_skills = []
    for category, items in skills.items():
        for s in items:
            all_skills.append((s["name"], category, SKILL_COLORS.get(s["name"], C["accent"])))

    if not all_skills:
        return

    pill_w = 95
    pill_h = 28
    pill_gap = 8
    pills_per_row = 5
    rows = (len(all_skills) + pills_per_row - 1) // pills_per_row

    cw = pills_per_row * (pill_w + pill_gap) - pill_gap + 40
    ch = rows * (pill_h + pill_gap) - pill_gap + 60

    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg", "width": str(cw), "height": str(ch),
        "viewBox": f"0 0 {cw} {ch}", "role": "img", "aria-label": "Tech Stack",
    })

    defs = ET.SubElement(svg, "defs")
    add_gradient(defs, "skillGrad", [C["accent"], C["accent2"]])

    # Title
    T(svg, cw // 2, 28, "TECH STACK", C["text2"], sz=11, w="700", anc="middle", ff=FF_MONO)
    ET.SubElement(svg, "rect", {
        "x": str(cw // 2 - 45), "y": "34", "width": "90", "height": "2",
        "rx": "1", "fill": "url(#skillGrad)", "opacity": "0.6"
    })

    start_y = 50
    for i, (name, category, color) in enumerate(all_skills):
        row = i // pills_per_row
        col = i % pills_per_row
        x = 20 + col * (pill_w + pill_gap)
        y = start_y + row * (pill_h + pill_gap)

        # Pill with colored border
        R(svg, x, y, pill_w, pill_h, C["surface2"], rx=14, stroke=color, sw=1)

        # Color dot
        ET.SubElement(svg, "circle", {
            "cx": str(x + 14), "cy": str(y + pill_h // 2), "r": "4", "fill": color
        })

        # Skill name
        T(svg, x + 24, y + pill_h // 2 + 4, name, C["text"], sz=10, w="500", ff=FF_MONO)

    with open(out, "w") as f:
        f.write(svg_str(svg))
    print(f"  [+] {out}")


# ── GitHub Stats Card ───────────────────────────────────────
def gen_stats(data, config, out):
    user = data.get("user", {})
    stats = data.get("repo_stats", {})

    repos = user.get("public_repos", 0)
    stars = stats.get("total_stars", 0)
    followers = user.get("followers", 0)
    following = user.get("following", 0)
    is_empty = (repos + stars + followers + following) == 0

    cw = 580
    ch = 165 if not is_empty else 130
    pad = 24

    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg", "width": str(cw), "height": str(ch),
        "viewBox": f"0 0 {cw} {ch}", "role": "img", "aria-label": "GitHub statistics",
    })

    defs = ET.SubElement(svg, "defs")
    add_gradient(defs, "statGrad", [C["accent"], C["accent2"], C["purple"]])

    # Card background
    R(svg, 0, 0, cw, ch, C["surface"], rx=14, stroke=C["border"], sw=1)

    # Top gradient accent bar
    ET.SubElement(svg, "rect", {
        "x": "1", "y": "1", "width": str(cw - 2), "height": "3",
        "rx": "14", "fill": "url(#statGrad)"
    })

    if is_empty:
        # Faux glow behind icon
        ET.SubElement(svg, "ellipse", {
            "cx": str(pad + 15), "cy": "55", "rx": "30", "ry": "25",
            "fill": C["accent"], "opacity": "0.06"
        })
        T(svg, pad + 4, 60, "\u26A1", C["accent"], sz=30, w="400")
        T(svg, pad + 48, 58, "Just getting started", C["text"], sz=17, w="700")
        T(svg, pad, 84, "Stars, repos, and contributions will appear here as I build.",
          C["text2"], sz=12)
        T(svg, pad, 106, "Watch this space grow.", C["text3"], sz=11)
    else:
        T(svg, pad, 38, "GITHUB STATS", C["text2"], sz=11, w="700", ff=FF_MONO)

        metrics = [
            (str(repos), "Repositories", C["accent"]),
            (str(stars), "Stars", C["accent2"]),
            (str(followers), "Followers", C["purple"]),
            (str(following), "Following", C["pink"]),
        ]

        box_w = (cw - pad * 2 - 3 * 14) // 4
        for i, (val, label, color) in enumerate(metrics):
            x = pad + i * (box_w + 14)
            y = 55

            # Mini card
            R(svg, x, y, box_w, 85, C["bg"], rx=10, stroke=C["border"], sw=0.5)

            # Colored top accent
            ET.SubElement(svg, "rect", {
                "x": str(x + 1), "y": str(y + 1), "width": str(box_w - 2), "height": "3",
                "rx": "10", "fill": color, "opacity": "0.7"
            })

            # Faux glow behind value
            ET.SubElement(svg, "ellipse", {
                "cx": str(x + box_w // 2), "cy": str(y + 42),
                "rx": "25", "ry": "15", "fill": color, "opacity": "0.06"
            })

            # Value
            T(svg, x + box_w // 2, y + 48, val, color, sz=28, w="700", anc="middle")

            # Label
            T(svg, x + box_w // 2, y + 70, label, C["text2"], sz=10,
              w="500", anc="middle", ff=FF_MONO)

    with open(out, "w") as f:
        f.write(svg_str(svg))
    print(f"  [+] {out}")


# ── Languages Card ──────────────────────────────────────────
def gen_languages(data, out):
    languages = data.get("repo_stats", {}).get("languages", [])

    cw = 580
    pad = 24
    title_area = 48
    bottom_pad = 20
    row_h = 36

    if not languages:
        ch = title_area + 55 + bottom_pad
        svg = ET.Element("svg", {
            "xmlns": "http://www.w3.org/2000/svg", "width": str(cw), "height": str(ch),
            "viewBox": f"0 0 {cw} {ch}", "role": "img", "aria-label": "Top languages",
        })
        R(svg, 0, 0, cw, ch, C["surface"], rx=14, stroke=C["border"], sw=1)
        T(svg, pad, 32, "TOP LANGUAGES", C["text2"], sz=11, w="700", ff=FF_MONO)
        ET.SubElement(svg, "rect", {
            "x": str(pad), "y": "38", "width": "110", "height": "2",
            "rx": "1", "fill": C["accent"], "opacity": "0.4"
        })
        T(svg, cw // 2, title_area + 35,
          "Push some code and your languages will show up here",
          C["text3"], sz=11, anc="middle")
        with open(out, "w") as f:
            f.write(svg_str(svg))
        print(f"  [+] {out} (empty)")
        return

    languages = languages[:6]
    ch = title_area + len(languages) * row_h + bottom_pad

    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg", "width": str(cw), "height": str(ch),
        "viewBox": f"0 0 {cw} {ch}", "role": "img", "aria-label": "Top languages",
    })

    R(svg, 0, 0, cw, ch, C["surface"], rx=14, stroke=C["border"], sw=1)

    # Title
    T(svg, pad, 32, "TOP LANGUAGES", C["text2"], sz=11, w="700", ff=FF_MONO)
    ET.SubElement(svg, "rect", {
        "x": str(pad), "y": "38", "width": "110", "height": "2",
        "rx": "1", "fill": C["accent"], "opacity": "0.4"
    })

    label_w = 105
    pct_w = 48
    bar_area = cw - pad * 2 - label_w - pct_w - 16
    max_pct = max(l["percentage"] for l in languages) or 1

    for i, lang in enumerate(languages):
        y = title_area + i * row_h
        color = LANG_COLORS.get(lang["name"], C["accent"])

        T(svg, pad, y + 22, lang["name"], C["text"], sz=12, w="500")

        bar_x = pad + label_w
        R(svg, bar_x, y + 12, bar_area, 12, C["bg"], rx=6, stroke=C["border"], sw=0.5)

        fill_w = max((lang["percentage"] / max_pct) * bar_area, 8) if max_pct > 0 else 8
        # Faux glow behind bar
        ET.SubElement(svg, "rect", {
            "x": str(bar_x - 2), "y": str(y + 10),
            "width": str(fill_w + 4), "height": "16",
            "rx": "8", "fill": color, "opacity": "0.12"
        })
        R(svg, bar_x, y + 12, fill_w, 12, color, rx=6)

        # Shimmer
        shimmer = ET.SubElement(svg, "rect", {
            "x": str(bar_x), "y": str(y + 12), "width": str(fill_w), "height": "12",
            "rx": "6", "fill": "white", "opacity": "0"
        })
        ET.SubElement(shimmer, "animate", {
            "attributeName": "opacity", "values": "0;0.12;0",
            "dur": f"{2 + i * 0.3}s", "repeatCount": "indefinite"
        })

        T(svg, cw - pad, y + 22, f'{lang["percentage"]}%',
          C["text2"], sz=11, w="600", anc="middle", ff=FF_MONO)

    with open(out, "w") as f:
        f.write(svg_str(svg))
    print(f"  [+] {out}")


# ── Activity Card ───────────────────────────────────────────
def gen_activity(data, out):
    weeks = data.get("activity", [])
    while len(weeks) < 12:
        weeks.append({"label": "", "count": 0})
    weeks = weeks[:12]

    cw = 580
    pad = 24
    title_area = 48
    bottom_pad = 30
    bar_max_h = 80
    bar_w = 28
    bar_gap = 12

    bars_w = 12 * bar_w + 11 * bar_gap
    start_x = (cw - bars_w) // 2
    max_count = max((w["count"] for w in weeks), default=1) or 1
    ch = title_area + bar_max_h + bottom_pad

    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg", "width": str(cw), "height": str(ch),
        "viewBox": f"0 0 {cw} {ch}", "role": "img", "aria-label": "Contribution activity",
    })

    defs = ET.SubElement(svg, "defs")
    add_gradient(defs, "barGrad", [C["accent"], C["accent2"]])

    R(svg, 0, 0, cw, ch, C["surface"], rx=14, stroke=C["border"], sw=1)

    T(svg, pad, 32, "RECENT ACTIVITY", C["text2"], sz=11, w="700", ff=FF_MONO)
    ET.SubElement(svg, "rect", {
        "x": str(pad), "y": "38", "width": "120", "height": "2",
        "rx": "1", "fill": C["accent"], "opacity": "0.4"
    })

    for i, week in enumerate(weeks):
        x = start_x + i * (bar_w + bar_gap)
        count = week["count"]
        bh = max((count / max_count) * bar_max_h, 4) if max_count > 0 else 4
        y = title_area + bar_max_h - bh

        # Faux glow behind bar
        ET.SubElement(svg, "rect", {
            "x": str(x - 3), "y": str(y - 3),
            "width": str(bar_w + 6), "height": str(bh + 6),
            "rx": "9", "fill": C["accent"], "opacity": "0.08"
        })

        # Bar with gradient
        R(svg, x, y, bar_w, bh, "url(#barGrad)", rx=6)

        if count > 0:
            # Pulse
            bar_g = ET.SubElement(svg, "rect", {
                "x": str(x), "y": str(y), "width": str(bar_w), "height": str(bh),
                "rx": "6", "fill": "white", "opacity": "0"
            })
            ET.SubElement(bar_g, "animate", {
                "attributeName": "opacity", "values": "0;0.1;0",
                "dur": f"{2 + i * 0.2}s", "repeatCount": "indefinite"
            })
            T(svg, x + bar_w // 2, y - 6, str(count),
              C["accent2"], sz=9, w="700", anc="middle", ff=FF_MONO)

        label = week.get("label", "")
        if label:
            T(svg, x + bar_w // 2, title_area + bar_max_h + 18, label,
              C["text3"], sz=8, w="400", anc="middle")

    with open(out, "w") as f:
        f.write(svg_str(svg))
    print(f"  [+] {out}")


# ── Wave Divider ─────────────────────────────────────────────
def gen_wave(out):
    w, h = 900, 30

    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg", "width": str(w), "height": str(h),
        "viewBox": f"0 0 {w} {h}", "role": "img", "aria-label": "", "aria-hidden": "true",
    })

    defs = ET.SubElement(svg, "defs")
    add_gradient(defs, "waveLine", ["#00f5a000", C["accent"], C["accent2"], "#00f5a000"])

    # Main wave
    points = []
    for x_i in range(0, w + 1, 3):
        y_val = h // 2 + math.sin(x_i * 0.015) * 5 + math.sin(x_i * 0.04) * 3
        points.append(f"{x_i},{y_val:.1f}")
    path_d = "M " + " L ".join(points)
    ET.SubElement(svg, "path", {
        "d": path_d, "fill": "none", "stroke": "url(#waveLine)",
        "stroke-width": "1.5", "stroke-linecap": "round"
    })

    # Secondary subtle wave
    points2 = []
    for x_i in range(0, w + 1, 3):
        y_val = h // 2 + math.sin(x_i * 0.012 + 2) * 3 + math.sin(x_i * 0.035 + 1) * 2
        points2.append(f"{x_i},{y_val:.1f}")
    path2_d = "M " + " L ".join(points2)
    ET.SubElement(svg, "path", {
        "d": path2_d, "fill": "none", "stroke": "url(#waveLine)",
        "stroke-width": "0.8", "stroke-linecap": "round", "opacity": "0.3"
    })

    with open(out, "w") as f:
        f.write(svg_str(svg))
    print(f"  [+] {out}")


# ── Avatar Frame ────────────────────────────────────────────
def gen_avatar_frame(config, out):
    """Avatar frame with embedded photo and animated gradient ring."""
    avatar_url = config.get("avatar_url", "")
    size = 150
    cx, cy = size // 2, size // 2
    r_outer = 72
    r_inner = 62

    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "xmlns:xlink": "http://www.w3.org/1999/xlink",
        "width": str(size), "height": str(size),
        "viewBox": f"0 0 {size} {size}",
        "role": "img", "aria-label": "Avatar",
    })

    defs = ET.SubElement(svg, "defs")
    add_gradient(defs, "frameGrad", [C["accent"], C["accent2"], C["purple"], C["accent"]])

    # Clip path for circular avatar
    clip = ET.SubElement(defs, "clipPath", {"id": "avatarClip"})
    ET.SubElement(clip, "circle", {"cx": str(cx), "cy": str(cy), "r": str(r_inner - 2)})

    # Outer glow
    ET.SubElement(svg, "circle", {
        "cx": str(cx), "cy": str(cy), "r": str(r_outer + 5),
        "fill": "none", "stroke": C["accent"], "stroke-width": "1", "opacity": "0.12"
    })

    # Animated rotating gradient ring
    ring = ET.SubElement(svg, "circle", {
        "cx": str(cx), "cy": str(cy), "r": str(r_outer),
        "fill": "none", "stroke": "url(#frameGrad)",
        "stroke-width": "3", "stroke-linecap": "round",
    })
    circumference = 2 * math.pi * r_outer
    ring.set("stroke-dasharray", f"{circumference * 0.25} {circumference * 0.75}")
    ET.SubElement(ring, "animate", {
        "attributeName": "stroke-dashoffset",
        "values": f"0;-{circumference}",
        "dur": "4s", "repeatCount": "indefinite"
    })

    # Second ring rotating opposite
    ring2 = ET.SubElement(svg, "circle", {
        "cx": str(cx), "cy": str(cy), "r": str(r_outer + 3),
        "fill": "none", "stroke": C["accent2"],
        "stroke-width": "1", "stroke-linecap": "round", "opacity": "0.3",
    })
    ring2.set("stroke-dasharray", f"{circumference * 0.15} {circumference * 0.85}")
    ET.SubElement(ring2, "animate", {
        "attributeName": "stroke-dashoffset",
        "values": f"0;{circumference}",
        "dur": "6s", "repeatCount": "indefinite"
    })

    # Inner border ring
    ET.SubElement(svg, "circle", {
        "cx": str(cx), "cy": str(cy), "r": str(r_inner),
        "fill": "none", "stroke": C["border"], "stroke-width": "1.5"
    })

    # Avatar image (clipped to circle)
    if avatar_url:
        ET.SubElement(svg, "image", {
            "xlink:href": avatar_url,
            "x": str(cx - r_inner + 2), "y": str(cy - r_inner + 2),
            "width": str((r_inner - 2) * 2), "height": str((r_inner - 2) * 2),
            "clip-path": "url(#avatarClip)",
            "preserveAspectRatio": "xMidYMid slice",
        })

    # 4 accent dots at cardinal points
    for i, angle_deg in enumerate([0, 90, 180, 270]):
        rad = math.radians(angle_deg)
        ax = cx + (r_outer + 1) * math.cos(rad)
        ay = cy + (r_outer + 1) * math.sin(rad)
        color = [C["accent"], C["accent2"], C["purple"], C["pink"]][i]
        dot = ET.SubElement(svg, "circle", {
            "cx": str(ax), "cy": str(ay), "r": "3", "fill": color
        })
        ET.SubElement(dot, "animate", {
            "attributeName": "r", "values": "2.5;4;2.5",
            "dur": "2s", "repeatCount": "indefinite"
        })
        ET.SubElement(dot, "animate", {
            "attributeName": "opacity", "values": "0.6;1;0.6",
            "dur": "2s", "repeatCount": "indefinite"
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

    print("[*] Generating SVG assets (GitHub-safe Neon Dark v2)...")
    gen_avatar_frame(config, os.path.join(assets_dir, "avatar-frame.svg"))
    gen_banner(config, os.path.join(assets_dir, "banner.svg"))
    gen_typing(config, os.path.join(assets_dir, "typing-card.svg"))
    gen_terminal(config, os.path.join(assets_dir, "terminal-card.svg"))
    gen_skills(config, os.path.join(assets_dir, "skills.svg"))
    gen_stats(data, config, os.path.join(assets_dir, "github-stats.svg"))
    gen_languages(data, os.path.join(assets_dir, "languages.svg"))
    gen_activity(data, os.path.join(assets_dir, "activity.svg"))
    gen_wave(os.path.join(assets_dir, "wave-divider.svg"))
    print("[+] All assets generated.")


if __name__ == "__main__":
    main()
