# Zombie Quest

1982 LA Sunset Strip adventure game. Solve puzzles, survive zombies, explore multiple endings. Uses procedurally generated sprites and audio—no external assets.

## Commands

```bash
# Game
./run_game.sh                    # Launch (auto-installs pygame)
python main.py                   # Direct launch
python main.py --headless        # CI validation (120 frames)
python main.py --headless --verbose  # Verbose validation

# Tests (300+ tests)
pytest tests/                    # Run all tests
pytest tests/ -x                 # Stop on first failure
pytest -m integration            # Integration tests only
pytest --cov=zombie_quest tests/ # With coverage report
```

## Stack

Python 3.x + Pygame. Single dependency: `pygame>=2.0.0`

## Architecture

```
main.py → GameEngine.run() @ 60 FPS
              ↓
    ┌─────────────────────────────────────┐
    │  State Machine (8 states)           │
    │  MENU → PLAYING ↔ PAUSED           │
    │         ↓ ↓ ↓                       │
    │  DIALOGUE / INVENTORY / TRANSITION  │
    │         ↓                           │
    │  GAME_OVER → CREDITS                │
    └─────────────────────────────────────┘
              ↓
    ┌─────────────────────────────────────┐
    │  Per-Frame: handle_events()         │
    │           → update(dt)              │
    │           → draw()                  │
    └─────────────────────────────────────┘
```

## Module Map

```
zombie_quest/
├── CORE
│   ├── engine.py           # GameEngine - orchestrates everything
│   ├── config.py           # Frozen dataclasses (speeds, colors, timings)
│   ├── rooms.py            # Room, Hotspot classes
│   ├── characters.py       # Hero, Zombie, spawner
│   ├── characters_enhanced.py  # Enhanced movement (Hero alias)
│   ├── pathfinding.py      # A* grid navigation
│   ├── data_loader.py      # JSON parsing
│   └── resources.py        # Asset loading utilities
│
├── NARRATIVE
│   ├── dialogue.py         # DialogueTree, nodes, choices, effects
│   ├── memory.py           # Progressive hotspot text, backstory
│   ├── tutorial.py         # Contextual hints, highlights
│   └── save_system.py      # Multi-slot save/load
│
├── INVENTORY
│   ├── inventory_enhanced.py   # Grid UI, drag-drop, tooltips
│   └── item_combinations.py    # 10 crafting recipes
│
├── VISUALS
│   ├── sprites.py          # Procedural sprite generation
│   ├── sprite_cache.py     # LRU cache for sprites
│   ├── sprite_config.py    # Character definitions
│   ├── backgrounds.py      # Procedural room backgrounds
│   ├── parallax_backgrounds.py # Layered scrolling
│   ├── neon_lighting.py    # Additive glow lights
│   ├── shadow_renderer.py  # Drop shadows
│   ├── crt_shader.py       # Scanlines, barrel distortion, bloom
│   └── ui.py               # VerbBar, MessageBox, menus
│
├── EFFECTS
│   ├── effects.py          # Particles, transitions, screen shake
│   ├── juice.py            # Hitstop, knockback, infection visuals
│   ├── feedback_juice.py   # Camera trauma, squash/stretch
│   ├── idle_animation.py   # Idle poses
│   └── eight_direction.py  # 8-dir sprite support
│
├── AUDIO
│   ├── audio.py            # Procedural synth, music layers, SFX
│   ├── diegetic_audio.py   # In-world music sources (affect zombies)
│   └── movement.py         # Movement sound triggers
│
├── UX
│   ├── accessibility.py    # Colorblind, font size, screen shake toggle
│   ├── hotspot_highlight.py # Interactive object highlighting
│   └── radial_menu.py      # Radial verb selection
│
└── DEMO
    └── visual_demo.py      # Visual system showcase
```

## Key Data Files

```
game_data.json    # Rooms, hotspots, items, zombies (schema below)
pytest.ini        # Test configuration
requirements.txt  # pygame>=2.0.0
```

### game_data.json Schema

