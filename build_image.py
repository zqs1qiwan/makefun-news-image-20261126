#!/usr/bin/env python3
"""Rebuild the front page for news-image-20261126 (post-opening session).

The page is a 1024x1024 newspaper front page, typeset entirely in PIL
on top of six photographs cut from one fresh AI-generated 3x2 collage
(assets/entry-source-20261126-fresh.png, generated in this session).

Sections, top to bottom:
  * masthead — title, red rule, exact date
  * four story panels in a 2x2 grid (photo + kicker + headline + subhead)
  * a full-width strip holding the last two big stories (thumb + text)
  * a navy ALSO band with three short items

Running this file writes entry.png next to it and then re-opens the
file to check it: 1024x1024, PNG, at most 1 MiB. The build is fully
deterministic — same input bytes, same output bytes.
"""
from __future__ import annotations

import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(BASE, "assets", "entry-source-20261126-fresh.png")
TARGET = os.path.join(BASE, "entry.png")

PAGE_W, PAGE_H = 1024, 1024
MARGIN = 16

# Palette
PAPER = (247, 242, 231)
INK = (18, 18, 18)
RULE_RED = (178, 34, 34)
MUTED = (90, 88, 82)
NAVY = (20, 36, 62)
GOLD = (232, 190, 90)
OFFWHITE = (245, 245, 245)
PHOTO_EDGE = (40, 40, 40)

NOTO = "/usr/share/fonts/truetype/noto"
FONTS = {
    "cond": os.path.join(NOTO, "NotoSans-Condensed.ttf"),
    "cond_bold": os.path.join(NOTO, "NotoSans-CondensedBold.ttf"),
    "regular": os.path.join(NOTO, "NotoSans-Regular.ttf"),
}


def load(kind: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONTS[kind], size)


