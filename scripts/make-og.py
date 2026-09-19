#!/usr/bin/env python3
"""Compose Sky Instrument og:{word}.jpg — 1200x630 sky + paper bar + mono caption.

Usage:
  python3 make-og.py --sky virga.jpg --time 16:03 --word virga --out og-virga.jpg

Requires: Pillow (pip install pillow)
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H = 1200, 630
BAR_H = 96
PAPER = (243, 241, 236)  # #f3f1ec
INK = (22, 22, 22)  # #161616
PAD_X = 40


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/ibm-plex/IBMPlexMono-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "C:/Windows/Fonts/consola.ttf",
    ]
    for path in candidates:
        p = Path(path)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def main() -> None:
    ap = argparse.ArgumentParser(description="Sky Instrument OG card composer")
    ap.add_argument("--sky", required=True, help="Path to sky JPG")
    ap.add_argument("--time", required=True, help="HH:MM")
    ap.add_argument("--word", required=True, help="lowercase state word")
    ap.add_argument("--out", required=True, help="Output og JPG path")
    args = ap.parse_args()

    sky = Image.open(args.sky).convert("RGB")
    sky_h = H - BAR_H
    # Cover-crop into the sky band
    scale = max(W / sky.width, sky_h / sky.height)
    nw, nh = int(sky.width * scale), int(sky.height * scale)
    sky = sky.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - sky_h) // 2
    sky = sky.crop((left, top, left + W, top + sky_h))

    canvas = Image.new("RGB", (W, H), PAPER)
    canvas.paste(sky, (0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, sky_h, W, H), fill=PAPER)

    caption = f"{args.time} {args.word.lower()}"
    font = load_font(28)
    draw.text((PAD_X, sky_h + (BAR_H - 28) // 2 - 2), caption, fill=INK, font=font)

    out = Path(args.out)
    canvas.save(out, format="JPEG", quality=90, optimize=True)
    print(f"wrote {out} ({W}x{H})")


if __name__ == "__main__":
    main()
