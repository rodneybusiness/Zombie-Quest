from __future__ import annotations

import os
import sys

from zombie_quest.engine import GameEngine


def main() -> None:
    base_path = os.path.dirname(os.path.abspath(__file__))
    engine = GameEngine(base_path)
    if "--headless" in sys.argv:
        # Run a minimal update loop for automated validation without opening the window.
        for _ in range(5):
            engine.update(1 / 60)
        return
    engine.run()


if __name__ == "__main__":  # pragma: no cover - direct execution guard
    main()
