#!/usr/bin/env python3
"""Compose the 25 November 2026 front page (1024x1024): three generated
scene illustrations plus PIL-drawn headlines, text and captions.
Fresh build for news-image-20261125. Run: python3 compose.py
-> writes entry.png here. Deterministic: no network, no randomness,
no timestamps; the same input files always produce the same bytes.

Stories (all events of Wed 25 Nov 2026, cross-checked across Reuters,
AP/CNN, BBC/Al Jazeera, WSJ, SCMP):
  LEAD  Russia hits Kyiv with ballistic missiles; energy/gas sites
        struck, power cut in five regions
  TARIFFS US proposes new tariffs on 14 trading partners; markets slide
  RIYADH Houthi drone hits Riyadh financial-district tower, 11 hurt
  HUAWEI Brooklyn jury convicts Huawei on 10 of 12 counts
  COLOMBIA Hostages freed after 17-hour supermarket siege
  BRIEFS Nigeria, Egypt, Congo Ebola, Sudan, Solomons, Hormuz
"""
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (17, 17, 17)
RED = (178, 34, 34)
GREY = (90, 90, 88)
RULE = (60, 60, 60)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_lines(draw, text, fnt, width):
    """Greedy word wrap: lines of `text` that fit in `width` pixels."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if draw.textlength(trial, font=fnt) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


def draw_para(draw, x, y, width, text, fnt, fill=INK, leading=None):
    leading = leading or int(fnt.size * 1.35)
    for line in wrap_lines(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def cover(im, w, h):
    """Centre-crop an image to exactly w x h."""
    iw, ih = im.size
    s = max(w / iw, h / ih)
    im = im.resize((round(iw * s), round(ih * s)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 28  # margin
    right = W - M

    # ---- Masthead ----
    d.text((W // 2, 18), "THE WORLD", font=font(SERIF_B, 62),
           fill=INK, anchor="ma")
    d.line([(M, 96), (right, 96)], fill=RULE, width=2)
    d.text((W // 2, 104), "WEDNESDAY, 25 NOVEMBER 2026  \u2022  ONE DAY IN PICTURES",
           font=font(SANS_B, 19), fill=INK, anchor="ma")
    d.line([(M, 134), (right, 134)], fill=RULE, width=2)

    # ---- Lead story: missiles rain on Kyiv ----
    y = 148
    kyiv = Image.open(HERE / "assets" / "media-generation-kyiv-night-missiles-0-afb16ca5-6d7f-40af-8e69-69733eb173d2.webp").convert("RGB")
    img.paste(cover(kyiv, 512, 268), (484, y))
    d.text((484, y + 274), "Kyiv at night. Russian ballistic missiles struck",
           font=font(SERIF, 13), fill=GREY)
    d.text((484, y + 292), "two sites in the capital, the mayor said.",
           font=font(SERIF, 13), fill=GREY)
    d.text((M, y), "UKRAINE", font=font(SANS_B, 15), fill=RED)
    d.text((M, y + 22), "MISSILES RAIN", font=font(SERIF_B, 44), fill=RED)
    d.text((M, y + 70), "ON KYIV", font=font(SERIF_B, 44), fill=RED)
    by = draw_para(d, M, y + 128, 440,
                   "Russian forces hit Kyiv with ballistic missiles late "
                   "on Wednesday, striking two sites in the city.",
                   font(SANS, 16))
    by = draw_para(d, M, by + 6, 440,
                   "An overnight attack on energy and gas sites cut power "
                   "in five regions and halted a thermal power plant.",
                   font(SANS, 16))

    # ---- Row 2: tariffs + Riyadh ----
    y2 = 470
    d.line([(M, y2 - 10), (right, y2 - 10)], fill=RULE, width=2)
    col_w = 474
    # left: tariffs
    ship = Image.open(HERE / "assets" / "media-generation-tariffs-container-ship-0-702e352e-0331-4ce8-9d68-549c4ebc0e6e.webp").convert("RGB")
    img.paste(cover(ship, col_w, 150), (M, y2))
    d.text((M, y2 + 158), "NEW TARIFFS", font=font(SERIF_B, 24), fill=INK)
    d.text((M, y2 + 187), "ON 14 NATIONS", font=font(SERIF_B, 24), fill=INK)
    draw_para(d, M, y2 + 222, col_w,
              "The US proposed new tariffs on 14 trading partners to "
              "fight excess factory capacity \u2014 up to 20% on China, "
              "15% on the EU \u2014 as markets slid worldwide.",
              font(SANS, 16), leading=20)
    # right: Riyadh tower
    tower = Image.open(HERE / "assets" / "media-generation-riyadh-tower-smoke-0-46061971-cc78-4f98-9d07-3ac6f55ff2f7.webp").convert("RGB")
    img.paste(cover(tower, col_w, 150), (522, y2))
    d.text((522, y2 + 158), "DRONE HITS", font=font(SERIF_B, 24), fill=INK)
    d.text((522, y2 + 187), "RIYADH TOWER", font=font(SERIF_B, 24), fill=INK)
    draw_para(d, 522, y2 + 222, col_w,
              "A Houthi drone struck a tower in Riyadh\u2019s financial "
              "district, wounding 11 people \u2014 the second strike on "
              "the capital\u2019s tallest tower in less than a week.",
              font(SANS, 16), leading=20)

    # ---- Row 3: Huawei + Colombia ----
    y3 = 770
    d.line([(M, y3 - 10), (right, y3 - 10)], fill=RULE, width=2)
    d.text((M, y3), "HUAWEI GUILTY ON", font=font(SERIF_B, 21), fill=INK)
    d.text((M, y3 + 26), "10 OF 12 COUNTS", font=font(SERIF_B, 21), fill=INK)
    draw_para(d, M, y3 + 58, col_w,
              "A Brooklyn jury convicted Huawei of bank fraud, wire "
              "fraud and sanctions violations, but acquitted it of "
              "racketeering conspiracy.",
              font(SANS, 15), leading=19)
    d.text((522, y3), "COLOMBIA: HOSTAGES", font=font(SERIF_B, 21), fill=INK)
    d.text((522, y3 + 26), "FREED AFTER SIEGE", font=font(SERIF_B, 21), fill=INK)
    draw_para(d, 522, y3 + 58, col_w,
              "Twenty-five hostages were freed in Cartagena after a "
              "17-hour supermarket siege; one captor was killed.",
              font(SANS, 16), leading=20)

    # ---- Briefs strip ----
    y4 = 906
    d.line([(M, y4 - 8), (right, y4 - 8)], fill=RULE, width=2)
    d.text((M, y4), "ALSO TODAY", font=font(SANS_B, 17), fill=RED)
    briefs = [
        "NIGERIA: Suspected militants killed at least 30 people in villages in Niger state.",
        "EGYPT: At least 21 killed after a fuel vehicle overturned and caught fire.",
        "CONGO: UN peacekeepers evacuated Ebola workers trapped by fighting in the east.",
        "SUDAN: Rights groups say drone strikes killed 19 people.",
        "SOLOMONS: The Solomon Islands chose Australia as top partner, ruling out any foreign base.",
        "HORMUZ: Iran claims mines hit two tankers, leaving them on fire in the Strait of Hormuz.",
    ]
    by = y4 + 22
    for b in briefs:
        d.text((M, by), "\u2022", font=font(SANS_B, 13), fill=RED)
        by = draw_para(d, M + 18, by, right - M - 18, b, font(SANS, 12), leading=13)
    d.text((W // 2, H - 16), "Sources: Reuters, AP, CNN, BBC, Al Jazeera, WSJ  \u2022  All events 25 November 2026",
           font=font(SANS, 11), fill=GREY, anchor="ma")

    out = HERE / "entry.png"
    img.save(out, "PNG", optimize=True)
    print("saved", out, out.stat().st_size, "bytes", img.size)


if __name__ == "__main__":
    main()
