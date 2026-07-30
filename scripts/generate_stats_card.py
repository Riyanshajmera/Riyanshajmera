"""
generate_stats_card.py

Builds a self-contained, animated "skills" SVG card for a GitHub profile
README: each skill bar animates from 0 to its proficiency width on load
using SMIL <animate>, which still plays when the SVG is embedded via
<img src="..."> in a README.

Usage:
    python scripts/generate_stats_card.py [--out assets/stats-card.svg]
"""

import argparse
import os

WIDTH = 460
BAR_HEIGHT = 10
ROW_GAP = 34
PADDING_TOP = 56
PADDING_X = 24
BG = "#0d1117"
TEXT = "#c9d1d9"
TRACK = "#21262d"

# (skill label, proficiency 0-100, bar color)
SKILLS = [
    ("Java",        88, "#ED8B00"),
    ("Spring Boot", 85, "#6DB33F"),
    ("React.js",    75, "#61DAFB"),
    ("JavaScript",  78, "#F7DF1E"),
    ("SQL / DBMS",  80, "#4479A1"),
    ("Docker / K8s",65, "#2496ED"),
]


def bar_row(index: int, label: str, pct: int, color: str) -> str:
    y = PADDING_TOP + index * ROW_GAP
    bar_w = WIDTH - PADDING_X * 2
    target_w = bar_w * pct / 100
    delay = f"{index * 0.12:.2f}s"

    return f"""
  <text x="{PADDING_X}" y="{y - 6}" fill="{TEXT}" font-family="Segoe UI, Helvetica, sans-serif" font-size="13">{label}</text>
  <text x="{PADDING_X + bar_w}" y="{y - 6}" fill="{TEXT}" font-family="Segoe UI, Helvetica, sans-serif" font-size="12" text-anchor="end" opacity="0.7">{pct}%</text>
  <rect x="{PADDING_X}" y="{y}" width="{bar_w}" height="{BAR_HEIGHT}" rx="{BAR_HEIGHT/2}" fill="{TRACK}"/>
  <rect x="{PADDING_X}" y="{y}" width="0" height="{BAR_HEIGHT}" rx="{BAR_HEIGHT/2}" fill="{color}">
    <animate attributeName="width" from="0" to="{target_w:.1f}" dur="1.1s" begin="{delay}" fill="freeze" calcMode="spline" keySplines="0.25 0.1 0.25 1"/>
  </rect>"""


def build_svg() -> str:
    height = PADDING_TOP + len(SKILLS) * ROW_GAP + 16
    rows = "\n".join(
        bar_row(i, label, pct, color) for i, (label, pct, color) in enumerate(SKILLS)
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <rect width="{WIDTH}" height="{height}" rx="12" fill="{BG}"/>
  <text x="{PADDING_X}" y="28" fill="{TEXT}" font-family="Segoe UI, Helvetica, sans-serif" font-size="16" font-weight="600">
    Riyansh's Core Skills
    <animate attributeName="opacity" from="0" to="1" dur="0.6s" fill="freeze"/>
  </text>
  {rows}
</svg>"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="assets/stats-card.svg")
    args = parser.parse_args()

    svg = build_svg()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
