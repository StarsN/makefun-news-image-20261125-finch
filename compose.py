#!/usr/bin/env python3
"""Compose the news-image-20261125 front page: one 1024x1024 PNG.

Draws a newspaper front page for Wednesday 25 November 2026 with PIL:
masthead, dateline, a lead story with a night photo of Kyiv, two
picture stories (tariffs, Riyadh), two text stories (Huawei, Colombia),
a briefs strip and a sources footer. All copy is written here; the three
scene photos live in assets/ and are centre-cropped into their frames.

Deterministic: same inputs always produce the same bytes.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
OUT = HERE / "entry.png"

PAGE = 1024
MARGIN = 30
CONTENT_RIGHT = PAGE - MARGIN
CONTENT_W = CONTENT_RIGHT - MARGIN

PAPER = (248, 243, 232)
INK = (26, 26, 26)
RED = (172, 32, 28)
GREY = (96, 90, 80)
RULE = (26, 26, 26)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, width: int) -> list[str]:
    """Greedy word wrap; returns lines that fit inside `width` pixels."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=fnt) <= width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def para(draw: ImageDraw.ImageDraw, text: str, fnt, x: int, y: int,
         width: int, leading: int, fill=INK) -> int:
    """Draw a wrapped paragraph; return the y just below its last line."""
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def headline(draw: ImageDraw.ImageDraw, lines: list[str], fnt,
             x: int, y: int, leading: int, fill=INK) -> int:
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rule(draw: ImageDraw.ImageDraw, y: int, weight: int = 2) -> None:
    draw.line([(MARGIN, y), (CONTENT_RIGHT, y)], fill=RULE, width=weight)


def photo(draw: ImageDraw.ImageDraw, page: Image.Image, name: str,
          box: tuple[int, int, int, int], focus: tuple[float, float]) -> None:
    """Centre-crop `name` into `box` (x, y, w, h) and paste it."""
    x, y, w, h = box
    with Image.open(ASSETS / name) as src:
        fitted = ImageOps.fit(src.convert("RGB"), (w, h),
                              method=Image.LANCZOS, centering=focus)
        page.paste(fitted, (x, y))
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=1)


