#!/usr/bin/env python
"""Regenerate the golden reference frames in tests/golden/.

Run this after an INTENTIONAL visual change, review the diff (git shows
the changed PNGs; CI artifacts show expected/actual/diff), and commit
the new goldens together with the change that caused them.

Usage: python tools/update_goldens.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "tests"))

import pygame  # noqa: E402

from golden_utils import GOLDEN_DIR, render_room_frame  # noqa: E402
from zombie_quest.engine import GameEngine  # noqa: E402


def main() -> None:
    os.makedirs(GOLDEN_DIR, exist_ok=True)
    engine = GameEngine(REPO_ROOT)
    for room_id in engine.rooms:
        frame = render_room_frame(engine, room_id)
        pygame.image.save(frame, os.path.join(GOLDEN_DIR, f"{room_id}.png"))
        print(f"golden updated: {room_id}")


if __name__ == "__main__":
    main()
