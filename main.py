"""Entry point for the SCI-inspired Zombie Quest demo."""
from __future__ import annotations

import os

import pygame

from engine import Game


def main() -> None:
    if "SDL_VIDEODRIVER" not in os.environ:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    if "SDL_AUDIODRIVER" not in os.environ:
        os.environ["SDL_AUDIODRIVER"] = "dummy"
    pygame.init()
    data_path = os.path.join(os.path.dirname(__file__), "game_data.json")
    game = Game(data_path)
    game.run()


if __name__ == "__main__":
    main()
