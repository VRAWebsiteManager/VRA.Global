#!/usr/bin/env python3
"""VRA Open Graph card generator.  1200x627, matches the house style.

  python3 make_og.py out.png "Headline line one" "Headline line two" "Subline."
"""
import sys
from PIL import Image, ImageDraw, ImageFont

PLATE = "plate.png"
BOLD  = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
REG   = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

X        = 92
RULE     = (X, 159, X + 64, 164)
C_RULE   = (160, 210, 234)
C_EYE    = (182, 236, 255)
C_HEAD   = (255, 255, 255)
C_SUB    = (200, 223, 239)
C_MARK   = (182, 236, 255)
EYEBROW  = "VIRTUAL REALTY ASSISTANTS"


def tracked(d, xy, text, font, fill, track):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + track
    return x - track


def build(out, l1, l2, sub, wordmark="vra.global"):
    im = Image.open(PLATE).convert("RGB")
    d = ImageDraw.Draw(im)
    f_eye  = ImageFont.truetype(BOLD, 20)
    f_head = ImageFont.truetype(BOLD, 66)
    f_sub  = ImageFont.truetype(REG, 28)
    f_mark = ImageFont.truetype(BOLD, 24)

    d.rectangle(RULE, fill=C_RULE)
    tracked(d, (X, 188), EYEBROW, f_eye, C_EYE, 5.9)
    d.text((X, 240), l1, font=f_head, fill=C_HEAD)
    d.text((X, 305), l2, font=f_head, fill=C_HEAD)
    d.text((X, 430), sub, font=f_sub, fill=C_SUB)
    d.text((X, 548), wordmark, font=f_mark, fill=C_MARK)
    im.save(out)
    return im


if __name__ == "__main__":
    o, l1, l2, sub = sys.argv[1:5]
    build(o, l1, l2, sub)
    print("wrote", o)
