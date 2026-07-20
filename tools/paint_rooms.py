#!/usr/bin/env python
"""Paint the room backgrounds: 320x200, ZQ-32-strict, Sierra idiom.

Each room is composed from a shared scene toolkit (dithered skies and
walls, perspective floors, brick, posters, neon signage with painted
halos, furniture, and rig-painted NPC figures) and written to
assets/rooms/<id>/bg.png plus a binary priority.png walk-behind mask.
Props are placed on their game_data.json hotspot rects so interaction
targets always match the art.

Usage: python tools/paint_rooms.py [room_id ...]   (default: all rooms)
"""
from __future__ import annotations

import json
import os
import sys
from typing import Dict, List, Optional, Sequence, Tuple

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame  # noqa: E402

from zombie_quest.dither import BAYER_4X4, dither_gradient_vertical  # noqa: E402
from zombie_quest.palette import RAMPS, assert_surface_palette  # noqa: E402
from author_characters import (  # noqa: E402
    HERO_STYLE, ZOMBIE_STYLES, STAND_POSE, build_frame,
)

W, H = 320, 200
NIGHT, MAGENTA, CYAN, GOLD = RAMPS["night"], RAMPS["neon_magenta"], RAMPS["neon_cyan"], RAMPS["gold"]
BRICK, SICK, SKIN, BONE = RAMPS["brick"], RAMPS["sick"], RAMPS["skin"], RAMPS["bone"]
BLACK, WHITE = NIGHT[0], BONE[3]

Color = Tuple[int, int, int]

# Fixed star field (no randomness - deterministic art).
STARS = [(14, 8), (41, 22), (67, 5), (95, 15), (123, 9), (150, 25), (178, 6),
         (205, 18), (232, 11), (259, 24), (286, 7), (305, 16), (28, 33),
         (86, 30), (140, 34), (196, 31), (250, 33), (298, 29), (55, 12), (270, 3)]

_FONTS: Dict[int, pygame.font.Font] = {}


def font(size: int) -> pygame.font.Font:
    if size not in _FONTS:
        _FONTS[size] = pygame.font.Font(None, size)
    return _FONTS[size]


def text(s, string, x, y, color, size=10, center=False):
    surf = font(size).render(string, False, color)
    if center:
        x -= surf.get_width() // 2
    s.blit(surf, (x, y))
    return surf.get_width()


def rect(s, x, y, w, h, color):
    s.fill(color, (x, y, w, h))


def outline(s, x, y, w, h, color=BLACK):
    pygame.draw.rect(s, color, (x, y, w, h), 1)


def mix(s, x, y, w, h, color, coverage):
    """Bayer-mix `color` over an area at the given coverage (0..1)."""
    threshold = coverage * 16
    for yy in range(y, min(y + h, H)):
        row = BAYER_4X4[yy % 4]
        for xx in range(x, min(x + w, W)):
            if row[xx % 4] < threshold:
                s.set_at((xx, yy), color)


def halo(s, cx, cy, radius, color):
    """Painted glow: three dithered rings, densest at the center."""
    for band, coverage in ((radius, 0.1), (int(radius * 0.66), 0.22), (int(radius * 0.4), 0.4)):
        for yy in range(max(0, cy - band), min(H, cy + band)):
            row = BAYER_4X4[yy % 4]
            for xx in range(max(0, cx - band), min(W, cx + band)):
                dx, dy = xx - cx, yy - cy
                if dx * dx + dy * dy <= band * band and row[xx % 4] < coverage * 16:
                    s.set_at((xx, yy), color)


def sky(s, horizon, ramp=NIGHT):
    dither_gradient_vertical(s, pygame.Rect(0, 0, W, horizon), list(reversed(ramp)))
    for (sx, sy) in STARS:
        if sy < horizon - 6:
            s.set_at((sx, sy), WHITE if (sx + sy) % 3 else BONE[2])