def build() -> Image.Image:
    page = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(page)

    # ---- Masthead -------------------------------------------------------
    mast = font(SERIF_BOLD, 80)
    title = "THE WORLD"
    tw = draw.textlength(title, font=mast)
    draw.text(((PAGE - tw) / 2, 14), title, font=mast, fill=INK)
    rule(draw, 108, 2)

    # ---- Dateline -------------------------------------------------------
    date_font = font(SANS_BOLD, 19)
    dateline = "WEDNESDAY, 25 NOVEMBER 2026  \u2022  ONE DAY IN PICTURES"
    dw = draw.textlength(dateline, font=date_font)
    draw.text(((PAGE - dw) / 2, 118), dateline, font=date_font, fill=INK)
    rule(draw, 148, 2)

    # ---- Lead story: Kyiv ----------------------------------------------
    left_x = MARGIN
    left_w = 410
    img_x = 455
    img_w = CONTENT_RIGHT - img_x  # 539
    lead_top = 158

    kicker = font(SANS_BOLD, 18)
    draw.text((left_x, lead_top), "UKRAINE", font=kicker, fill=RED)

    lead_head = font(SERIF_BOLD, 50)
    y = headline(draw, ["MISSILES RAIN", "ON KYIV"], lead_head,
                 left_x, lead_top + 24, 50)
    body = font(SANS, 17)
    y = para(draw,
             "Russian forces hit Kyiv with ballistic missiles late on "
             "Wednesday, striking two sites in the city.",
             body, left_x, y + 10, left_w, 22)
    y = para(draw,
             "An overnight attack on energy and gas sites cut power in "
             "five regions and halted a thermal power plant.",
             body, left_x, y + 6, left_w, 22)

    photo(draw, page, "media-generation-kyiv-night-missiles-0-"
          "afb16ca5-6d7f-40af-8e69-69733eb173d2.webp",
          (img_x, lead_top, img_w, 250), (0.5, 0.45))
    caption = font(SERIF_ITALIC, 14)
    para(draw,
         "Kyiv at night. Russian ballistic missiles struck two sites in "
         "the capital, the mayor said.",
         caption, img_x, lead_top + 256, img_w, 18, fill=GREY)

    rule(draw, 450, 2)

    # ---- Middle row: two picture stories --------------------------------
    mid_top = 460
    mid_img_h = 110
    col_w = 462
    gap = 32
    right_x = MARGIN + col_w + gap  # 524

    photo(draw, page, "media-generation-tariffs-container-ship-0-"
          "702e352e-0331-4ce8-9d68-549c4ebc0e6e.webp",
          (MARGIN, mid_top, col_w, mid_img_h), (0.5, 0.5))
    photo(draw, page, "media-generation-riyadh-tower-smoke-0-"
          "46061971-cc78-4f98-9d07-3ac6f55ff2f7.webp",
          (right_x, mid_top, col_w, mid_img_h), (0.5, 0.5))

    mid_head = font(SERIF_BOLD, 28)
    mid_body = font(SANS, 16)
    hy = mid_top + mid_img_h + 8
    headline(draw, ["NEW TARIFFS", "ON 14 NATIONS"], mid_head,
             MARGIN, hy, 28)
    headline(draw, ["DRONE HITS", "RIYADH TOWER"], mid_head,
             right_x, hy, 28)
    by = hy + 56 + 6
    para(draw,
         "The US proposed new tariffs on 14 trading partners to fight "
         "excess factory capacity \u2014 up to 20% on China, 15% on the "
         "EU \u2014 as markets slid worldwide.",
         mid_body, MARGIN, by, col_w, 21)
    para(draw,
         "A Houthi drone struck a tower in Riyadh\u2019s financial "
         "district, wounding 11 people \u2014 the second strike on the "
         "capital\u2019s tallest tower in less than a week.",
         mid_body, right_x, by, col_w, 21)

    rule(draw, 716, 1)

    # ---- Bottom row: two text stories ------------------------------------
    bot_top = 726
    bot_head = font(SERIF_BOLD, 24)
    bot_body = font(SANS, 16)
    headline(draw, ["HUAWEI GUILTY ON", "10 OF 12 COUNTS"], bot_head,
             MARGIN, bot_top, 24)
    headline(draw, ["COLOMBIA: HOSTAGES", "FREED AFTER SIEGE"], bot_head,
             right_x, bot_top, 24)
    by2 = bot_top + 48 + 6
    para(draw,
         "A Brooklyn jury convicted Huawei of bank fraud, wire fraud "
         "and sanctions violations, but acquitted it of racketeering "
         "conspiracy.",
         bot_body, MARGIN, by2, col_w, 22)
    para(draw,
         "Twenty-five hostages were freed in Cartagena after a 17-hour "
         "supermarket siege; one captor was killed.",
         bot_body, right_x, by2, col_w, 22)

    rule(draw, 858, 2)

    # ---- Briefs strip ------------------------------------------------------
    brief_head = font(SANS_BOLD, 17)
    draw.text((MARGIN, 866), "ALSO TODAY", font=brief_head, fill=RED)
    brief = font(SANS, 14)
    briefs = [
        "NIGERIA: Suspected militants killed at least 30 people in "
        "villages in Niger state.",
        "EGYPT: At least 21 killed after a fuel vehicle overturned and "
        "caught fire.",
        "CONGO: UN peacekeepers evacuated Ebola workers trapped by "
        "fighting in the east.",
        "SUDAN: Rights groups say drone strikes killed 19 people.",
        "SOLOMONS: The Solomon Islands chose Australia as top partner, "
        "ruling out any foreign base.",
        "HORMUZ: Iran claims mines hit two tankers, leaving them on "
        "fire in the Strait of Hormuz.",
    ]
    y = 890
    dot_r = 3
    for item in briefs:
        draw.ellipse([MARGIN, y + 6, MARGIN + 2 * dot_r, y + 6 + 2 * dot_r],
                     fill=RED)
        draw.text((MARGIN + 12, y), item, font=brief, fill=INK)
        y += 17

    # ---- Footer ------------------------------------------------------------
    foot = font(SANS, 12)
    note = ("Sources: Reuters, AP, CNN, BBC, Al Jazeera, WSJ  \u2022  "
            "All events 25 November 2026")
    fw = draw.textlength(note, font=foot)
    draw.text(((PAGE - fw) / 2, 996), note, font=foot, fill=GREY)

    return page


def main() -> None:
    page = build()
    assert page.size == (PAGE, PAGE), page.size
    page.save(OUT, format="PNG")
    data = OUT.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    print(f"wrote {OUT} {len(data)} bytes sha256={digest}")


if __name__ == "__main__":
    main()
