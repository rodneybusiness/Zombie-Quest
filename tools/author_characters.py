#!/usr/bin/env python
"""Author the character sprites: 16x32, ZQ-32, real walk cycles.

Sprites are built from a parameterized component rig (hair/head/torso/
arms/legs) so every walk frame shares one anatomy and the stride reads
frame-to-frame: 6 frames per direction (contact/recoil/passing x2) with
leg alternation, arm counter-swing, and a 1px body bob on passing poses.
A final pass traces a 1px black outline around the silhouette - the
Sierra look. Right-facing frames mirror left.

Zombie variants reuse the rig with a hunch, a forward-arm shamble, an
uneven stride, and per-type palettes/accessories (bouncer shades, DJ
headphones, rocker bleach-blond hair).

Output: assets/characters/<name>/{sheet.png, meta.json}
Usage:  python tools/author_characters.py [assets_root]
"""
from __future__ import annotations

import json
import os
import sys
from typing import Dict, Optional, Tuple

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import pygame  # noqa: E402

from zombie_quest.palette import RAMPS, assert_surface_palette  # noqa: E402

FRAME_W, FRAME_H = 16, 32
DIRECTIONS = ["down", "up", "left", "right"]
WALK_FRAMES = 6
TOTAL_FRAMES = 7  # 6 walk + 1 stand

NIGHT, MAGENTA, CYAN, GOLD = RAMPS["night"], RAMPS["neon_magenta"], RAMPS["neon_cyan"], RAMPS["gold"]
BRICK, SICK, SKIN, BONE = RAMPS["brick"], RAMPS["sick"], RAMPS["skin"], RAMPS["bone"]
BLACK = NIGHT[0]

HERO_STYLE = {
    "hair": NIGHT[2], "hair_hi": NIGHT[3], "hair_sh": NIGHT[1],
    "skin": SKIN[2], "skin_hi": SKIN[3], "skin_sh": SKIN[1],
    "jacket": MAGENTA[0], "jacket_hi": MAGENTA[1], "shirt": NIGHT[1],
    "pants": BONE[1], "pants_sh": BONE[0], "boots": NIGHT[1], "accent": MAGENTA[2],
    "hunch": 0, "eye": BLACK,
}

ZOMBIE_STYLES = {
    "zombie_scene": {
        "hair": SICK[1], "hair_hi": SICK[2], "hair_sh": SICK[0],
        "skin": SICK[2], "skin_hi": SICK[3], "skin_sh": SICK[1],
        "jacket": NIGHT[2], "jacket_hi": NIGHT[3], "shirt": NIGHT[1],
        "pants": NIGHT[2], "pants_sh": NIGHT[1], "boots": BLACK, "accent": MAGENTA[1],
        "hunch": 1, "eye": MAGENTA[2],
    },
    "zombie_bouncer": {
        "hair": NIGHT[1], "hair_hi": BONE[0], "hair_sh": BLACK,
        "skin": SICK[1], "skin_hi": SICK[2], "skin_sh": SICK[0],
        "jacket": BONE[0], "jacket_hi": BONE[1], "shirt": BONE[3],
        "pants": BONE[0], "pants_sh": NIGHT[1], "boots": BLACK, "accent": BONE[1],
        "hunch": 1, "eye": MAGENTA[2], "shades": True, "broad": True,
    },
    "zombie_rocker": {
        "hair": GOLD[3], "hair_hi": GOLD[3], "hair_sh": GOLD[2],
        "skin": SICK[2], "skin_hi": SICK[3], "skin_sh": SICK[1],
        "jacket": BRICK[1], "jacket_hi": BRICK[2], "shirt": BLACK,
        "pants": NIGHT[2], "pants_sh": NIGHT[1], "boots": BLACK, "accent": GOLD[2],
        "hunch": 1, "eye": MAGENTA[2],
    },
    "zombie_dj": {
        "hair": NIGHT[2], "hair_hi": NIGHT[3], "hair_sh": NIGHT[1],
        "skin": SICK[2], "skin_hi": SICK[3], "skin_sh": SICK[1],
        "jacket": CYAN[0], "jacket_hi": CYAN[1], "shirt": NIGHT[1],
        "pants": NIGHT[2], "pants_sh": NIGHT[1], "boots": BLACK, "accent": CYAN[2],
        "hunch": 1, "eye": CYAN[3], "headphones": True,
    },
}

# Walk pose table: (front_leg_reach, back_leg_reach, bob, arm_swing)
# reach in px toward stride direction; bob lifts the body on passing poses.
POSES = [
    (3, -3, 0, 2),   # contact
    (2, -2, 0, 1),   # recoil
    (0, 0, 1, 0),    # passing (body up)
    (-3, 3, 0, -2),  # contact, other leg
    (-2, 2, 0, -1),  # recoil
    (0, 0, 1, 0),    # passing
]
STAND_POSE = (0, 0, 0, 0)  # column 6: neutral standing (idle)


