#!/usr/bin/env python3
"""
Generates the GitHub social preview card for the keeper-plugin repo.

Aesthetic: "Tumbler Field" — a specimen plate of pin-tumbler chambers
arrayed across the canvas, broken by a single horizontal shear line.
Renders at 2x and downsamples for crisp anti-aliased edges.
"""

from __future__ import annotations

import math
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Constants

FONT_DIR = Path(
    "/Users/patrickking/Library/Application Support/Claude/"
    "local-agent-mode-sessions/skills-plugin/"
    "3220224b-1250-400b-8bac-32e43903cd43/"
    "c1f61ff3-fad9-4b58-89ff-0e058295926e/skills/canvas-design/canvas-fonts"
)

OUT_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = OUT_DIR / "social-preview.png"

# Final target dimensions (GitHub social preview spec)
TARGET_W, TARGET_H = 1280, 640
SCALE = 2
W, H = TARGET_W * SCALE, TARGET_H * SCALE

# 40pt safe-zone, scaled
SAFE = 80 * SCALE // 2  # 40pt → 80 at 2x

# Palette — graphite ground, paper marks, warm brass accent
GROUND = (15, 17, 21)         # ink graphite
PIN    = (228, 224, 213)      # cool paper, slightly bone
PIN_TOP = (196, 192, 182)     # top pins read very slightly recessed
SHEAR  = (211, 171, 109)      # antique brass, a touch more saturated
MUTED  = (98, 100, 106)       # quiet annotation
ACCENT_DIM = (138, 114, 78)   # darker brass, for URL
SUB    = (162, 158, 148)      # subtitle — dimmer than PIN

# Pin field config
N_PINS = 56
PIN_W = 3 * SCALE             # column thickness at 2x
SHEAR_RATIO = 0.42            # shear line at 42% from top (just above visual center)
PIN_GAP = 5 * SCALE           # gap between top/bottom pin at shear line

# Pin heights — encoded from a phrase, then normalized.
# This is the subtle reference: the bitting spells something.
SEED_PHRASE = "KEEPER-IS-THE-KEY-TO-THE-VAULT-CLAUDE-CODE-COWORK-CUSTODY"


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = FONT_DIR / name
    return ImageFont.truetype(str(path), size)


def pin_heights() -> list[float]:
    """Return N_PINS values in [0.25, 0.85] derived from SEED_PHRASE bytes."""
    bytes_ = (SEED_PHRASE.encode("utf-8") * 4)[:N_PINS]
    lo, hi = 0.22, 0.82
    return [lo + (b % 64) / 63 * (hi - lo) for b in bytes_]


def smooth_jitter(values: list[float], passes: int = 1) -> list[float]:
    """Light 3-tap smoothing so adjacent pins read as a rhythmic field, not noise."""
    out = list(values)
    for _ in range(passes):
        out = [
            (out[max(i - 1, 0)] + out[i] * 2 + out[min(i + 1, len(out) - 1)]) / 4
            for i in range(len(out))
        ]
    return out