```json
{
  "hero": { "start_room": "room_id", "position": [x, y] },
  "items": [{ "name": "...", "description": "...", "icon_color": [r,g,b] }],
  "starting_inventory": [],
  "rooms": [{
    "id": "room_id",
    "name": "Display Name",
    "entry_message": "Shown on enter",
    "default_entry": [x, y],
    "size": [320, 200],
    "background": { "gradient": [...], "shapes": [...] },
    "walkable_zones": [{ "shape": "polygon", "points": [...] }],
    "hotspots": [{
      "name": "Door",
      "rect": [x, y, w, h],
      "walk_position": [x, y],
      "verbs": { "look": "msg", "use": "msg" },
      "target_room": "other_room",      // optional: room transition
      "required_item": "Key",           // optional: item gate
      "give_item": "Reward",            // optional: item reward
      "talk_target": "npc_id"           // optional: dialogue trigger
    }],
    "zombies": [{ "position": [x, y], "type": "scene|bouncer|rocker|dj" }]
  }]
}
```

## Core Patterns

### Verb-Based Interactions
All hotspot actions use verbs: `WALK`, `LOOK`, `TALK`, `USE`. Hotspots define responses per verb with outcomes: `default`, `success`, `missing`.

### Deferred Interactions
Player clicks hotspot → hero walks there → `pending_interaction` stored → executes when `hero.has_arrived()`.

### Zombie State Machines
```
MusicState: HOSTILE → ENTRANCED → DANCING → REMEMBERING
Alertness:  DORMANT → WANDERING → SUSPICIOUS → HUNTING → FRENZIED
```
Music items create diegetic audio sources that affect nearby zombie behavior.

### Infection System
- 0-100% scale, visual stages at 40%/70%/100%
- Affects screen visuals (veins, vignette, distortion)
- 100% triggers transformation ending

### Configuration-Driven
All magic numbers in `config.py` frozen dataclasses:
- `DisplayConfig`: Window dimensions
- `GameplayConfig`: Speeds, detection radii, infection rates
- `AnimationConfig`: Frame timings
- `AudioConfig`: Volume levels
- `ColorPalette`: 80s neon theme colors

## Sharp Edges

1. **Procedural Everything** - Sprites and audio are generated in code, not loaded. Changes require understanding generation algorithms in `sprites.py` and `audio.py`.

2. **String-Based Flags** - `game_flags` dict uses string keys. Typos won't error—flags just won't match. Check existing flags in `dialogue.py` and `engine.py`.

3. **Enhanced Character Alias** - `characters.py` imports `EnhancedHero` as `Hero`. The enhanced version lives in `characters_enhanced.py`.

4. **Legacy Monoliths** - `zombie_quest.py` and `zombie_quest_fixed.py` are deprecated. Use `zombie_quest/` module.

5. **No JSON Validation** - `game_data.json` is trusted. Malformed data may cause cryptic errors.

6. **Headless Limitations** - `--headless` mode validates game logic but not rendering. Uses SDL dummy drivers.

7. **Test Mocking** - Tests heavily mock pygame. Some integration tests run 200+ frames but don't test actual rendering.

## Testing

```bash
# Markers
pytest -m integration    # Multi-system flows
pytest -m slow          # Long-running tests
pytest -m headless      # CI-compatible tests

# Coverage
pytest --cov=zombie_quest --cov-report=html tests/
# Opens htmlcov/index.html
```

**Fixtures** (`tests/conftest.py`):
- `mock_display`, `mock_audio` - Pygame mocking
- `mock_room`, `mock_hero`, `test_zombie` - Game objects
- `minimal_room_data`, `game_data_two_rooms` - Test data

## Quick Reference

| Task | Location |
|------|----------|
| Add new room | `game_data.json` → rooms array |
| Add new item | `game_data.json` → items array |
| Add dialogue | `dialogue.py` → create_*_dialogue() |
| Add NPC | `sprites.py` → character generation |
| Add puzzle | Hotspot with `required_item` + `give_item` |
| Add zombie type | `characters.py` → ZombieType enum |
| Tune gameplay | `config.py` → GameplayConfig |
| Add ending | `engine.py` → endings_data checks |