def _rect(s, x, y, w, h, color):
    s.fill((*color, 255), (x, y, w, h))


def _px(s, x, y, color):
    if 0 <= x < FRAME_W and 0 <= y < FRAME_H:
        s.set_at((x, y), (*color, 255))


def _outline(s):
    """1px black outline: any transparent pixel 4-adjacent to the body."""
    mask = [[s.get_at((x, y))[3] > 0 for y in range(FRAME_H)] for x in range(FRAME_W)]
    for x in range(FRAME_W):
        for y in range(FRAME_H):
            if mask[x][y]:
                continue
            near = ((x > 0 and mask[x - 1][y]) or (x < FRAME_W - 1 and mask[x + 1][y]) or
                    (y > 0 and mask[x][y - 1]) or (y < FRAME_H - 1 and mask[x][y + 1]))
            if near:
                s.set_at((x, y), (*BLACK, 255))


def _head(s, st, facing, h):
    """Hair + face. h = hunch offset (whole head sits lower)."""
    if facing == "down":
        _rect(s, 3, 1 + h, 10, 4, st["hair"])
        _rect(s, 2, 2 + h, 1, 4, st["hair"]); _rect(s, 13, 2 + h, 1, 4, st["hair"])
        _rect(s, 4, 1 + h, 3, 1, st["hair_hi"])
        _rect(s, 5, 5 + h, 6, 5, st["skin"])
        _rect(s, 5, 5 + h, 6, 1, st["hair_sh"])          # brow shadow under hair
        if st.get("shades"):
            _rect(s, 5, 7 + h, 6, 1, BLACK)
        else:
            _px(s, 6, 7 + h, st["eye"]); _px(s, 9, 7 + h, st["eye"])
        _px(s, 5, 9 + h, st["skin_sh"]); _px(s, 10, 9 + h, st["skin_sh"])
        _rect(s, 7, 10 + h, 2, 1, st["skin_sh"])          # neck
    elif facing == "up":
        _rect(s, 3, 1 + h, 10, 8, st["hair"])
        _rect(s, 2, 2 + h, 1, 4, st["hair"]); _rect(s, 13, 2 + h, 1, 4, st["hair"])
        _rect(s, 4, 1 + h, 4, 1, st["hair_hi"])
        _rect(s, 3, 8 + h, 10, 1, st["hair_sh"])
        _rect(s, 7, 9 + h, 2, 2, st["skin_sh"])           # neck
    else:  # left profile
        _rect(s, 3, 1 + h, 10, 5, st["hair"])             # big 80s volume
        _rect(s, 11, 5 + h, 3, 5, st["hair"])             # swept back and down
        _rect(s, 4, 1 + h, 4, 1, st["hair_hi"])
        _rect(s, 11, 9 + h, 3, 1, st["hair_sh"])
        _rect(s, 4, 5 + h, 7, 5, st["skin"])
        _rect(s, 4, 5 + h, 7, 1, st["hair_sh"])
        if st.get("shades"):
            _rect(s, 4, 7 + h, 4, 1, BLACK)
        else:
            _px(s, 5, 7 + h, st["eye"])
        _px(s, 3, 8 + h, st["skin"])                      # nose
        _px(s, 4, 9 + h, st["skin_sh"])                   # jaw
        _rect(s, 7, 10 + h, 2, 1, st["skin_sh"])          # neck
    if st.get("headphones"):
        y0 = 0 + h
        _rect(s, 4, y0, 8, 1, st["accent"])               # band
        if facing != "up":
            _rect(s, 2, 5 + h, 2, 3, st["accent"])        # ear cup(s)
        if facing == "down":
            _rect(s, 12, 5 + h, 2, 3, st["accent"])