def moon(s, cx, cy, r):
    pygame.draw.circle(s, BONE[2], (cx, cy), r)
    pygame.draw.circle(s, BONE[3], (cx - r // 3, cy - r // 3), r // 2)
    for (ox, oy, cr) in ((r // 2, r // 4, 2), (-r // 4, r // 2, 1), (r // 3, -r // 2, 1)):
        pygame.draw.circle(s, BONE[1], (cx + ox, cy + oy), cr)


def brick_wall(s, x, y, w, h, base=BRICK[1], dark=BRICK[0], light=BRICK[2]):
    rect(s, x, y, w, h, base)
    for row_index, yy in enumerate(range(y, y + h, 5)):
        pygame.draw.line(s, dark, (x, yy), (x + w - 1, yy))
        offset = 0 if row_index % 2 == 0 else 5
        for xx in range(x + offset, x + w, 10):
            pygame.draw.line(s, dark, (xx, yy), (xx, min(yy + 4, y + h - 1)))
        if row_index % 3 == 1:
            rect(s, x + (offset + 5) % max(1, w - 8), yy + 1, 4, 3, light)


def wood_floor(s, y0, ramp=BRICK):
    """Perspective floorboards: seams converge toward a vanishing point."""
    dither_gradient_vertical(s, pygame.Rect(0, y0, W, H - y0), [ramp[0], ramp[1], ramp[2]])
    vpx, vpy = W // 2, y0 - 40
    for k in range(-8, 9):
        x_at_bottom = W // 2 + k * 44
        for yy in range(y0, H):
            t = (yy - vpy) / (H - vpy)
            xx = int(vpx + (x_at_bottom - vpx) * t)
            if 0 <= xx < W:
                s.set_at((xx, yy), ramp[0])
    for yy in range(y0 + 4, H, 9):
        pygame.draw.line(s, ramp[0], (0, yy), (W - 1, yy))


def street(s, y0):
    """Sidewalk + asphalt with a curb line."""
    rect(s, 0, y0, W, 12, BONE[1])
    pygame.draw.line(s, BONE[0], (0, y0 + 11), (W - 1, y0 + 11))
    for xx in range(0, W, 32):
        pygame.draw.line(s, BONE[0], (xx, y0), (xx, y0 + 10))
    dither_gradient_vertical(s, pygame.Rect(0, y0 + 12, W, H - y0 - 12),
                             [NIGHT[1], BONE[0]])
    for xx in range(6, W, 40):
        rect(s, xx, y0 + 26, 14, 2, GOLD[1])


def tile_floor(s, y0, a=CYAN[0], b=NIGHT[1]):
    for yy in range(y0, H):
        t = (yy - y0) / max(1, H - y0)
        size = 6 + int(t * 8)
        for xx in range(0, W):
            tile = ((xx // size) + ((yy - y0) // (size // 2 + 1))) % 2
            s.set_at((xx, yy), a if tile else b)
    pygame.draw.line(s, BLACK, (0, y0), (W - 1, y0))


def poster(s, x, y, w, h, paper, art_color):
    rect(s, x, y, w, h, paper)
    outline(s, x, y, w, h)
    rect(s, x + 2, y + 2, w - 4, (h - 4) // 2, art_color)
    for i, yy in enumerate(range(y + h // 2 + 2, y + h - 2, 3)):
        pygame.draw.line(s, NIGHT[1], (x + 3, yy), (x + w - 4 - (i % 2) * 3, yy))


def door(s, x, y, w, h, panel=BRICK[1], frame=NIGHT[1]):
    rect(s, x, y, w, h, frame)
    rect(s, x + 2, y + 2, w - 4, h - 2, panel)
    outline(s, x, y, w, h)
    rect(s, x + 4, y + 4, w - 8, h // 2 - 5, shade(panel))
    rect(s, x + 4, y + h // 2 + 2, w - 8, h // 2 - 6, shade(panel))
    s.set_at((x + w - 5, y + h // 2), GOLD[3])


def shade(color: Color) -> Color:
    """The next-darker shade in whatever ramp the color belongs to."""
    for ramp in RAMPS.values():
        if color in ramp:
            index = ramp.index(color)
            return ramp[max(0, index - 1)]
    return color


def neon_sign(s, string, cx, cy, ramp, size=14, backing=True):
    surf = font(size).render(string, False, ramp[2])
    w, h = surf.get_size()
    x, y = cx - w // 2, cy - h // 2
    # Tight halo: a glow collar around the sign, not a cloud over the scene.
    halo(s, cx, cy, min(18, w // 3 + 6), ramp[1])
    if backing:
        rect(s, x - 4, y - 3, w + 8, h + 6, NIGHT[1])
        outline(s, x - 4, y - 3, w + 8, h + 6)
    glow = font(size).render(string, False, ramp[1])
    for (ox, oy) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        s.blit(glow, (x + ox, y + oy))
    s.blit(surf, (x, y))


def window(s, x, y, w, h, lit=False):
    rect(s, x, y, w, h, GOLD[1] if lit else NIGHT[2])
    outline(s, x, y, w, h)
    pygame.draw.line(s, BLACK, (x + w // 2, y), (x + w // 2, y + h - 1))
    pygame.draw.line(s, BLACK, (x, y + h // 2), (x + w - 1, y + h // 2))
    if lit:
        rect(s, x + 1, y + 1, w // 2 - 1, h // 2 - 1, GOLD[2])


def figure(s, style, facing, cx, foot_y, scale=1.0):
    frame = build_frame(style, facing, STAND_POSE)
    if scale != 1.0:
        frame = pygame.transform.scale(
            frame, (max(1, round(16 * scale)), max(1, round(32 * scale))))
    s.blit(frame, (cx - frame.get_width() // 2, foot_y - frame.get_height()))


def record_bin(s, x, y, w, h):
    rect(s, x, y, w, h, BRICK[1])
    outline(s, x, y, w, h)
    spine_colors = [MAGENTA[1], CYAN[1], GOLD[2], SICK[2], BONE[2], BRICK[2]]
    for i, xx in enumerate(range(x + 2, x + w - 3, 3)):
        rect(s, xx, y + 2, 2, h - 8, spine_colors[i % len(spine_colors)])
    rect(s, x + 1, y + h - 5, w - 2, 4, BRICK[0])


def crate(s, x, y, w, h, base=BRICK[1]):
    rect(s, x, y, w, h, base)
    outline(s, x, y, w, h)
    pygame.draw.line(s, shade(base), (x, y + h // 2), (x + w - 1, y + h // 2))
    pygame.draw.line(s, shade(base), (x + w // 2, y), (x + w // 2, y + h - 1))


NPC_MAYA = dict(HERO_STYLE)
NPC_MAYA.update({"hair": BLACK, "hair_hi": NIGHT[2], "hair_sh": BLACK,
                 "jacket": CYAN[1], "jacket_hi": CYAN[2], "accent": CYAN[3],
                 "pants": NIGHT[1], "pants_sh": NIGHT[1]})
NPC_JOHNNY = dict(HERO_STYLE)
NPC_JOHNNY.update({"hair": GOLD[2], "hair_hi": GOLD[3], "hair_sh": GOLD[1],
                   "jacket": GOLD[1], "jacket_hi": GOLD[2], "accent": GOLD[3]})
NPC_CLERK = dict(HERO_STYLE)
NPC_CLERK.update({"hair": BRICK[2], "hair_hi": BRICK[2], "hair_sh": BRICK[1],
                  "jacket": SICK[1], "jacket_hi": SICK[2], "accent": BONE[2]})
NPC_PROMOTER = dict(HERO_STYLE)
NPC_PROMOTER.update({"hair": BONE[1], "hair_hi": BONE[2], "hair_sh": BONE[0],
                     "jacket": NIGHT[1], "jacket_hi": NIGHT[2], "accent": GOLD[3],
                     "shades": True})


# ---------------------------------------------------------------- rooms

def paint_hennepin_outside(s, prio):
    sky(s, 78)
    moon(s, 288, 22, 12)
    # Distant skyline
    for (bx, bw, bh) in ((0, 46, 26), (50, 38, 34), (92, 30, 20), (250, 40, 30), (294, 26, 22)):
        rect(s, bx, 78 - bh, bw, bh, NIGHT[1])
        for wx in range(bx + 4, bx + bw - 3, 8):
            for wy in range(78 - bh + 4, 74, 7):
                s.set_at((wx, wy), GOLD[1] if (wx * wy) % 5 else NIGHT[2])
    # First Avenue star wall: black band with white stars (the marquee strip)
    rect(s, 0, 42, W, 36, NIGHT[1])
    pygame.draw.line(s, BLACK, (0, 78), (W - 1, 78))
    for i, sx in enumerate(range(8, W, 26)):
        sy = 48 + (i % 3) * 9
        s.set_at((sx, sy), WHITE); s.set_at((sx - 1, sy), BONE[2])
        s.set_at((sx + 1, sy), BONE[2]); s.set_at((sx, sy - 1), BONE[2]); s.set_at((sx, sy + 1), BONE[2])
    neon_sign(s, "FIRST AVENUE", 160, 58, GOLD, size=16, backing=False)
    # Building facades down to the street
    brick_wall(s, 0, 79, W, 71)
    # Record store storefront (door hotspot 116..176)
    rect(s, 100, 82, 92, 68, NIGHT[2])
    outline(s, 100, 82, 92, 68)
    neon_sign(s, "LET IT BE", 146, 90, MAGENTA, size=12)
    window(s, 104, 106, 12, 30, lit=True)
    door(s, 118, 100, 56, 50, panel=BRICK[1])
    # First Avenue doors (hotspot 184..242)
    rect(s, 180, 84, 66, 66, NIGHT[1])
    outline(s, 180, 84, 66, 66)
    neon_sign(s, "THE NEON DEAD", 213, 96, MAGENTA, size=12)
    door(s, 186, 106, 26, 44, panel=NIGHT[2])
    door(s, 214, 106, 26, 44, panel=NIGHT[2])
    # Alley to KJRR (hotspot 246..306)
    rect(s, 250, 84, 54, 66, BLACK)
    mix(s, 250, 84, 54, 66, NIGHT[1], 0.35)
    halo(s, 276, 96, 11, CYAN[1])
    text(s, "KJRR >", 256, 92, CYAN[2], 10)
    # Poster kiosk (hotspot 20..74 x 110..180)
    rect(s, 24, 112, 46, 68, BRICK[1])
    outline(s, 24, 112, 46, 68)
    rect(s, 22, 108, 50, 6, BRICK[0])
    outline(s, 22, 108, 50, 6)
    poster(s, 28, 120, 18, 24, BONE[2], MAGENTA[1])
    poster(s, 48, 118, 18, 26, GOLD[3], NIGHT[2])
    poster(s, 30, 148, 16, 22, CYAN[1], NIGHT[1])
    poster(s, 48, 150, 18, 20, MAGENTA[3], SICK[1])
    street(s, 150)
    # Street light (hotspot 8..28 x 40..190): pole with painted pool of light
    halo(s, 16, 46, 16, GOLD[2])
    rect(s, 15, 44, 4, 6, GOLD[3])
    rect(s, 16, 50, 2, 146, NIGHT[1])
    pygame.draw.line(s, BONE[1], (16, 50), (16, 195))
    mix(s, 2, 186, 30, 12, GOLD[1], 0.35)
    # Walk-behind: the lamp pole column
    rect(prio, 15, 44, 4, 6, WHITE)
    rect(prio, 16, 50, 2, 146, WHITE)


def paint_record_store(s, prio):
    # Warm interior: back wall, poster row, bins, counter with clerk.
    dither_gradient_vertical(s, pygame.Rect(0, 0, W, 40), [NIGHT[1], NIGHT[2]])
    brick_wall(s, 0, 40, W, 132, base=BRICK[1])
    pygame.draw.line(s, BLACK, (0, 40), (W - 1, 40))
    neon_sign(s, "VINYL", 160, 24, MAGENTA, size=16)
    halo(s, 60, 30, 12, GOLD[1]); rect(s, 56, 26, 8, 3, GOLD[3])
    halo(s, 260, 30, 12, GOLD[1]); rect(s, 256, 26, 8, 3, GOLD[3])
    # Poster wall over the racks
    poster(s, 46, 48, 22, 30, BONE[2], MAGENTA[1])
    poster(s, 74, 50, 22, 28, GOLD[3], NIGHT[2])
    poster(s, 204, 48, 20, 30, CYAN[1], NIGHT[1])
    # Rare vinyl shelf (hotspot 140..200 x 86..126)
    rect(s, 138, 86, 64, 42, BRICK[0])
    outline(s, 138, 86, 64, 42)
    for row in range(2):
        for i in range(5):
            rect(s, 142 + i * 12, 90 + row * 20, 10, 14,
                 [MAGENTA[1], CYAN[1], GOLD[2], SICK[2], BONE[2]][i])
            outline(s, 142 + i * 12, 90 + row * 20, 10, 14)
    text(s, "RARE", 158, 78, GOLD[2], 10)
    # Street door (hotspot 0..36 x 92..184)
    door(s, 2, 96, 34, 84, panel=NIGHT[2])
    window(s, 8, 102, 20, 24, lit=False)
    # Listening booth (hotspot 44..124 x 96..172)
    rect(s, 46, 98, 74, 74, NIGHT[2])
    outline(s, 46, 98, 74, 74)
    window(s, 54, 104, 26, 30, lit=True)
    rect(s, 86, 104, 26, 42, NIGHT[1])
    figure(s, NPC_MAYA, "down", 99, 144, 0.875)  # patron silhouette in booth
    text(s, "LISTEN", 62, 152, CYAN[2], 10)
    rect(s, 52, 160, 60, 10, BRICK[0])
    # Clerk behind the counter (hotspot 222..298 x 86..182): the figure is
    # painted first with deep feet so the counter occludes the lower body.
    figure(s, NPC_CLERK, "down", 268, 148, 1.0)
    rect(s, 222, 120, 78, 52, BRICK[1])
    outline(s, 222, 120, 78, 52)
    rect(s, 222, 116, 78, 6, BONE[1])
    pygame.draw.line(s, BONE[0], (222, 121), (299, 121))
    # Register on the counter top
    rect(s, 230, 106, 18, 12, NIGHT[1])
    outline(s, 230, 106, 18, 12)
    rect(s, 232, 108, 14, 3, GOLD[2])
    text(s, "$", 286, 126, GOLD[3], 10)
    wood_floor(s, 172)
    # New arrivals bin sits proud of the floor so the hero passes behind it
    record_bin(s, 138, 148, 64, 44)
    text(s, "NEW", 170, 180, MAGENTA[2], 10, center=True)
    rect(prio, 138, 148, 64, 44, WHITE)


def paint_college_station(s, prio):
    # Basement studio: cinder walls, acoustic foam, on-air light, console.
    dither_gradient_vertical(s, pygame.Rect(0, 0, W, 36), [BLACK, NIGHT[1]])
    brick_wall(s, 0, 36, W, 136, base=NIGHT[2], dark=NIGHT[1], light=NIGHT[3])
    pygame.draw.line(s, BLACK, (0, 36), (W - 1, 36))
    # Acoustic foam strip
    for xx in range(0, W, 8):
        pygame.draw.polygon(s, NIGHT[1], [(xx, 36), (xx + 4, 28), (xx + 8, 36)])
    # Poster wall (hotspot 50..100 x 88..138)
    poster(s, 50, 90, 22, 30, MAGENTA[3], NIGHT[2])
    poster(s, 76, 92, 22, 28, BONE[2], SICK[1])
    text(s, "KJRR 89.3", 52, 76, CYAN[2], 10)
    # On-air light (hotspot 108..178 x 86..146)
    halo(s, 143, 100, 22, BRICK[2])
    rect(s, 118, 92, 50, 18, NIGHT[1])
    outline(s, 118, 92, 50, 18)
    text(s, "ON AIR", 143, 96, MAGENTA[2], 12, center=True)
    # Request-line payphone on the wall (hotspot 130..170 x 140..180)
    rect(s, 134, 122, 30, 40, NIGHT[1])
    outline(s, 134, 122, 30, 40)
    rect(s, 138, 126, 22, 12, BONE[1])   # coin panel
    rect(s, 137, 140, 8, 18, BRICK[1])   # handset
    outline(s, 137, 140, 8, 18)
    pygame.draw.line(s, BONE[0], (145, 156), (152, 168))  # cord
    text(s, "REQ", 146, 144, CYAN[2], 8)
    # DJ console (hotspot 214..304 x 84..184)
    rect(s, 214, 120, 92, 52, NIGHT[1])
    outline(s, 214, 120, 92, 52)
    for i in range(6):
        rect(s, 222 + i * 14, 128, 8, 3, [CYAN[2], MAGENTA[2], GOLD[2]][i % 3])
        rect(s, 222 + i * 14, 136, 2, 12, BONE[1])
    rect(s, 214, 114, 92, 8, BONE[0])
    # Turntables
    pygame.draw.circle(s, NIGHT[2], (238, 118), 7); pygame.draw.circle(s, BLACK, (238, 118), 3)
    pygame.draw.circle(s, NIGHT[2], (282, 118), 7); pygame.draw.circle(s, BLACK, (282, 118), 3)
    # Alley door
    door(s, 2, 96, 32, 84, panel=BRICK[1])
    # Records everywhere
    tile_floor(s, 172, a=NIGHT[2], b=NIGHT[1])
    record_bin(s, 44, 156, 56, 36)
    rect(prio, 44, 156, 56, 36, WHITE)


def paint_backstage_stage(s, prio):
    dither_gradient_vertical(s, pygame.Rect(0, 0, W, 44), [BLACK, NIGHT[1]])
    # Stage rigging
    for xx in range(10, W, 44):
        pygame.draw.line(s, NIGHT[1], (xx, 0), (xx, 26))
        halo(s, xx, 30, 9, MAGENTA[1])
        rect(s, xx - 3, 26, 6, 5, NIGHT[2]); rect(s, xx - 2, 31, 4, 2, MAGENTA[2])
    brick_wall(s, 0, 44, W, 132)
    # Green room door (hotspot 0..30 x 100..180)
    door(s, 0, 102, 30, 78, panel=SICK[1])
    text(s, "GREEN", 2, 92, SICK[2], 8)
    # Setlist crate (hotspot 40..100 x 116..180)
    crate(s, 42, 130, 56, 48, BRICK[1])
    rect(s, 50, 122, 26, 10, BONE[2])
    text(s, "SET", 52, 123, BLACK, 8)
    # Monitor mix desk (hotspot 124..198 x 98..172)
    rect(s, 126, 118, 72, 54, NIGHT[1])
    outline(s, 126, 118, 72, 54)
    for i in range(5):
        rect(s, 132 + i * 13, 126, 8, 2, GOLD[2])
        rect(s, 132 + i * 13, 132, 2, 16, BONE[1])
    rect(s, 126, 112, 72, 8, BONE[0])
    text(s, "MON", 152, 100, CYAN[2], 10)
    # Makeup mirrors (hotspot 200..270 x 86..136)
    rect(s, 202, 88, 66, 48, NIGHT[2])
    outline(s, 202, 88, 66, 48)
    for i in range(3):
        rect(s, 206 + i * 22, 92, 18, 34, BONE[1])
        outline(s, 206 + i * 22, 92, 18, 34)
        for (bx, by) in ((208 + i * 22, 94), (220 + i * 22, 94), (208 + i * 22, 122), (220 + i * 22, 122)):
            s.set_at((bx, by), GOLD[3])
        halo(s, 215 + i * 22, 108, 6, GOLD[1])
    # Stage door (hotspot 284..320 x 88..184)
    door(s, 286, 92, 32, 92, panel=BRICK[1])
    neon_sign(s, "EXIT", 300, 84, MAGENTA, size=10, backing=False)
    wood_floor(s, 176, ramp=NIGHT[:3])
    # Flight cases (hotspot 140..180 x 150..180) sit into the walkable band
    crate(s, 140, 160, 40, 30, NIGHT[2])
    rect(s, 144, 164, 8, 4, GOLD[2])
    rect(prio, 140, 160, 40, 30, WHITE)


def paint_green_room(s, prio):
    dither_gradient_vertical(s, pygame.Rect(0, 0, W, 34), [NIGHT[1], NIGHT[2]])
    # Wallpaper: sick-green stripes (it's the Green Room)
    rect(s, 0, 34, W, 142, SICK[0])
    for xx in range(0, W, 8):
        pygame.draw.line(s, SICK[1], (xx, 34), (xx, 175))
    pygame.draw.line(s, BLACK, (0, 34), (W - 1, 34))
    halo(s, 160, 26, 14, GOLD[1]); rect(s, 154, 22, 12, 4, GOLD[3])
    # Band poster wall (hotspot 210..280 x 88..138)
    poster(s, 212, 90, 20, 28, BONE[2], MAGENTA[1])
    poster(s, 236, 88, 20, 30, MAGENTA[3], NIGHT[1])
    poster(s, 258, 92, 18, 26, GOLD[3], BRICK[1])
    # Vintage couch (hotspot 30..110 x 90..140)
    rect(s, 30, 106, 80, 34, MAGENTA[0])
    rect(s, 30, 98, 80, 12, MAGENTA[1])
    rect(s, 26, 104, 8, 36, MAGENTA[0]); rect(s, 106, 104, 8, 36, MAGENTA[0])
    outline(s, 26, 98, 88, 42)
    for xx in (50, 70, 90):
        pygame.draw.line(s, MAGENTA[1], (xx, 108), (xx, 136))
    # Deli tray (hotspot 130..180 x 100..135)
    rect(s, 132, 128, 46, 26, BRICK[1])  # table
    outline(s, 132, 128, 46, 26)
    rect(s, 130, 124, 50, 6, BONE[1])    # tray on the table top
    outline(s, 130, 124, 50, 6)
    rect(s, 134, 120, 10, 4, SICK[2]); rect(s, 148, 120, 12, 4, BRICK[2]); rect(s, 164, 120, 10, 4, GOLD[2])
    # Maya (talk hotspot 100..150) and Johnny Chrome (200..245)
    figure(s, NPC_MAYA, "down", 125, 180, 1.125)
    figure(s, NPC_JOHNNY, "down", 244, 172, 1.125)
    # Guitar rack (hotspot 50..90 x 145..180)
    rect(s, 50, 148, 40, 30, BRICK[0])
    outline(s, 50, 148, 40, 30)
    for i in range(3):
        gx = 56 + i * 12
        rect(s, gx, 150, 3, 22, [MAGENTA[2], CYAN[2], GOLD[2]][i])
        pygame.draw.circle(s, BRICK[2], (gx + 1, 174), 3)
    # Backstage door (hotspot 285..320 x 95..185)
    door(s, 287, 98, 32, 86, panel=NIGHT[2])
    wood_floor(s, 176, ramp=BRICK)
    # Record collection (hotspot 180..230 x 145..180) proud of the floor
    record_bin(s, 180, 156, 50, 34)
    rect(prio, 180, 156, 50, 34, WHITE)



def paint_practice_space(s, prio):
    # Warehouse rehearsal room: block walls, gear everywhere.
    dither_gradient_vertical(s, pygame.Rect(0, 0, W, 30), [BLACK, NIGHT[1]])
    brick_wall(s, 0, 30, W, 146, base=NIGHT[1], dark=BLACK, light=NIGHT[2])
    halo(s, 160, 22, 12, GOLD[1]); rect(s, 154, 18, 12, 4, GOLD[3])
    # Setlist on wall (hotspot 65..90 x 35..65)
    rect(s, 65, 38, 22, 28, BONE[2])
    outline(s, 65, 38, 22, 28)
    for yy in range(42, 62, 4):
        pygame.draw.line(s, NIGHT[1], (68, yy), (83, yy))
    # Egg-crate soundproofing patches
    for (px, py) in ((110, 40), (200, 36), (260, 44)):
        rect(s, px, py, 36, 22, NIGHT[2])
        for xx in range(px, px + 36, 6):
            pygame.draw.line(s, NIGHT[1], (xx, py), (xx, py + 21))
    # Guitar amps (hotspot 185..255 x 85..170)
    for i in range(2):
        ax, ay = 188 + i * 36, 108
        rect(s, ax, ay, 32, 44, NIGHT[1])
        outline(s, ax, ay, 32, 44)
        rect(s, ax + 3, ay + 4, 26, 18, NIGHT[2])
        mix(s, ax + 3, ay + 4, 26, 18, BONE[0], 0.3)
        pygame.draw.circle(s, GOLD[2], (ax + 6, ay + 28), 2)
        pygame.draw.circle(s, GOLD[2], (ax + 14, ay + 28), 2)
        rect(s, ax + 2, ay + 34, 28, 8, NIGHT[2])
    # Drum kit (hotspot 55..135 x 95..170)
    pygame.draw.circle(s, BRICK[2], (95, 140), 16)
    pygame.draw.circle(s, BRICK[1], (95, 140), 16, 2)
    pygame.draw.circle(s, BONE[2], (95, 140), 12)
    pygame.draw.circle(s, BRICK[2], (70, 128), 9); pygame.draw.circle(s, BONE[2], (70, 128), 6)
    pygame.draw.circle(s, BRICK[2], (118, 126), 9); pygame.draw.circle(s, BONE[2], (118, 126), 6)
    pygame.draw.line(s, BONE[1], (60, 110), (66, 128)); pygame.draw.ellipse(s, GOLD[2], (52, 104, 18, 5))
    pygame.draw.line(s, BONE[1], (128, 108), (124, 124)); pygame.draw.ellipse(s, GOLD[2], (120, 102, 18, 5))
    # Mic stands (hotspot 110..180 x 60..170)
    for mx in (150, 170):
        pygame.draw.line(s, BONE[1], (mx, 96), (mx, 168))
        rect(s, mx - 2, 92, 4, 6, NIGHT[1])
        outline(s, mx - 2, 92, 4, 6)
    # Beat-up couch (hotspot 230..300 x 115..150)
    rect(s, 232, 122, 66, 28, BRICK[1])
    rect(s, 232, 116, 66, 10, BRICK[2])
    rect(s, 228, 120, 8, 30, BRICK[1]); rect(s, 294, 120, 8, 30, BRICK[1])
    outline(s, 228, 116, 74, 34)
    rect(s, 250, 124, 12, 6, NIGHT[1])  # torn patch
    # Warehouse door (hotspot 0..28 x 90..170)
    door(s, 0, 94, 28, 82, panel=NIGHT[2])
    wood_floor(s, 176, ramp=NIGHT[:3])
    # Cables across the floor
    for (x0, x1, yy) in ((30, 140, 186), (150, 280, 190)):
        pygame.draw.line(s, BLACK, (x0, yy), (x1, yy + 2))
    rect(prio, 228, 116, 74, 34, WHITE)


def paint_club_bathroom(s, prio):
    # Grimy tiled bathroom, Maya's graffiti on the stall wall.
    rect(s, 0, 0, W, 30, NIGHT[1])
    halo(s, 90, 24, 10, SICK[2]); rect(s, 84, 20, 12, 3, SICK[3])  # dying fluorescent
    # Tiled walls
    for yy in range(30, 150, 10):
        for xx in range(0, W, 10):
            tile_color = CYAN[0] if ((xx + yy) // 10) % 7 else SICK[0]
            rect(s, xx, yy, 9, 9, tile_color)
    # Grout shadows
    mix(s, 0, 130, W, 20, NIGHT[1], 0.3)
    # Cracked mirror (hotspot 35..100 x 50..100)
    rect(s, 37, 50, 60, 46, BONE[2])
    outline(s, 37, 50, 60, 46)
    pygame.draw.line(s, NIGHT[1], (50, 54), (72, 90))
    pygame.draw.line(s, NIGHT[1], (72, 90), (60, 66))
    pygame.draw.line(s, BONE[1], (80, 54), (66, 92))
    # Sink (hotspot 40..95 x 95..145)
    rect(s, 44, 108, 46, 12, BONE[2])
    outline(s, 44, 108, 46, 12)
    rect(s, 54, 120, 26, 20, BONE[1])
    outline(s, 54, 120, 26, 20)
    rect(s, 62, 102, 8, 6, BONE[1])  # faucet
    s.set_at((65, 108), CYAN[2])     # drip
    # Paper towel dispenser (hotspot 115..145 x 70..105)
    rect(s, 117, 72, 26, 30, BONE[1])
    outline(s, 117, 72, 26, 30)
    rect(s, 122, 96, 16, 10, BONE[2])
    # Stalls (hotspot 180..320 x 45..145)
    rect(s, 180, 45, 138, 100, SICK[1])
    outline(s, 180, 45, 138, 100)
    for i in range(2):
        dx = 184 + i * 68
        rect(s, dx, 52, 62, 92, SICK[0])
        outline(s, dx, 52, 62, 92)
        s.set_at((dx + 56, 96), BONE[2])  # latch
    # Maya graffiti (hotspot 185..275 x 70..100): lyric tag
    text(s, "MAYA WAS HERE", 230, 74, MAGENTA[2], 10, center=True)
    text(s, "one more song", 228, 86, CYAN[2], 8, center=True)
    # Door (hotspot 0..30 x 60..145)
    door(s, 0, 62, 30, 84, panel=NIGHT[2])
    tile_floor(s, 150, a=BONE[0], b=NIGHT[1])
    mix(s, 0, 150, W, 50, SICK[0], 0.15)  # grime
    rect(prio, 54, 120, 26, 20, WHITE)    # sink pedestal


def paint_record_vault(s, prio):
    # The collector's vault: floor-to-ceiling shelves, golden display.
    dither_gradient_vertical(s, pygame.Rect(0, 0, W, 28), [BLACK, NIGHT[1]])
    brick_wall(s, 0, 28, W, 148, base=NIGHT[2], dark=NIGHT[1], light=NIGHT[3])
    halo(s, 262, 66, 16, GOLD[2])
    # Rare vinyl shelves (hotspot 110..210 x 30..170)
    rect(s, 108, 30, 104, 144, BRICK[0])
    outline(s, 108, 30, 104, 144)
    spine_colors = [MAGENTA[1], CYAN[1], GOLD[2], SICK[2], BONE[2], BRICK[2], MAGENTA[3], CYAN[2]]
    for row in range(5):
        sy = 36 + row * 28
        rect(s, 112, sy, 96, 22, NIGHT[1])
        for i, xx in enumerate(range(114, 206, 4)):
            rect(s, xx, sy + 2, 3, 18, spine_colors[(i + row) % len(spine_colors)])
        pygame.draw.line(s, BRICK[1], (108, sy + 24), (211, sy + 24))
    # Wooden ladder (hotspot 135..171 x 40..155) leaning on the shelves
    for yy in range(42, 158, 12):
        rect(s, 138, yy, 26, 3, GOLD[1])
    pygame.draw.line(s, GOLD[1], (138, 42), (138, 158))
    pygame.draw.line(s, GOLD[1], (163, 42), (163, 158))
    # Golden display case (hotspot 240..290 x 60..120)
    rect(s, 240, 62, 50, 58, NIGHT[1])
    outline(s, 240, 62, 50, 58)
    rect(s, 244, 66, 42, 34, GOLD[1])
    pygame.draw.circle(s, BLACK, (265, 83), 12)
    pygame.draw.circle(s, GOLD[3], (265, 83), 12, 1)
    pygame.draw.circle(s, GOLD[2], (265, 83), 4)
    text(s, "THE ONE", 265, 106, GOLD[3], 8, center=True)
    # Listening station (hotspot 235..295 x 110..155)
    rect(s, 236, 126, 58, 30, NIGHT[1])
    outline(s, 236, 126, 58, 30)
    pygame.draw.circle(s, NIGHT[2], (252, 138), 8); pygame.draw.circle(s, BLACK, (252, 138), 3)
    rect(s, 268, 132, 20, 12, NIGHT[2])
    rect(s, 270, 134, 6, 3, CYAN[2])
    # Record crate (hotspot 20..75 x 120..155)
    wood_floor(s, 176, ramp=BRICK)
    crate(s, 22, 140, 52, 40, BRICK[1])
    for i, xx in enumerate(range(26, 70, 5)):
        rect(s, xx, 144, 4, 14, spine_colors[i % len(spine_colors)])
    # Vault door (hotspot 0..26 x 75..155)
    rect(s, 0, 78, 26, 98, BONE[0])
    outline(s, 0, 78, 26, 98)
    pygame.draw.circle(s, BONE[1], (13, 120), 8)
    pygame.draw.circle(s, NIGHT[1], (13, 120), 8, 2)
    pygame.draw.line(s, NIGHT[1], (13, 114), (13, 126))
    pygame.draw.line(s, NIGHT[1], (7, 120), (19, 126 - 6))
    rect(prio, 22, 140, 52, 40, WHITE)


def paint_promoter_office(s, prio):
    # Velvet-and-gold office with something wrong underneath.
    dither_gradient_vertical(s, pygame.Rect(0, 0, W, 26), [BLACK, NIGHT[1]])
    rect(s, 0, 26, W, 150, NIGHT[2])
    for xx in range(0, W, 12):  # wallpaper stripes
        pygame.draw.line(s, NIGHT[1], (xx, 26), (xx, 175))
    halo(s, 160, 20, 12, GOLD[1]); rect(s, 152, 16, 16, 4, GOLD[3])
    # Window, city night (hotspot 10..60 x 35..95)
    rect(s, 12, 36, 46, 56, NIGHT[1])
    outline(s, 12, 36, 46, 56)
    rect(s, 14, 38, 42, 52, NIGHT[2])
    for (wx, wy) in ((20, 60), (30, 52), (42, 66), (48, 48), (26, 74), (44, 80)):
        s.set_at((wx, wy), GOLD[2])
    moon(s, 44, 46, 5)
    pygame.draw.line(s, BLACK, (35, 36), (35, 91))
    # Gold records (hotspot 90..220 x 35..85)
    for i in range(4):
        gx = 94 + i * 32
        rect(s, gx, 40, 26, 30, BRICK[0])
        outline(s, gx, 40, 26, 30)
        pygame.draw.circle(s, GOLD[2], (gx + 13, 55), 9)
        pygame.draw.circle(s, GOLD[3], (gx + 13, 55), 9, 1)
        pygame.draw.circle(s, BRICK[0], (gx + 13, 55), 3)
    # Bookshelf (hotspot 235..310 x 60..150)
    rect(s, 236, 60, 74, 92, BRICK[0])
    outline(s, 236, 60, 74, 92)
    for row in range(4):
        sy = 64 + row * 22
        for i, xx in enumerate(range(240, 304, 8)):
            book = [BRICK[1], NIGHT[1], SICK[1], BRICK[2], MAGENTA[0]][(i + row) % 5]
            rect(s, xx, sy, 7, 18, book)
        pygame.draw.line(s, BRICK[1], (236, sy + 19), (309, sy + 19))
    # The Promoter behind his desk (talk hotspot 150..205 x 85..180)
    figure(s, NPC_PROMOTER, "down", 178, 148, 1.125)
    # Massive desk (hotspot 80..240 x 100..150)
    rect(s, 82, 118, 156, 36, BRICK[0])
    outline(s, 82, 118, 156, 36)
    rect(s, 80, 112, 160, 8, BRICK[1])
    outline(s, 80, 112, 160, 8)
    # Contracts on the desk (hotspot 110..155 x 107..137)
    rect(s, 112, 106, 20, 8, BONE[2])
    rect(s, 116, 104, 20, 8, BONE[3])
    pygame.draw.line(s, NIGHT[1], (118, 107), (132, 107))
    s.set_at((133, 109), MAGENTA[2])  # signature line... in red
    # Desk lamp
    rect(s, 210, 100, 3, 12, NIGHT[1])
    pygame.draw.ellipse(s, GOLD[2], (204, 96, 16, 6))
    halo(s, 212, 104, 8, GOLD[1])
    # Occult symbols half-hidden by the rug (hotspot 260..295 x 165..195)
    wood_floor(s, 176, ramp=NIGHT[:3])
    rect(s, 70, 180, 180, 20, BRICK[0])  # rug
    pygame.draw.circle(s, MAGENTA[1], (277, 184), 7, 1)
    pygame.draw.line(s, MAGENTA[1], (272, 188), (282, 180))
    pygame.draw.line(s, MAGENTA[1], (272, 180), (282, 188))
    # Private door (hotspot 285..320 x 65..150)
    door(s, 287, 68, 32, 84, panel=BRICK[0])
    rect(prio, 80, 112, 160, 42, WHITE)   # desk: hero can walk behind it


def paint_loading_dock(s, prio):
    # Night loading dock: elevated platform, semi truck, harsh security light.
    sky(s, 60)
    moon(s, 30, 16, 8)
    brick_wall(s, 0, 60, W, 56, base=NIGHT[1], dark=BLACK, light=NIGHT[2])
    # Overhead rolling door (hotspot 10..100 x 35..115)
    rect(s, 10, 38, 90, 76, BONE[0])
    outline(s, 10, 38, 90, 76)
    for yy in range(42, 110, 7):
        pygame.draw.line(s, NIGHT[1], (11, yy), (98, yy))
    # Exit sign (hotspot 105..125 x 80..90)
    neon_sign(s, "EXIT", 115, 84, MAGENTA, size=10, backing=False)
    # Security light (hotspot 22..42 x 20..140)
    halo(s, 32, 26, 14, BONE[2])
    rect(s, 28, 22, 8, 5, BONE[1])
    pygame.draw.line(s, BONE[1], (32, 27), (32, 38))
    # Semi truck (hotspot 100..280 x 70..140) parked at the dock
    rect(s, 104, 74, 150, 62, BONE[1])       # trailer
    outline(s, 104, 74, 150, 62)
    mix(s, 104, 74, 150, 30, BONE[0], 0.25)
    text(s, "NEON DEAD TOUR", 178, 96, MAGENTA[1], 12, center=True)
    rect(s, 254, 90, 30, 46, BRICK[1])       # cab
    outline(s, 254, 90, 30, 46)
    window(s, 258, 96, 14, 14, lit=False)
    pygame.draw.circle(s, BLACK, (268, 138), 9); pygame.draw.circle(s, BONE[0], (268, 138), 4)
    pygame.draw.circle(s, BLACK, (120, 138), 9); pygame.draw.circle(s, BONE[0], (120, 138), 4)
    # Dock platform (hotspot 0..120 x 115..140) - the walkable zone
    rect(s, 0, 115, 120, 10, BONE[1])
    pygame.draw.line(s, BONE[0], (0, 124), (119, 124))
    rect(s, 0, 125, 120, 20, NIGHT[1])
    mix(s, 0, 125, 120, 20, BONE[0], 0.3)
    pygame.draw.line(s, GOLD[2], (0, 115), (119, 115))  # safety stripe
    # Road cases (hotspot 20..100 x 90..150)
    crate(s, 24, 92, 34, 24, NIGHT[2])
    crate(s, 62, 98, 30, 18, NIGHT[2])
    rect(s, 28, 96, 8, 4, GOLD[2])
    # Zombie roadie slumped by the truck (hotspot 245..275 x 110..150)
    figure(s, ZOMBIE_STYLES["zombie_rocker"], "left", 258, 148, 0.875)
    # Ground below the dock edge
    rect(s, 120, 145, 200, 55, NIGHT[1])
    mix(s, 120, 145, 200, 55, BONE[0], 0.2)
    rect(s, 0, 145, 120, 55, NIGHT[1])
    mix(s, 0, 145, 120, 55, BLACK, 0.4)
    rect(prio, 24, 92, 34, 24, WHITE)
    rect(prio, 62, 98, 30, 18, WHITE)


ROOM_PAINTERS = {
    "hennepin_outside": paint_hennepin_outside,
    "record_store": paint_record_store,
    "college_station": paint_college_station,
    "backstage_stage": paint_backstage_stage,
    "green_room": paint_green_room,
    "practice_space": paint_practice_space,
    "club_bathroom": paint_club_bathroom,
    "record_vault": paint_record_vault,
    "promoter_office": paint_promoter_office,
    "loading_dock": paint_loading_dock,
}


def paint_room(room_id: str, assets_root: str) -> None:
    painter = ROOM_PAINTERS[room_id]
    s = pygame.Surface((W, H))
    s.fill(BLACK)
    prio = pygame.Surface((W, H))
    prio.fill((0, 0, 0))
    painter(s, prio)
    assert_surface_palette(s, context=f"{room_id} bg")
    # Normalize the mask to strict binary black/white regardless of what
    # tones the painter used.
    bitmask = pygame.mask.from_threshold(prio, (255, 255, 255), (80, 80, 80))
    prio = bitmask.to_surface(setcolor=(255, 255, 255), unsetcolor=(0, 0, 0))
    out_dir = os.path.join(assets_root, "rooms", room_id)
    os.makedirs(out_dir, exist_ok=True)
    pygame.image.save(s, os.path.join(out_dir, "bg.png"))
    pygame.image.save(prio, os.path.join(out_dir, "priority.png"))
    print(f"painted {room_id}")


def main() -> None:
    pygame.init()
    pygame.font.init()
    assets_root = os.path.join(REPO_ROOT, "assets")
    targets = sys.argv[1:] or list(ROOM_PAINTERS)
    for room_id in targets:
        paint_room(room_id, assets_root)


if __name__ == "__main__":
    main()