def draw_field(draw: ImageDraw.ImageDraw) -> tuple[int, int, int, int]:
    """Render the pin-tumbler specimen field. Returns its bounding box."""
    field_left = SAFE + 30 * SCALE
    field_right = W - SAFE - 30 * SCALE
    field_top = SAFE + 40 * SCALE
    field_bottom = H - SAFE - 130 * SCALE  # leave room for caption strip

    chamber_h = field_bottom - field_top
    shear_y = field_top + int(chamber_h * SHEAR_RATIO)

    heights = smooth_jitter(pin_heights(), passes=1)
    # In real pin tumblers, top pins are mostly uniform driver pins; the
    # bittings live in the bottom pins. Mirror that here for honesty of form.
    top_lengths = smooth_jitter(
        [0.86 + ((i * 37) % 7) / 100 for i in range(N_PINS)], passes=2
    )

    spacing = (field_right - field_left) / (N_PINS - 1)
    chamber_top_h = (shear_y - PIN_GAP // 2) - field_top
    chamber_bot_h = field_bottom - (shear_y + PIN_GAP // 2)

    for i, (h, t) in enumerate(zip(heights, top_lengths)):
        cx = round(field_left + i * spacing)

        # Bottom pin (the bitting) — rises from field_bottom
        bp_y0 = (shear_y + PIN_GAP // 2) + int((1 - h) * chamber_bot_h)
        bp_y1 = field_bottom

        # Top pin (driver) — descends from field_top, mostly uniform
        tp_y0 = field_top
        tp_y1 = field_top + int(t * chamber_top_h)

        # Top pins read slightly recessed via a cooler grey
        draw.rectangle(
            [cx - PIN_W // 2, tp_y0, cx + PIN_W // 2, tp_y1],
            fill=PIN_TOP,
        )
        draw.rectangle(
            [cx - PIN_W // 2, bp_y0, cx + PIN_W // 2, bp_y1],
            fill=PIN,
        )

        # Specimen-plate registration ticks below every 8th column
        if i % 8 == 0:
            tick_h = 6 * SCALE
            draw.rectangle(
                [cx - 1, field_bottom + 8 * SCALE,
                 cx + 1, field_bottom + 8 * SCALE + tick_h],
                fill=MUTED,
            )

    # The shear line itself — single thin warm thread across the whole field
    shear_thickness = 1 * SCALE
    draw.rectangle(
        [field_left - 10 * SCALE, shear_y - shear_thickness // 2,
         field_right + 10 * SCALE, shear_y + shear_thickness // 2],
        fill=SHEAR,
    )

    # Whisper-thin baseline beneath the field
    draw.rectangle(
        [field_left, field_bottom + 1,
         field_right, field_bottom + 1 + 1 * SCALE],
        fill=(48, 50, 56),
    )

    return field_left, field_top, field_right, field_bottom, shear_y


def draw_typography(draw: ImageDraw.ImageDraw, field_box: tuple[int, int, int, int, int]) -> None:
    field_left, field_top, field_right, field_bottom, shear_y = field_box

    # ----- KEEPER — set on the shear line, large display serif
    title_font = load_font("Italiana-Regular.ttf", 120 * SCALE)
    title = "KEEPER"
    title_tracked = "  ".join(list(title))  # add extra letter-spacing

    bbox = draw.textbbox((0, 0), title_tracked, font=title_font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (W - tw) // 2 - bbox[0]
    ty = shear_y - th // 2 - bbox[1] - 4 * SCALE

    # Knock out the shear line behind the title — gives the letters air
    pad_x = 18 * SCALE
    pad_y = 8 * SCALE
    draw.rectangle(
        [tx - pad_x, ty + bbox[1] - pad_y,
         tx + tw + pad_x, ty + bbox[3] + pad_y],
        fill=GROUND,
    )
    # Title in warm brass — same hue as the shear line so the word IS the mechanism
    draw.text((tx, ty), title_tracked, font=title_font, fill=SHEAR)

    # ----- Plate annotation (top-right): "FIG. 01 / N = 56"
    plate_font = load_font("IBMPlexMono-Regular.ttf", 18 * SCALE)
    plate_text = "FIG. 01   ·   N = 56"
    bbox = draw.textbbox((0, 0), plate_text, font=plate_font)
    draw.text(
        (W - SAFE - (bbox[2] - bbox[0]), SAFE),
        plate_text,
        font=plate_font,
        fill=MUTED,
    )

    # ----- Plate annotation (top-left): movement title
    movement_font = load_font("IBMPlexMono-Regular.ttf", 18 * SCALE)
    movement = "TUMBLER FIELD"
    draw.text((SAFE, SAFE), movement, font=movement_font, fill=MUTED)

    # ----- Subtitle beneath the field
    sub_font = load_font("IBMPlexMono-Regular.ttf", 20 * SCALE)
    subtitle = "A   CUSTODIAL   TOOLKIT   ·   CLAUDE   CODE   &   COWORK"
    bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
    sx = (W - (bbox[2] - bbox[0])) // 2
    sy = field_bottom + 40 * SCALE
    draw.text((sx, sy), subtitle, font=sub_font, fill=SUB)

    # ----- URL (bottom-center, small, brass-dim)
    url_font = load_font("IBMPlexMono-Regular.ttf", 16 * SCALE)
    url = "github.com / patrickking67 / keeper-plugin"
    bbox = draw.textbbox((0, 0), url, font=url_font)
    ux = (W - (bbox[2] - bbox[0])) // 2
    uy = field_bottom + 76 * SCALE
    draw.text((ux, uy), url, font=url_font, fill=ACCENT_DIM)

    # ----- Small specimen marks: dimension brackets at field corners
    bracket_color = MUTED
    bw = 14 * SCALE
    bt = 1 * SCALE
    # top-left bracket
    draw.rectangle([field_left - 18 * SCALE, field_top - 18 * SCALE,
                    field_left - 18 * SCALE + bw, field_top - 18 * SCALE + bt],
                   fill=bracket_color)
    draw.rectangle([field_left - 18 * SCALE, field_top - 18 * SCALE,
                    field_left - 18 * SCALE + bt, field_top - 18 * SCALE + bw],
                   fill=bracket_color)
    # top-right bracket
    draw.rectangle([field_right + 18 * SCALE - bw, field_top - 18 * SCALE,
                    field_right + 18 * SCALE, field_top - 18 * SCALE + bt],
                   fill=bracket_color)
    draw.rectangle([field_right + 18 * SCALE - bt, field_top - 18 * SCALE,
                    field_right + 18 * SCALE, field_top - 18 * SCALE + bw],
                   fill=bracket_color)
    # bottom-left
    draw.rectangle([field_left - 18 * SCALE, field_bottom + 18 * SCALE - bt,
                    field_left - 18 * SCALE + bw, field_bottom + 18 * SCALE],
                   fill=bracket_color)
    draw.rectangle([field_left - 18 * SCALE, field_bottom + 18 * SCALE - bw,
                    field_left - 18 * SCALE + bt, field_bottom + 18 * SCALE],
                   fill=bracket_color)
    # bottom-right
    draw.rectangle([field_right + 18 * SCALE - bw, field_bottom + 18 * SCALE - bt,
                    field_right + 18 * SCALE, field_bottom + 18 * SCALE],
                   fill=bracket_color)
    draw.rectangle([field_right + 18 * SCALE - bt, field_bottom + 18 * SCALE - bw,
                    field_right + 18 * SCALE, field_bottom + 18 * SCALE],
                   fill=bracket_color)


def main() -> None:
    img = Image.new("RGB", (W, H), GROUND)
    draw = ImageDraw.Draw(img)

    field_box = draw_field(draw)
    draw_typography(draw, field_box)

    # Downsample to target with high-quality filter for anti-aliased edges
    final = img.resize((TARGET_W, TARGET_H), Image.LANCZOS)
    final.save(OUTPUT_PATH, "PNG", optimize=True)
    print(f"Wrote {OUTPUT_PATH}  ({OUTPUT_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
