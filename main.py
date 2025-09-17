"""Entry point for the Zombie Quest SCI-style adventure."""

from __future__ import annotations

from pathlib import Path

from engine import run_game


if __name__ == "__main__":
    data_path = Path(__file__).resolve().parent / "game_data.json"
    run_game(str(data_path))
