#!/usr/bin/env python
"""Generate review contact sheets for rooms and characters.

Per room, a 2x2 grid at 2x: raw background | background + priority tint
(walk-behind bands in magenta) | background + walkable tint (cyan) |
composite with the hero drawn at three depths (near/mid/far) to judge
perspective scaling and walk-behind behavior.

Per character (hero + one zombie of each type in the data), every
direction x frame at 4x.

Usage: python tools/contact_sheet.py [out_dir]  (default: build/contact_sheets)
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import pygame  # noqa: E402

from zombie_quest.engine import GameEngine  # noqa: E402

PRIORITY_TINT = (255, 20, 147)
WALKABLE_TINT = (60, 190, 208)


def _tinted(base: pygame.Surface, mask: pygame.Surface | None,
            tint: tuple) -> pygame.Surface:
    result = base.copy()
    if mask is None:
        return result
    overlay = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    bitmask = pygame.mask.from_threshold(mask, (255, 255, 255), (60, 60, 60))
    tint_surface = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    tint_surface.fill((*tint, 140))
    overlay = bitmask.to_surface(surface=overlay, setsurface=tint_surface,
                                 unsetcolor=(0, 0, 0, 0))
    result.blit(overlay, (0, 0))
    return result


def room_sheets(engine: GameEngine, out_dir: str) -> None:
    for room_id, room in engine.rooms.items():
        engine.change_room(room_id, announce=False)
        width, height = room.size
        raw = pygame.Surface(room.size)
        raw.blit(room.background, (0, 0))

        composite = pygame.Surface(room.size)
        composite.blit(room.background, (0, 0))
        # Hero at three depths: far (top of walkable band), mid, near.
        for y in (150, 172, 196):
            engine.hero.position.update((width // 2, y))
            room.draw(composite, engine.hero)

        panels = [
            raw,
            _tinted(raw, room.priority_mask, PRIORITY_TINT),
            _tinted(raw, room.walkable_mask, WALKABLE_TINT),
            composite,
        ]
        scale = 2
        pad = 4
        sheet = pygame.Surface((width * 2 * scale + pad, height * 2 * scale + pad))
        sheet.fill((24, 24, 30))
        for index, panel in enumerate(panels):
            big = pygame.transform.scale(panel, (width * scale, height * scale))
            x = (index % 2) * (width * scale + pad)
            y = (index // 2) * (height * scale + pad)
            sheet.blit(big, (x, y))
        pygame.image.save(sheet, os.path.join(out_dir, f"room_{room_id}.png"))
    print(f"Room sheets: {len(engine.rooms)}")


def character_sheets(engine: GameEngine, out_dir: str, scale: int = 4) -> None:
    subjects = {"hero": engine.hero.animations}
    for room in engine.rooms.values():
        for zombie in room.zombies:
            key = f"zombie_{zombie.zombie_type}"
            if key not in subjects:
                subjects[key] = zombie.animations
    for name, animations in subjects.items():
        directions = list(animations.keys())
        frames_per_direction = max(len(f) for f in animations.values())
        frame_w, frame_h = animations[directions[0]][0].get_size()
        pad = 2
        sheet = pygame.Surface(((frame_w + pad) * frames_per_direction * scale,
                                (frame_h + pad) * len(directions) * scale))
        sheet.fill((40, 40, 48))
        for row, direction in enumerate(directions):
            for col, frame in enumerate(animations[direction]):
                big = pygame.transform.scale(frame, (frame_w * scale, frame_h * scale))
                sheet.blit(big, (col * (frame_w + pad) * scale, row * (frame_h + pad) * scale))
        pygame.image.save(sheet, os.path.join(out_dir, f"char_{name}.png"))
    print(f"Character sheets: {len(subjects)}")


def main() -> None:
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO_ROOT, "build", "contact_sheets")
    os.makedirs(out_dir, exist_ok=True)
    engine = GameEngine(REPO_ROOT)
    room_sheets(engine, out_dir)
    character_sheets(engine, out_dir)
    print(f"All contact sheets in {out_dir}")


if __name__ == "__main__":
    main()
