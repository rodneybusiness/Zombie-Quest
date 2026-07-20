#!/usr/bin/env python
"""Capture the game's actual rendered output for visual review.

Dumps, per room: the full composed frame (everything the player sees) and
the raw 320x200 room surface scaled 3x (art without UI/post-fx). Also
writes a hero walk-cycle sheet at 5x and the ZQ-32 swatch sheet.

Usage: python tools/capture.py [out_dir]   (default: build/captures)
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import pygame  # noqa: E402

from zombie_quest import palette  # noqa: E402
from zombie_quest.engine import GameEngine  # noqa: E402


def capture_rooms(engine: GameEngine, out_dir: str) -> None:
    for room_id, room in engine.rooms.items():
        engine.change_room(room_id, announce=False)
        for _ in range(5):
            engine.update(1 / 60)
        engine.draw()
        pygame.image.save(engine.screen, os.path.join(out_dir, f"frame_{room_id}.png"))

        raw = pygame.Surface(room.size)
        room.draw(raw, engine.hero)
        scaled = pygame.transform.scale(raw, (room.size[0] * 3, room.size[1] * 3))
        pygame.image.save(scaled, os.path.join(out_dir, f"room_{room_id}.png"))
    print(f"Captured {len(engine.rooms)} rooms (frame_* composed, room_* raw 3x)")


def capture_hero_sheet(engine: GameEngine, out_dir: str, scale: int = 5) -> None:
    animations = engine.hero.animations
    directions = list(animations.keys())
    frames_per_direction = max(len(frames) for frames in animations.values())
    frame_w, frame_h = animations[directions[0]][0].get_size()
    pad = 2
    sheet = pygame.Surface(((frame_w + pad) * frames_per_direction * scale,
                            (frame_h + pad) * len(directions) * scale))
    sheet.fill((40, 40, 48))
    for row, direction in enumerate(directions):
        for col, frame in enumerate(animations[direction]):
            big = pygame.transform.scale(frame, (frame_w * scale, frame_h * scale))
            sheet.blit(big, (col * (frame_w + pad) * scale, row * (frame_h + pad) * scale))
    pygame.image.save(sheet, os.path.join(out_dir, "hero_walk_sheet.png"))
    print(f"Captured hero sheet: {frames_per_direction} frames x {len(directions)} dirs "
          f"at {frame_w}x{frame_h}")


def main() -> None:
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO_ROOT, "build", "captures")
    os.makedirs(out_dir, exist_ok=True)
    engine = GameEngine(REPO_ROOT)
    capture_rooms(engine, out_dir)
    capture_hero_sheet(engine, out_dir)
    pygame.image.save(palette.swatch_sheet(cell=24), os.path.join(out_dir, "zq32_swatches.png"))
    print(f"All captures in {out_dir}")


if __name__ == "__main__":
    main()
