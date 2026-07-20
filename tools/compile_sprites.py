#!/usr/bin/env python
"""Bootstrap assets/characters/ from the current procedural sprites.

Renders each character's animation set at native 1x (16x32), quantizes it
through the ZQ-32 palette, and writes sheet.png (rows = directions,
columns = frames) plus meta.json in the pipeline's canonical format.

This exists so the asset loader path can be exercised end-to-end before
hand-drawn art lands; authored art then replaces these files one
character at a time.

Usage: python tools/compile_sprites.py [assets_root]  (default: assets)
"""
from __future__ import annotations

import json
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import pygame  # noqa: E402

from zombie_quest import palette  # noqa: E402
from zombie_quest.sprites import create_hero_animations, create_zombie_animations  # noqa: E402

DIRECTIONS = ["down", "up", "left", "right"]
ZOMBIE_TYPES = ["scene", "bouncer", "rocker", "dj"]
PERSPECTIVE_STEPS = [0.625, 0.75, 0.875, 1.0, 1.125, 1.25]


def compile_character(name: str, animations: dict, assets_root: str) -> None:
    frames_per_direction = max(len(frames) for frames in animations.values())
    frame_w, frame_h = animations[DIRECTIONS[0]][0].get_size()

    sheet = pygame.Surface((frame_w * frames_per_direction,
                            frame_h * len(DIRECTIONS)), pygame.SRCALPHA)
    for row, direction in enumerate(DIRECTIONS):
        for col, frame in enumerate(animations[direction]):
            sheet.blit(palette.quantize_surface(frame), (col * frame_w, row * frame_h))

    char_dir = os.path.join(assets_root, "characters", name)
    os.makedirs(char_dir, exist_ok=True)
    pygame.image.save(sheet, os.path.join(char_dir, "sheet.png"))

    meta = {
        "frame_size": [frame_w, frame_h],
        "anchor": [frame_w // 2, frame_h - 1],
        "directions": DIRECTIONS,
        "animations": {
            "walk": {"frames": list(range(frames_per_direction)), "fps": 1 / 0.15},
        },
        "perspective_steps": PERSPECTIVE_STEPS,
    }
    with open(os.path.join(char_dir, "meta.json"), "w", encoding="utf-8") as handle:
        json.dump(meta, handle, indent=2)
    print(f"compiled {name}: {frames_per_direction} frames x {len(DIRECTIONS)} dirs "
          f"at {frame_w}x{frame_h}")


def main() -> None:
    pygame.init()
    pygame.display.set_mode((1, 1))
    assets_root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO_ROOT, "assets")

    compile_character("hero", create_hero_animations(scale=1.0), assets_root)
    for zombie_type in ZOMBIE_TYPES:
        compile_character(f"zombie_{zombie_type}",
                          create_zombie_animations(zombie_type=zombie_type, scale=1.0),
                          assets_root)

    palette_dir = os.path.join(assets_root, "palette")
    os.makedirs(palette_dir, exist_ok=True)
    palette.write_gpl(os.path.join(palette_dir, "zq32.gpl"))
    print("wrote assets/palette/zq32.gpl")


if __name__ == "__main__":
    main()
