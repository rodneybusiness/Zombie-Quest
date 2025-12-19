# Zombie Quest: Neon Dead - Minneapolis '82

![Zombie Quest Banner](https://via.placeholder.com/800x200/1E0A3C/FF69B4?text=Zombie+Quest:+Neon+Dead)

A retro point-and-click adventure game set in 1982 Minneapolis during a zombie apocalypse on the Sunset Strip. Navigate the legendary music venues of Hennepin Avenue, solve puzzles, and use the power of music to pacify the undead while uncovering the truth behind the outbreak.

## Features

- **Period-Authentic Setting**: Explore First Avenue, Let It Be Records, and KJRR college radio station
- **Musical Zombie Combat**: Use guitar picks, demo tapes, setlists, and vinyl records to affect zombie behavior
- **Branching Dialogue**: Complex conversation trees with emotional NPC interactions
- **Multiple Endings**: Your backstory and choices determine how the story concludes
- **Point-and-Click & WASD**: Full keyboard and mouse support
- **Procedural Audio**: Synthesized sound effects and dynamic music layers
- **Retro Aesthetic**: CRT scanlines, neon lighting, and 80s visual effects
- **Save System**: Save and load your progress
- **Accessibility Features**: Keyboard navigation, visual feedback, and customizable controls

## Installation

### Prerequisites

- Python 3.7 or higher
- Pygame 2.0+

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/zombie-quest.git
   cd zombie-quest
   ```

2. **Using the run script** (Recommended):
   ```bash
   ./run_game.sh
   ```
   This automatically creates a virtual environment and installs dependencies.

3. **Manual installation**:
   ```bash
   pip install pygame
   python main.py
   ```

### System Requirements

- **OS**: Windows, macOS, Linux
- **Python**: 3.7+
- **RAM**: 512MB minimum
- **Display**: 320x276 minimum resolution (scales to modern displays)
- **Audio**: Optional but recommended for full experience

## How to Play

### Controls

#### Movement
- **Mouse Click**: Click anywhere to walk to that location
- **WASD / Arrow Keys**: Direct character movement
- **Space/Enter**: Interact with nearest hotspot

#### Verbs (Point-and-Click Actions)
- **1 Key**: Walk mode
- **2 Key**: Look mode
- **3 Key**: Use mode
- **4 Key**: Talk mode
- **Tab**: Cycle through verbs
- **Right Click**: Next verb

#### Inventory
- **I Key**: Open/close inventory
- **Arrow Keys**: Navigate items
- **Enter/Space**: Select item
- **Mouse Click**: Click items to select

#### System
- **P Key / ESC**: Pause menu
- **ESC**: Close windows/Back

### Basic Gameplay

1. **Explore** the rooms by clicking on locations or using keyboard movement
2. **Examine** objects with the Look verb to gather information
3. **Talk** to NPCs to get clues and items
4. **Collect items** by using the Use verb on interactive hotspots
5. **Solve puzzles** by combining items or using them in the right places
6. **Use musical items** near zombies to pacify them:
   - **Guitar Pick**: Raw rock energy
   - **Demo Tape**: New wave basement sound
   - **Setlist**: Remembered melodies
   - **Vinyl Record**: The Neon Dead's fury

### Zombie Mechanics

Zombies have different types and behaviors:
- **Scene Kids**: Love new wave and electronic music
- **Bouncers**: Respond to heavy guitar and punk
- **Rockers**: Energized by guitar riffs
- **DJs**: Entranced by electronic beats

Musical items create zones of effect that can:
- **Entrance** zombies (freeze them in place)
- **Make them dance** (harmless swaying)
- **Trigger memories** (brief lucidity)

## Game Objective

Navigate the zombie-infested Minneapolis music scene to uncover the truth behind the outbreak. Your backstory (Sellout, Purist, or Survivor) affects NPC reactions and available dialogue choices. Reach Maya, your former bandmate, and make crucial decisions that determine one of multiple endings.

## Screenshots

<!-- Placeholder for screenshots -->
*Screenshots coming soon*

### Main Game Screen
![Main Screen](https://via.placeholder.com/640x552/1E0A3C/00FFFF?text=Main+Game+Screen)

### Inventory System
![Inventory](https://via.placeholder.com/640x552/1E0A3C/FFD700?text=Inventory+System)

### Dialogue System
![Dialogue](https://via.placeholder.com/640x552/1E0A3C/FF69B4?text=Dialogue+Tree)

## Development Status

**Current Version**: 1.0.0 (Ship-Ready)

All core features implemented and tested. The game is fully playable from start to finish with multiple endings.

## Documentation

- **[Gameplay Guide](GAMEPLAY_GUIDE.md)**: Walkthrough, puzzle solutions, and tips
- **[Developer Guide](DEVELOPER_GUIDE.md)**: Architecture and how to extend the game
- **[API Reference](API_REFERENCE.md)**: Technical documentation for all classes and methods
- **[Changelog](CHANGELOG.md)**: Version history and feature updates
- **[Credits](CREDITS.md)**: Acknowledgments and inspiration

## Technical Architecture

```
main.py → GameEngine.run()
              ↓
    ┌─────────┴─────────┐
    │   Game Loop       │
    │  update() → draw()│
    └─────────┬─────────┘
              ↓
    rooms ←→ characters ←→ pathfinding
       ↓           ↓
      UI       dialogue
       ↓           ↓
    audio     effects
```

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for detailed architecture information.

## Testing

### Headless Mode

For CI/CD validation:

```bash
python main.py --headless        # Runs 120 frames with validation
python main.py --headless -v     # Verbose output
```

### Manual Testing

```bash
./run_game.sh
```

Play through the game to test all features. See testing procedures in [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md).

## Project Structure

```
zombie-quest/
├── main.py                    # Entry point
├── run_game.sh               # Launch script
├── game_data.json            # Room, item, and NPC definitions
├── zombie_quest/             # Core game modules
│   ├── __init__.py
│   ├── engine.py             # Main game engine
│   ├── rooms.py              # Room system
│   ├── characters.py         # Player and zombie AI
│   ├── ui.py                 # UI components
│   ├── audio.py              # Audio synthesis
│   ├── dialogue.py           # Dialogue trees
│   ├── effects.py            # Visual effects
│   ├── pathfinding.py        # A* pathfinding
│   ├── data_loader.py        # JSON parsing
│   ├── config.py             # Game configuration
│   └── [20+ additional modules]
├── README.md                 # This file
├── GAMEPLAY_GUIDE.md         # Player guide
├── DEVELOPER_GUIDE.md        # Developer documentation
├── API_REFERENCE.md          # API documentation
├── CHANGELOG.md              # Version history
└── CREDITS.md                # Acknowledgments
```

## Contributing

This is a complete, finished game project created as a demonstration. However, if you'd like to:

1. **Report bugs**: Open an issue with reproduction steps
2. **Suggest features**: Create a feature request issue
3. **Submit improvements**: Fork and create a pull request

## License

[Specify your license here - e.g., MIT, GPL, etc.]

## Credits

Created by [Your Name/Team]

Inspired by:
- Classic LucasArts adventure games (Maniac Mansion, Day of the Tentacle)
- Minneapolis music scene of the early 1980s
- First Avenue & 7th St Entry venue history

See [CREDITS.md](CREDITS.md) for full acknowledgments.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/zombie-quest/issues)
- **Documentation**: See the docs/ directory
- **Email**: [your-email@example.com]

## Acknowledgments

Special thanks to:
- Minneapolis music community
- Pygame community
- Classic adventure game developers who paved the way

---

**Rock on and survive the neon apocalypse!** 🎸🧟💜
