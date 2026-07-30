"""
generate_snake.py

Generates a decorative animated "snake" SVG for a GitHub profile README.

Note: this is a *decorative* moving-snake animation (a snake slithering
along a wavy path with a pulsing trail), not a snake that solves/eats
your real contribution graph. That specific effect (a snake literally
eating each contribution square) is normally produced by the
Platane/snk GitHub Action, which isn't Python-based. This script is a
from-scratch Python alternative that gives a similar "something is
alive on my profile" effect without depending on that action.

Usage:
    python scripts/generate_snake.py [--out assets/snake.svg] [--color 6DB33F]

Output is a single self-contained SVG using SMIL <animateMotion>, which
renders its animation even when embedded via <img src="..."> in a
README (GitHub serves the raw SVG file and the browser animates it).
"""

import argparse
import os

WIDTH = 800
HEIGHT = 120
SEGMENTS = 12          # number of body segments
SEGMENT_R = 8           # radius of each segment
DURATION = 6            # seconds for one full lap
STAGGER = 0.08          # seconds of delay between segments


def build_path() -> str:
    """A gentle wavy path the snake will travel along, left to right and back."""
    return (
        f"M -20,{HEIGHT/2} "
        f"C {WIDTH*0.2},{HEIGHT*0.1} {WIDTH*0.3},{HEIGHT*0.9} {WIDTH*0.5},{HEIGHT/2} "
        f"S {WIDTH*0.8},{HEIGHT*0.1} {WIDTH+20},{HEIGHT/2} "
        f"S {WIDTH*0.5},{HEIGHT*0.9} {WIDTH*0.2},{HEIGHT/2} "
        f"S -20,{HEIGHT/2} -20,{HEIGHT/2}"
    )


def build_segment(index: int, color: str, path_id: str) -> str:
    """One circle following the path with a per-segment time offset,
    so the body trails behind the head."""
    begin_offset = f"-{index * STAGGER}s"
    opacity = max(0.25, 1 - index * (0.6 / SEGMENTS))
    radius = SEGMENT_R * max(0.4, 1 - index * (0.5 / SEGMENTS))
    return f"""
    <circle r="{radius:.1f}" fill="{color}" opacity="{opacity:.2f}">
      <animateMotion dur="{DURATION}s" repeatCount="indefinite" begin="{begin_offset}" rotate="auto">
        <mpath xlink:href="#{path_id}"/>
      </animateMotion>
    </circle>"""


def build_svg(color: str) -> str:
    path_id = "snakePath"
    path_d = build_path()
    segments = "\n".join(build_segment(i, color, path_id) for i in range(SEGMENTS))

    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="{HEIGHT}">
  <defs>
    <path id="{path_id}" d="{path_d}" fill="none"/>
    <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"  stop-color="{color}" stop-opacity="0"/>
      <stop offset="10%" stop-color="{color}" stop-opacity="0.15"/>
      <stop offset="90%" stop-color="{color}" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="{color}" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <path d="{path_d}" fill="none" stroke="url(#fade)" stroke-width="2"/>
  {segments}
</svg>"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="assets/snake.svg")
    parser.add_argument("--color", default="6DB33F", help="hex color, no leading #")
    args = parser.parse_args()

    svg = build_svg(f"#{args.color}")
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