def wrap_text(draw: ImageDraw.ImageDraw, text: str,
              font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    """Split text into lines that each fit inside width pixels."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_headline(draw: ImageDraw.ImageDraw, text: str, start: int,
                 width: int, max_lines: int = 2) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    """Largest bold-condensed size (<= start) wrapping into max_lines."""
    size = start
    while size > 13:
        fnt = load("cond_bold", size)
        lines = wrap_text(draw, text, fnt, width)
        if len(lines) <= max_lines:
            return fnt, lines
        size -= 1
    fnt = load("cond_bold", 13)
    return fnt, wrap_text(draw, text, fnt, width)


def cover_fill(img: Image.Image, focus: tuple[float, float],
               tw: int, th: int) -> Image.Image:
    """Resize-crop img to exactly tw x th, keeping focus in frame."""
    w, h = img.size
    scale = max(tw / w, th / h)
    cw, ch = round(tw / scale), round(th / scale)
    cx, cy = round(focus[0] * w), round(focus[1] * h)
    x0 = min(max(cx - cw // 2, 0), w - cw)
    y0 = min(max(cy - ch // 2, 0), h - ch)
    return img.crop((x0, y0, x0 + cw, y0 + ch)).resize((tw, th), Image.LANCZOS)


# Cell rectangles measured from the fresh collage (1920x1280): the grey
# frame is ~10px and the gutters sit near x=636-650, x=1272-1284 and
# y=645-656, so each cell is inset a few px past the frame/gutter.
CELLS = {
    "tanker": (16, 16, 630, 639),
    "refinery": (656, 16, 1266, 639),
    "space": (1290, 16, 1904, 639),
    "cemetery": (16, 662, 630, 1264),
    "port": (656, 662, 1266, 1264),
    "island": (1290, 662, 1904, 1264),
}
FOCUS = {
    "tanker": (0.50, 0.62),
    "refinery": (0.50, 0.50),
    "space": (0.55, 0.50),
    "cemetery": (0.50, 0.60),
    "port": (0.50, 0.55),
    "island": (0.50, 0.60),
}

GRID_STORIES = [
    {"cell": "tanker", "kicker": "MIDDLE EAST",
     "head": "TANKERS ABLAZE IN HORMUZ",
     "sub": "Two tankers hit mines and burn in the strait"},
    {"cell": "refinery", "kicker": "SAUDI ARABIA",
     "head": "REFINERY HIT IN SAUDI ARABIA",
     "sub": "Houthis claim strike; four drones shot down"},
    {"cell": "space", "kicker": "SPACE",
     "head": "PAKISTAN'S FIRST ASTRONAUT IN ORBIT",
     "sub": "First foreigner aboard China's Tiangong station"},
    {"cell": "cemetery", "kicker": "UKRAINE WAR",
     "head": "RUSSIA'S DEAD: NEARLY 500,000",
     "sub": "Leaked files put the toll at 490,334"},
]
STRIP_STORIES = [
    {"cell": "port", "kicker": "TRADE",
     "head": "US READIES NEW TARIFFS",
     "sub": "Duties planned on China, the EU and 15 others"},
    {"cell": "island", "kicker": "PACIFIC",
     "head": "PACIFIC PACT SHUTS OUT BASES",
     "sub": "Solomons sign treaty with Australia"},
]
ALSO_ITEMS = [
    "CARTAGENA HOSTAGES FREED \u2014 troops storm the store at dawn",
    "CAIRO TANKER FIRE KILLS AT LEAST 31 \u2014 ring road blaze engulfs 27 vehicles",
    "KILMAR \u00c1BREGO GARC\u00cdA LEAVES THE US FOR SPAIN",
]

DATE_LINE = "THURSDAY, 26 NOVEMBER 2026"


def draw_masthead(draw: ImageDraw.ImageDraw) -> None:
    draw.text((PAGE_W // 2, 12), "THE WORLD IN ONE DAY",
              font=load("cond_bold", 62), fill=INK, anchor="ma")
    draw.rectangle((MARGIN, 96, PAGE_W - MARGIN, 99), fill=RULE_RED)
    draw.text((PAGE_W // 2, 104), DATE_LINE,
              font=load("cond_bold", 27), fill=INK, anchor="ma")


def draw_grid(page: Image.Image, draw: ImageDraw.ImageDraw,
              src: Image.Image) -> None:
    panel_w, panel_h, photo_h = 490, 300, 170
    cols_x = [MARGIN, 526]
    rows_y = [140, 452]
    for idx, story in enumerate(GRID_STORIES):
        x = cols_x[idx % 2]
        y = rows_y[idx // 2]
        x0, y0, x1, y1 = CELLS[story["cell"]]
        cell = src.crop((x0, y0, x1, y1))
        photo = cover_fill(cell, FOCUS[story["cell"]], panel_w, photo_h)
        page.paste(photo, (x, y))
        draw.rectangle((x, y, x + panel_w - 1, y + photo_h - 1),
                       outline=PHOTO_EDGE, width=1)
        ty = y + photo_h + 8
        draw.text((x, ty), story["kicker"], font=load("cond_bold", 19),
                  fill=RULE_RED)
        ty += 24
        head_font, head_lines = fit_headline(draw, story["head"], 36, panel_w)
        for line in head_lines:
            draw.text((x, ty), line, font=head_font, fill=INK)
            ty += head_font.size + 2
        draw.text((x, ty), story["sub"], font=load("cond", 23), fill=MUTED)


def draw_strip(page: Image.Image, draw: ImageDraw.ImageDraw,
               src: Image.Image) -> None:
    top, height, thumb_w = 764, 116, 150
    for idx, story in enumerate(STRIP_STORIES):
        x = MARGIN if idx == 0 else 526
        x0, y0, x1, y1 = CELLS[story["cell"]]
        cell = src.crop((x0, y0, x1, y1))
        thumb = cover_fill(cell, FOCUS[story["cell"]], thumb_w, height)
        page.paste(thumb, (x, top))
        draw.rectangle((x, top, x + thumb_w - 1, top + height - 1),
                       outline=PHOTO_EDGE, width=1)
        tx = x + thumb_w + 12
        text_w = 490 - thumb_w - 12
        draw.text((tx, top + 2), story["kicker"], font=load("cond_bold", 18),
                  fill=RULE_RED)
        head_font, head_lines = fit_headline(draw, story["head"], 30, text_w)
        ty = top + 24
        for line in head_lines:
            draw.text((tx, ty), line, font=head_font, fill=INK)
            ty += head_font.size + 1
        sub_font = load("cond", 18)
        # Both strip subs now fit on one line at 18px (the tariff sub used
        # to strand a lone "others" on line two at 20px); the two-line
        # cap below stays as a safety net.
        for line in wrap_text(draw, story["sub"], sub_font, text_w)[:2]:
            draw.text((tx, ty + 2), line, font=sub_font, fill=MUTED)
            ty += sub_font.size + 1


def draw_also_band(draw: ImageDraw.ImageDraw) -> None:
    top = 892
    draw.rectangle((0, top, PAGE_W, PAGE_H), fill=NAVY)
    draw.text((MARGIN, top + 6), "ALSO TODAY", font=load("cond_bold", 22),
              fill=GOLD)
    y = top + 34
    for item in ALSO_ITEMS:
        size = 28
        while size > 19:
            fnt = load("cond", size)
            if draw.textlength(item, font=fnt) <= PAGE_W - 34 - MARGIN:
                break
            size -= 1
        draw.rectangle((MARGIN, y + 9, MARGIN + 8, y + 17), fill=RULE_RED)
        draw.text((34, y), item, font=fnt, fill=OFFWHITE)
        y += 31


def render() -> None:
    src = Image.open(SOURCE).convert("RGB")
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(page)
    draw_masthead(draw)
    draw_grid(page, draw, src)
    draw_strip(page, draw, src)
    draw_also_band(draw)
    page.save(TARGET, "PNG", optimize=True)
    print("wrote", TARGET)


def verify() -> str:
    with Image.open(TARGET) as im:
        assert im.size == (PAGE_W, PAGE_H), im.size
        assert im.format == "PNG"
    nbytes = os.path.getsize(TARGET)
    assert nbytes <= 1_048_576, nbytes
    digest = hashlib.sha256(open(TARGET, "rb").read()).hexdigest()
    print(f"verify: 1024x1024 PNG, {nbytes} bytes, sha256 {digest}")
    return digest


if __name__ == "__main__":
    render()
    verify()