def _torso(s, st, facing, h, arm_swing, broad=False):
    grow = 1 if broad else 0
    x0, w = 4 - grow, 8 + grow * 2
    _rect(s, x0, 11 + h, w, 8, st["jacket"])
    _rect(s, x0, 11 + h, w, 1, st["jacket_hi"])           # shoulder light
    if facing == "down":
        _rect(s, 7, 12 + h, 2, 3, st["shirt"])            # open jacket / shirt
        _px(s, 8, 15 + h, st["accent"])                   # pin/logo
    elif facing == "up":
        _rect(s, 7, 12 + h, 2, 6, st["jacket_hi"])        # back seam
    if facing in ("down", "up"):
        # Arms at sides, counter-swinging vertically.
        left_dy = max(-1, min(1, arm_swing))
        right_dy = -left_dy
        _rect(s, x0 - 1, 12 + h + left_dy, 1, 6, st["jacket"])
        _rect(s, x0 + w, 12 + h + right_dy, 1, 6, st["jacket"])
        _px(s, x0 - 1, 18 + h + left_dy, st["skin"])      # hands
        _px(s, x0 + w, 18 + h + right_dy, st["skin"])
    else:
        if st["hunch"]:
            # Shamble: both arms out in front, low.
            _rect(s, 1, 13 + h, 4, 2, st["jacket"])
            _rect(s, 0, 13 + h, 1, 2, st["skin"])         # hand
        else:
            # Near arm swings with the stride.
            ax = 6 + max(-2, min(2, arm_swing))
            _rect(s, ax, 12 + h, 2, 5, st["jacket"])
            _px(s, ax, 17 + h, st["skin"])


def _legs(s, st, facing, front, back, bob):
    """Legs + boots. front/back = stride reach in px (side view) or
    foot-lift alternation (front/back views)."""
    pants_sh = st.get("pants_sh", st["pants"])
    hip_y = 19 - bob
    _rect(s, 5, hip_y, 6, 2, st["pants"])
    if facing in ("down", "up"):
        # Alternate feet: the stepping leg lifts 2px, its boot rises with it.
        lift_l = 2 if front > 0 else 0
        lift_r = 2 if back > 0 else 0
        _rect(s, 5, hip_y + 2, 2, 8 - lift_l, st["pants"])
        _rect(s, 9, hip_y + 2, 2, 8 - lift_r, pants_sh)
        _rect(s, 4, 29 - lift_l, 3, 2, st["boots"])
        _rect(s, 9, 29 - lift_r, 3, 2, st["boots"])
    else:
        # Side view: legs scissor around the hip; the far leg is drawn
        # first in shadow tone so the near leg reads in front of it.
        fx = 7 + front
        bx = 7 + back
        _rect(s, bx, hip_y + 2, 2, 8, pants_sh)
        _rect(s, bx, 29, 3, 2, st["boots"])
        _rect(s, fx, hip_y + 2, 2, 8, st["pants"])
        _rect(s, fx - 1, 29, 3, 2, st["boots"])


def build_frame(style: Dict, facing: str, pose: Tuple[int, int, int, int]) -> pygame.Surface:
    front, back, bob, arm_swing = pose
    s = pygame.Surface((FRAME_W, FRAME_H), pygame.SRCALPHA)
    h = style["hunch"] - bob
    if style["hunch"]:
        # Shamble reads slower: halve the stride.
        front, back = front // 2 + (1 if front > 0 else -1 if front < 0 else 0), back // 2
    _legs(s, style, facing, front, back, bob)
    _torso(s, style, facing, h, arm_swing, style.get("broad", False))
    _head(s, style, facing, h)
    _outline(s)
    return s


def build_character(name: str, style: Dict, assets_root: str, fps: float) -> None:
    frames: Dict[str, list] = {}
    for facing in ["down", "up", "left"]:
        frames[facing] = [build_frame(style, facing, pose) for pose in POSES]
        frames[facing].append(build_frame(style, facing, STAND_POSE))
    frames["right"] = [pygame.transform.flip(f, True, False) for f in frames["left"]]

    sheet = pygame.Surface((FRAME_W * TOTAL_FRAMES, FRAME_H * len(DIRECTIONS)), pygame.SRCALPHA)
    for row, facing in enumerate(DIRECTIONS):
        for col, frame in enumerate(frames[facing]):
            sheet.blit(frame, (col * FRAME_W, row * FRAME_H))
    assert_surface_palette(sheet, context=f"{name} sheet")

    out_dir = os.path.join(assets_root, "characters", name)
    os.makedirs(out_dir, exist_ok=True)
    pygame.image.save(sheet, os.path.join(out_dir, "sheet.png"))
    meta = {
        "frame_size": [FRAME_W, FRAME_H],
        "anchor": [FRAME_W // 2, FRAME_H - 1],
        "directions": DIRECTIONS,
        "animations": {
            "walk": {"frames": list(range(WALK_FRAMES)), "fps": fps},
            "idle": {"frames": [6], "fps": 1.0},
        },
        "perspective_steps": [0.625, 0.75, 0.875, 1.0, 1.125, 1.25],
    }
    with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as handle:
        json.dump(meta, handle, indent=2)
    print(f"authored {name}")


def main() -> None:
    pygame.init()
    assets_root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO_ROOT, "assets")
    build_character("hero", HERO_STYLE, assets_root, fps=9.0)
    for name, style in ZOMBIE_STYLES.items():
        build_character(name, style, assets_root, fps=5.0)


if __name__ == "__main__":
    main()
