# Zombie Quest

1982 rock-scene adventure game. Navigate LA's Sunset Strip, solve puzzles, survive zombie encounters with period-authentic music and culture references.

## Commands

```bash
./run_game.sh              # Launch game (activates venv)
python main.py             # Direct launch (needs pygame)
python main.py --headless  # CI validation (no window)
```

## Stack

Python 3.x + Pygame. No build step, no tests yet.

## Structure

```
zombie_quest/        # Core modules
├── engine.py        # GameEngine - main loop, state machine
├── rooms.py         # Room definitions, transitions
├── characters.py    # Player, NPCs, zombies
├── pathfinding.py   # A* navigation
├── resources.py     # Asset loading
├── ui.py            # Rendering, HUD
└── data_loader.py   # JSON parsing
game_data.json       # Room data, item definitions
main.py              # Entry point
```

## Architecture

```
main.py → GameEngine.run()
              ↓
    ┌─────────┴─────────┐
    │   Game Loop       │
    │  update() → draw()│
    └─────────┬─────────┘
              ↓
    rooms ←→ characters ←→ pathfinding
```

## Sharp Edges

1. **No tests** - Game logic is untested; add pytest if modifying core mechanics
2. **Pygame dependency** - `pip install pygame` or use `run_game.sh`
3. **Headless mode** - Use `--headless` for CI; runs 5 frames then exits
4. **Two main files** - `zombie_quest.py` and `zombie_quest_fixed.py` are legacy monoliths; use `zombie_quest/` module
